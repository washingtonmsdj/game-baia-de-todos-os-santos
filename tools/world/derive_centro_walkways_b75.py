"""Recortar passeios com largura OSM na superfície B74, sem elevar/rebaixar o DEM."""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'artifacts/geospatial-python'))
import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from shapely.strtree import STRtree


def polygons(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type == 'Polygon':
        yield geometry
    else:
        for part in getattr(geometry, 'geoms', []):
            yield from polygons(part)


def surface_checks(old_vertices, old_faces, vertices, faces, parents):
    old = old_vertices[old_faces[parents]].astype(float)
    new = vertices[faces].astype(float)
    a=old[:,0];b=old[:,1]-a;d=old[:,2]-a
    determinant=b[:,0]*d[:,1]-b[:,1]*d[:,0]
    offset=new[:,:,:2]-a[:,None,:2]
    u=(offset[:,:,0]*d[:,None,1]-offset[:,:,1]*d[:,None,0])/determinant[:,None]
    v=(b[:,None,0]*offset[:,:,1]-b[:,None,1]*offset[:,:,0])/determinant[:,None]
    expected=a[:,None,2]+u*b[:,None,2]+v*d[:,None,2]
    max_z=float(np.max(np.abs(expected-new[:,:,2])))
    cross=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0])
    old_triangles=old_vertices[old_faces].astype(float)
    old_area=np.cross(old_triangles[:,1]-old_triangles[:,0],old_triangles[:,2]-old_triangles[:,0])[:,2]/2
    areas=np.bincount(parents,weights=cross[:,2]/2,minlength=len(old_faces))
    max_area=float(np.max(np.abs(areas-old_area)))
    # Área incorpora a quantização XY float32 nas coordenadas ~1.000 unidades;
    # tolerância de 0,001 unidade², independente da precisão da fonte geográfica.
    assert max_z<.00012 and max_area<.001, f'Z error {max_z}; local XY area error {max_area}'
    return {'max_inserted_z_error_from_original_triangle_plane':max_z,'max_per_original_triangle_xy_area_difference':max_area,'per_triangle_xy_area_tolerance_scene_squared':.001}


def main():
    art = ROOT / 'artifacts/structural-pipeline/centro-lapa-tororo-fontenova'
    reports = ROOT / 'docs/reports/blender/centro-expansion'
    catalog = json.loads((ROOT / 'world/areas/mvp-centro-lacerda/blender-revisions.json').read_text(encoding='utf8'))
    source = catalog['validation_source']
    assert source['revision'] == 'R30B.74'
    with (ROOT / source['file']).open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == source['sha256']
    reference = json.loads((art / 'structural_reference.json').read_text(encoding='utf8'))
    fit = json.loads((art / 'georef_fit.json').read_text(encoding='utf8'))['robust_fit']
    sys.path.insert(0,str(ROOT))
    from tools.georef.world_reference import project_reference
    project_reference(ROOT,fit)
    data = np.load(art / 'candidate_terrain.npz')
    xyz = data['vertices']; original_faces = data['faces']
    triangles = shapely.polygons(xyz[original_faces, :2])
    terrain_domain = shapely.union_all(triangles)
    lake = Polygon(next(f['blender_xy'] for f in reference['features'] if f['osm_id'] == 15601931))
    building_features = [f for f in reference['features'] if f['layer'] == 'buildings' and f['closed']]
    buildings = [shapely.make_valid(Polygon(f['blender_xy'])) for f in building_features]
    building_tree = STRtree(buildings)
    features = []; excluded = []
    priority = {'concrete': 1, 'paved': 2, 'asphalt': 3, None: 4}
    # OSM width é em metros no chão. O fit horizontal usa metros EPSG:3857;
    # explicitar a correção local de escala Mercator, sem promover o fit candidato.
    theta = math.radians(fit['rotation_epsg3857_to_blender_deg'])
    c, s = math.cos(theta), math.sin(theta)
    tx, ty = fit['translation_blender']; scale = fit['scale_blender_units_per_meter']
    occupied = Polygon(); regions = []
    for f in reference['features']:
        tags = f['tags']; width = f['metrics'].get('width_m_tagged')
        if f['layer'] != 'pedestrian' or width is None:
            continue
        line = LineString(f['blender_xy'])
        if not terrain_domain.intersects(line):
            continue
        reasons = []
        if tags.get('footway') == 'crossing': reasons.append('Travessia depende do pavimento viário ainda ausente')
        if 'escadaria' in tags.get('name', '').lower(): reasons.append('Ligação de escada exige perfil próprio')
        if tags.get('bridge', 'no') != 'no' or tags.get('tunnel', 'no') != 'no' or tags.get('layer', '0') != '0': reasons.append('Passagem em nível separado não resolvida')
        if reasons:
            excluded.append({'osm_id': f['osm_id'], 'classification': 'NEEDS_REVIEW', 'reasons': reasons})
            continue
        x, y = line.centroid.coords[0]
        mercator_y = (-s * (x-tx) + c * (y-ty)) / scale
        latitude = math.atan(math.sinh(mercator_y / 6378137.0))
        factor = scale / math.cos(latitude)
        width_scene = width * factor
        corridor = line.buffer(width_scene / 2, cap_style='flat', join_style='round', quad_segs=4)
        if corridor.difference(terrain_domain).area > .001 or corridor.intersection(lake).area > .001:
            excluded.append({'osm_id': f['osm_id'], 'classification': 'NEEDS_REVIEW', 'reasons': ['Corredor ultrapassa domínio terrestre disponível; não recortar silenciosamente a largura']})
            continue
        overlaps = []
        for idx in building_tree.query(corridor, predicate='intersects'):
            area = corridor.intersection(buildings[idx]).area
            if area > .01:
                overlaps.append({'osm_id': building_features[idx]['osm_id'], 'area_scene_squared': area})
        if overlaps:
            excluded.append({'osm_id': f['osm_id'], 'classification': 'NEEDS_REVIEW', 'reasons': ['Conflito XY com footprint explícito'], 'building_overlaps': overlaps})
            continue
        material = priority.get(tags.get('surface'), 4)
        features.append({'osm_id': f['osm_id'], 'osm_type': f['osm_type'], 'node_refs': f['node_refs'], 'tags': tags,
                         'width_m_tagged': width, 'width_blender_candidate': width_scene,
                         'blender_units_per_ground_meter_candidate': factor, 'length_blender': line.length,
                         'material_index': material, 'polygon': corridor, 'line': line})
    features.sort(key=lambda f: (f['material_index'], f['osm_id']))
    assert features, 'Nenhum corredor com fonte suficiente'
    for f in features:
        region = f['polygon'].difference(occupied)
        occupied = occupied.union(f['polygon'])
        regions.append(region)
    region_tree = STRtree(regions)
    affected = set(int(i) for i in STRtree(triangles).query(occupied, predicate='intersects'))
    vertices = xyz.tolist()
    index = {tuple(v[:2]): i for i, v in enumerate(xyz)}
    faces = []; labels = []; owners = []; parents = []; omitted_area = 0.0

    def append_face(points, parent, material=0, owner=0):
        nonlocal omitted_area
        ids = []
        source_tri = xyz[original_faces[parent]].astype(float)
        a, b, d = source_tri
        matrix = np.column_stack((b[:2]-a[:2], d[:2]-a[:2]))
        for p in points:
            xy = np.asarray(p[:2], dtype=np.float32)
            key = tuple(xy)
            if key not in index:
                u, v = np.linalg.solve(matrix, xy.astype(float)-a[:2])
                z = a[2] + u*(b[2]-a[2]) + v*(d[2]-a[2])
                index[key] = len(vertices); vertices.append([float(xy[0]), float(xy[1]), float(np.float32(z))])
            ids.append(index[key])
        tri = np.asarray([vertices[i] for i in ids], dtype=float)
        cross = np.cross(tri[1]-tri[0], tri[2]-tri[0])
        if len(set(ids)) != 3 or abs(cross[2]) < 1e-9:
            omitted_area += Polygon(points).area
            return
        if cross[2] < 0: ids.reverse()
        faces.append(ids); labels.append(material); owners.append(owner); parents.append(parent)

    for i, original in enumerate(original_faces):
        if i not in affected:
            faces.append(original.tolist()); labels.append(0); owners.append(0); parents.append(i)
            continue
        triangle = triangles[i]; remaining = triangle
        for j in region_tree.query(triangle, predicate='intersects'):
            part = triangle.intersection(regions[j])
            if part.area < 1e-10: continue
            for polygon in polygons(part):
                for tri in shapely.constrained_delaunay_triangles(polygon).geoms:
                    append_face(list(tri.exterior.coords)[:-1], i, features[j]['material_index'], features[j]['osm_id'])
            remaining = remaining.difference(regions[j])
        for polygon in polygons(remaining):
            for tri in shapely.constrained_delaunay_triangles(polygon).geoms:
                append_face(list(tri.exterior.coords)[:-1], i)

    vertices = np.asarray(vertices, dtype=np.float32); faces = np.asarray(faces, dtype=np.int32)
    labels = np.asarray(labels, dtype=np.int32); owners = np.asarray(owners, dtype=np.int32)
    parents = np.asarray(parents, dtype=np.int32)
    assert np.array_equal(vertices[:len(xyz)], xyz)
    # GEOS calcula em double; Blender grava float32. Encontros quase coincidentes
    # podem quantizar em lados opostos do mesmo ULP. Unificar apenas pontos novos,
    # com tolerância numérica explícita de 0,12 mm, nunca dois controles originais.
    coordinate_tree = STRtree(shapely.points(vertices[:, :2]))
    pairs = coordinate_tree.query(shapely.points(vertices[len(xyz):, :2]), predicate='dwithin', distance=.00012)
    remap = np.arange(len(vertices), dtype=np.int32)
    numeric_welded = 0; max_numeric_weld = 0.0
    for local, neighbor in zip(*pairs):
        current = int(local) + len(xyz)
        if neighbor >= current: continue
        representative = int(remap[neighbor])
        if representative >= remap[current]: continue
        error = float(np.linalg.norm(vertices[current,:2].astype(float)-vertices[representative,:2]))
        if error > .00012: continue
        remap[current] = representative
        numeric_welded += 1; max_numeric_weld = max(max_numeric_weld, error)
    for i in range(len(xyz), len(vertices)):
        remap[i] = remap[remap[i]]
    faces = remap[faces]
    quantized_cross = np.cross(vertices[faces[:,1]].astype(float)-vertices[faces[:,0]], vertices[faces[:,2]].astype(float)-vertices[faces[:,0]])
    valid = quantized_cross[:,2] > 1e-9
    removed_numeric_triangles = int(np.sum(~valid))
    omitted_area += float(np.sum(np.abs(quantized_cross[~valid,2]))/2)
    faces = faces[valid]; labels = labels[valid]; owners = owners[valid]; parents = parents[valid]
    # Buffers de ways adjacentes podem conter um nó colinear apenas de um lado
    # do encontro. Subdividir a aresta longa pelo mesmo vértice existente; não
    # mover o nó, não tapar a fresta por uma face sobreposta.
    conforming_splits = 0
    for _ in range(8):
        all_edges = np.sort(np.concatenate((faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]])),axis=1)
        unique_edges, inverse_edges, edge_counts = np.unique(all_edges,axis=0,return_inverse=True,return_counts=True)
        singles = np.flatnonzero(edge_counts==1)
        edge_midpoints = np.mean(vertices[unique_edges[singles],:2].astype(float),axis=1)
        internal = singles[shapely.distance(shapely.points(edge_midpoints),terrain_domain.boundary)>.002]
        if not len(internal): break
        candidates = np.unique(unique_edges[internal])
        candidate_tree = STRtree(shapely.points(vertices[candidates,:2]))
        replacements = {}
        for edge_index in internal:
            start,end = unique_edges[edge_index]
            a,b = vertices[start,:2].astype(float),vertices[end,:2].astype(float)
            segment=LineString([a,b]);delta=b-a;length_squared=float(delta@delta)
            chain=[]
            for candidate_index in candidate_tree.query(segment,predicate='dwithin',distance=.00012):
                vertex=int(candidates[candidate_index])
                if vertex in (start,end):continue
                t=float((vertices[vertex,:2]-a)@delta/length_squared)
                if 1e-6<t<1-1e-6:chain.append((t,vertex))
            if not chain:continue
            face_index=int(np.flatnonzero(inverse_edges==edge_index)[0]%len(faces))
            if face_index in replacements:continue
            opposite=next(int(v) for v in faces[face_index] if v not in (start,end))
            ordered=[int(start),*[v for _,v in sorted(chain)],int(end)]
            triangles_to_add=[]
            for u,v in zip(ordered,ordered[1:]):
                tri=[u,v,opposite];points=vertices[tri].astype(float)
                area=np.cross(points[1]-points[0],points[2]-points[0])[2]
                if abs(area)<1e-9:continue
                if area<0:tri.reverse()
                triangles_to_add.append(tri)
            replacements[face_index]=triangles_to_add
            conforming_splits+=len(triangles_to_add)-1
        assert replacements, 'Encontro não é colinear; requer revisar a derivação'
        added_faces=[];added_labels=[];added_owners=[];added_parents=[]
        keep=np.ones(len(faces),dtype=bool)
        for i,tris in replacements.items():
            keep[i]=False
            added_faces.extend(tris);added_labels.extend([labels[i]]*len(tris));added_owners.extend([owners[i]]*len(tris));added_parents.extend([parents[i]]*len(tris))
        faces=np.concatenate((faces[keep],np.asarray(added_faces,np.int32)))
        labels=np.concatenate((labels[keep],np.asarray(added_labels,np.int32)))
        owners=np.concatenate((owners[keep],np.asarray(added_owners,np.int32)))
        parents=np.concatenate((parents[keep],np.asarray(added_parents,np.int32)))
    cross = np.cross(vertices[faces[:,1]].astype(float)-vertices[faces[:,0]], vertices[faces[:,2]].astype(float)-vertices[faces[:,0]])
    assert np.all(cross[:,2] > 1e-9) and omitted_area < .0001
    edges = np.sort(np.concatenate((faces[:,[0,1]], faces[:,[1,2]], faces[:,[2,0]])), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    boundary = unique[counts == 1]
    midpoints = np.mean(vertices[boundary,:2].astype(float), axis=1)
    distances = shapely.distance(shapely.points(midpoints), terrain_domain.boundary)
    internal_open = int(np.sum(distances > .002))
    if internal_open or np.any(counts > 2):
        diagnostics={'internal_open_edges':internal_open,'edges_more_than_two_faces':int(np.sum(counts>2)),
                     'examples':[vertices[e].tolist() for e in boundary[distances>.002][:15]],'numeric_welded':numeric_welded}
        (reports/'walkways_b75_rejected_topology.json').write_text(json.dumps(diagnostics,indent=2)+'\n',encoding='utf8')
    assert not np.any(counts > 2) and internal_open == 0, f'Malha não conforme: {internal_open} bordas internas'
    previous_area = float(np.sum(shapely.area(triangles)))
    area_after = float(np.sum(cross[:,2])/2)
    assert abs(area_after-previous_area) < .001
    preservation=surface_checks(xyz,original_faces,vertices,faces,parents)
    file = art / 'walkways_b75.npz'
    np.savez_compressed(file, vertices=vertices, faces=faces, materials=labels, osm_way_ids=owners, source_faces=parents)
    metadata = [{k:v for k,v in f.items() if k not in ('polygon','line')} for f in features]
    (art/'walkways_b75.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
    report = {'schema':'boas/centro-walkways-b75-derivation-v1','source':source,'source_capture_id':'osm-mapzen-20261005T045222Z',
              'source_reference':'artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json',
              'features':metadata,'excluded':excluded,'walkway_count':len(features), 'axis_length_blender':sum(f['length_blender'] for f in features),
              'walkway_area_scene_squared':occupied.area,'original_vertices':len(xyz),'vertices':len(vertices),'triangles':len(faces),
              'original_vertex_coordinates_exact':True,'original_surface_preserved_by_planar_subdivision':True,
              'surface_preservation':preservation,
              'raised_overlay_created':False,'dem_source_edited':False,'width_conversion':'Fit EPSG:3857 candidato / cos(latitude); width OSM em metros no chão. Precisão absoluta do fit/larguras não certificada.',
              'edge_design':'Eixos originais; término plano e curvas locais de buffer. Bordas derivadas, não levantamento de meio-fio.',
              'material_semantics':['terrain','concrete_tag','paved_tag_unspecified_finish','asphalt_tag','surface_pending'],
              'topology':{'internal_open_edges':internal_open,'edges_more_than_two_faces':int(np.sum(counts>2)), 'degenerate_triangles':0,'xy_area_difference':area_after-previous_area,'omitted_numeric_area':omitted_area,'new_vertices_numeric_welded':numeric_welded,'max_numeric_weld_scene':max_numeric_weld,'collapsed_numeric_triangles_removed':removed_numeric_triangles,'collinear_junction_edge_splits':conforming_splits},
              'mesh_file':file.relative_to(ROOT).as_posix(),'mesh_sha256':hashlib.file_digest(file.open('rb'),'sha256').hexdigest(),
              'classification':'ADAPT_LOCAL','walkability_approved':False,'motor_roads_built':False,'production_ready':False}
    (reports/'walkways_b75_derivation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ('walkway_count','axis_length_blender','vertices','triangles','topology')},ensure_ascii=False))
    print('excluded',len(excluded))


if __name__ == '__main__':
    main()
