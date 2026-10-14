"""Derivar terreno/traçados candidatos de fontes preservadas; não altera o Blender."""
from pathlib import Path
import sys,json,math,hashlib,heapq
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'artifacts/geospatial-python'))
import numpy as np
import shapely
from shapely.geometry import Polygon,LineString,Point,box
from shapely.strtree import STRtree

def main():
    out=ROOT/'artifacts/structural-pipeline/centro-lapa-tororo-fontenova'
    report_dir=ROOT/'docs/reports/blender/centro-expansion'
    source=json.loads((ROOT/'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json').read_text(encoding='utf8'))
    reference=json.loads((out/'structural_reference.json').read_text(encoding='utf8'))
    fit=json.loads((out/'georef_fit.json').read_text(encoding='utf8'))['robust_fit']
    sys.path.insert(0,str(ROOT))
    from tools.georef.world_reference import project_reference
    project_reference(ROOT,fit)
    controls=json.loads((report_dir/'live_controls.json').read_text(encoding='utf8'))
    assert len(controls['controls'])>=6 and max(c['cached_center_difference'] for c in controls['controls'])<1e-4
    bounds=json.loads((report_dir/'existing_ground_boundaries.json').read_text(encoding='utf8'))
    polygons=[];segments=[];endpoints=[];projection_diagnostics=[]
    for d in bounds['domains']:
        assert not d['irregular_boundary_vertices'] and not d['open_chains']
        ring=max(d['rings'],key=lambda p:Polygon(np.asarray(p)[:,:2]).area)
        polygon=Polygon(np.asarray(ring)[:,:2])
        if not polygon.is_valid:
            original=polygon;valid=shapely.make_valid(original)
            parts=[p for p in getattr(valid,'geoms',[valid]) if p.geom_type in ('Polygon','MultiPolygon')]
            polygon=shapely.union_all(parts)
            assert abs(polygon.area-original.area)<1e-6, 'Reparo projetado alteraria área; revisar antes de integrar'
            projection_diagnostics.append({'object':d['object'],'classification':'NEEDS_REVIEW','reason':shapely.is_valid_reason(original),'projected_area_delta':polygon.area-original.area,'repair_scope':'Somente máscara XY derivada; mesh 3D e coordenadas fonte preservadas'})
        assert polygon.is_valid
        polygons.append(polygon)
        for a,b in zip(ring,ring[1:]):
            if math.dist(a[:2],b[:2])>1e-8:
                segments.append(LineString([a[:2],b[:2]]));endpoints.append([a,b])
    segment_tree=STRtree(segments);endpoints=np.array(endpoints,float)
    targets={f['osm_id']:f for f in reference['features'] if f['osm_id'] in (257113955,3346613,15601931)}
    lake=Polygon(targets[15601931]['blender_xy']);assert lake.is_valid
    # Margem de autoria/streaming candidata; não é limite real da cidade.
    rect=box(-260.75,-1900,1350,621.7371215820312)
    existing=shapely.union_all(polygons)
    # Não preencher ausências costeiras dentro do bounding box do núcleo.
    # A expansão segue somente os lados sul/leste; faixa curta inclui o contorno
    # irregular existente, que é subtraído sem mover seus vértices.
    sector=shapely.union_all([box(-260.75,-1900,1350,-250),box(512, -1900,1350,621.7371215820312)])
    domain=rect.intersection(sector).difference(existing).difference(lake)
    assert domain.is_valid
    raw=np.load(ROOT/source['capture_folder']/'terrain.npz');values=raw['elevation']
    theta=math.radians(fit['rotation_epsg3857_to_blender_deg']);c,s=math.cos(theta),math.sin(theta)
    scale=fit['scale_blender_units_per_meter'];tx,ty=fit['translation_blender']
    def dem(xy):
        xy=np.asarray(xy,float).reshape(-1,2);dx=xy[:,0]-tx;dy=xy[:,1]-ty
        ex=(c*dx+s*dy)/scale;ey=(-s*dx+c*dy)/scale
        u=(ex-float(raw['left']))/float(raw['pixel_size'])-.5;v=(float(raw['top'])-ey)/float(raw['pixel_size'])-.5
        i=np.floor(u).astype(int);j=np.floor(v).astype(int);du=u-i;dv=v-j
        assert np.all((i>=0)&(j>=0)&(i<values.shape[1]-1)&(j<values.shape[0]-1))
        return values[j,i]*(1-du)*(1-dv)+values[j,i+1]*du*(1-dv)+values[j+1,i]*(1-du)*dv+values[j+1,i+1]*du*dv
    transition=120.0
    def field(xy,details=False):
        xy=np.asarray(xy,float).reshape(-1,2);z=dem(xy)
        indices=segment_tree.nearest(shapely.points(xy));p=endpoints[indices,0];q=endpoints[indices,1]
        delta=q[:,:2]-p[:,:2];t=np.clip(np.sum((xy-p[:,:2])*delta,axis=1)/np.sum(delta*delta,axis=1),0,1)
        nearest=p[:,:2]+delta*t[:,None];distance=np.linalg.norm(xy-nearest,axis=1)
        boundary=p[:,2]+(q[:,2]-p[:,2])*t
        # Encaixe regional explícito aos controles atuais, sem escala/offset Z global.
        edge_dem=dem(nearest);a=np.clip(distance/transition,0,1);weight=1-3*a*a+2*a*a*a
        result=z+weight*(boundary-edge_dem)
        return (result,result-z,distance) if details else result
    verts=[];faces=[];index={}
    def vertex(p):
        key=(round(p[0],7),round(p[1],7))
        if key not in index:index[key]=len(verts);verts.append(key)
        return index[key]
    def append_polygon(poly):
        if poly.is_empty or poly.area<1e-9:return
        if poly.geom_type!='Polygon':
            for part in getattr(poly,'geoms',[]):append_polygon(part)
            return
        for tri in shapely.constrained_delaunay_triangles(poly).geoms:
            p=list(tri.exterior.coords)[:-1]
            if len(p)!=3 or tri.area<1e-9:continue
            if (p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[1][1]-p[0][1])*(p[2][0]-p[0][0])<0:p.reverse()
            faces.append([vertex(v) for v in p])
    spacing=6.0
    x0,y0,x1,y1=rect.bounds
    for x in np.arange(x0,x1,spacing):
        for y in np.arange(y0,y1,spacing):
            cell=box(x,y,min(x+spacing,x1),min(y+spacing,y1))
            if domain.covers(cell):
                p=list(cell.exterior.coords)[:-1]
                ids=[vertex(v) for v in p]
                faces.extend([[ids[0],ids[1],ids[2]],[ids[0],ids[2],ids[3]]])
            elif domain.intersects(cell):append_polygon(domain.intersection(cell))
    xy=np.array(verts);z,correction,dist=field(xy,True)
    xyz=np.column_stack((xy,z));faces=np.array(faces,np.int32)
    assert np.min(z)>=0 and np.max(np.abs(correction))<25, 'Domínio terrestre/encaixe precisa de revisão antes do Blender'
    cross=np.cross(xyz[faces[:,1]]-xyz[faces[:,0]],xyz[faces[:,2]]-xyz[faces[:,0]])
    assert np.isfinite(xyz).all() and np.all(np.linalg.norm(cross,axis=1)>1e-9)
    assert np.all(cross[:,2]>0)
    np.savez_compressed(out/'candidate_terrain.npz',vertices=xyz.astype(np.float32),faces=faces)
    # Eixos são referências, nunca larguras ou superfícies dirigíveis inventadas.
    traces=[]
    for f in reference['features']:
        if f['layer'] not in ('roads','pedestrian','steps','buildings'):continue
        line=LineString(f['blender_xy'])
        clipped=line.intersection(rect.intersection(sector)).difference(existing)
        if clipped.is_empty:continue
        for part in getattr(clipped,'geoms',[clipped]):
            if part.geom_type!='LineString' or part.length<.1:continue
            coordinates=list(part.coords);dense=[]
            for a,b in zip(coordinates,coordinates[1:]):
                n=max(1,math.ceil(math.dist(a,b)/3))
                dense.extend([[a[k]+(b[k]-a[k])*t/n for k in range(2)] for t in range(n)])
            dense.append(coordinates[-1]);points=np.array(dense)
            traces.append({'osm_type':f['osm_type'],'osm_id':f['osm_id'],'layer':f['layer'],'tags':f['tags'],'width_m_verified':f['metrics'].get('width_m_tagged'),'points':np.column_stack((points,field(points)+.09)).tolist(),'reference_only':True,'layer_z_verified':False})
    # Preservar também o anel interno da Arena, ausente no JSON simplificado.
    import xml.etree.ElementTree as ET
    xml=ET.parse(ROOT/source['capture_folder']/'map.osm').getroot()
    nodes={e.attrib['id']:(float(e.attrib['lat']),float(e.attrib['lon'])) for e in xml.findall('node')}
    ways={e.attrib['id']:[v.attrib['ref'] for v in e.findall('nd')] for e in xml.findall('way')}
    arena=next(e for e in xml.findall('relation') if e.attrib['id']=='3346613')
    pending=[ways[e.attrib['ref']][:] for e in arena.findall('member') if e.attrib.get('type')=='way' and e.attrib.get('role')=='inner']
    rings=[]
    while pending:
        chain=pending.pop(0)
        while chain[0]!=chain[-1]:
            found=next((i for i,w in enumerate(pending) if w[0]==chain[-1] or w[-1]==chain[-1]),None)
            assert found is not None,'Anel interno da Arena incompleto'
            part=pending.pop(found)
            if part[-1]==chain[-1]:part.reverse()
            chain.extend(part[1:])
        pts=[]
        for node in chain:
            lat,lon=nodes[node];ex=6378137*math.radians(lon);ey=6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))
            pts.append([scale*(c*ex-s*ey)+tx,scale*(s*ex+c*ey)+ty])
        rings.append(pts)
    landmark_rows=[]
    for osm_id,location_id in [(257113955,'center-lapa'),(3346613,'arena-fonte-nova'),(15601931,'dique-do-tororo')]:
        f=targets[osm_id];points=np.array(f['blender_xy']);base=float(np.median(field(points)))
        landmark_rows.append({'osm_id':osm_id,'osm_type':f['osm_type'],'location_id':location_id,'name':f['tags']['name'],'outer':points.tolist(),'inner':rings if osm_id==3346613 else [],'base_z_candidate':base,'height_m_tagged':float(f['tags']['height']) if 'height' in f['tags'] else None,'absolute_height_verified':False})
    lake_row=next(t for t in landmark_rows if t['osm_id']==15601931)
    lake_row['water_z_candidate']=float(np.min(field(lake_row['outer']))-.3)
    lake_triangles=shapely.constrained_delaunay_triangles(lake)
    lake_row['triangles']=[list(t.exterior.coords)[:3] for t in lake_triangles.geoms]
    # Três percursos topológicos; não aprovar altura/faixa/ponte por proximidade XY.
    graph=json.loads((out/'road_graph.json').read_text(encoding='utf8'));gn={n['id']:n for n in graph['nodes']};gw={w['osm_way_id']:w for w in graph['ways']}
    adjacency={};source_tags={f['osm_id']:f['tags'] for f in reference['features'] if f['layer']=='roads'}
    for e in graph['edges']:
        w=gw[e['osm_way_id']];tags=source_tags[e['osm_way_id']]
        if e['access']=='restricted' or tags.get('highway') in ('cycleway','track') or tags.get('bridge') not in (None,'no') or tags.get('tunnel') not in (None,'no') or tags.get('layer','0')!='0':continue
        if not rect.covers(Point(gn[e['from']]['blender_xy'])) or not rect.covers(Point(gn[e['to']]['blender_xy'])):continue
        pairs=[(e['from'],e['to'])] if e['direction']=='forward' else [(e['to'],e['from'])] if e['direction']=='reverse' else [(e['from'],e['to']),(e['to'],e['from'])]
        for a,b in pairs:
            adjacency.setdefault(a,[]).append((b,math.dist(gn[a]['blender_xy'],gn[b]['blender_xy']),e['osm_way_id']))
    start=min(adjacency,key=lambda n:math.dist(gn[n]['blender_xy'],[50,-180]))
    queue=[(0,start)];distance={start:0};parent={}
    while queue:
        d,a=heapq.heappop(queue)
        if d!=distance[a]:continue
        for b,length,way in adjacency.get(a,[]):
            nd=d+length
            if nd<distance.get(b,float('inf')):distance[b]=nd;parent[b]=(a,way);heapq.heappush(queue,(nd,b))
    routes=[]
    for target in landmark_rows:
        geometry=Polygon(target['outer'])
        end=min(distance,key=lambda n:geometry.boundary.distance(Point(gn[n]['blender_xy'])))
        if end not in distance:routes.append({'location_id':target['location_id'],'status':'no_source_route'});continue
        route=[end];ids=[]
        while route[-1]!=start:
            a,way=parent[route[-1]];ids.append(way);route.append(a)
        route.reverse();ids.reverse()
        routes.append({'location_id':target['location_id'],'status':'reference_route_not_driveable_approval','node_ids':route,'osm_way_ids':ids,'points':[gn[n]['blender_xy'] for n in route],'length_blender_units':distance[end],'target_boundary_distance_blender_units':geometry.boundary.distance(Point(gn[end]['blender_xy'])),'direct_target_access_verified':False,'widths_verified':all(gw[w].get('width_m_tagged') is not None for w in ids)})
    data={'schema':'boas/centro-expansion-candidate-v1','source_summary':'docs/reports/world/centro-lapa-tororo-fontenova/source_summary.json','terrain_npz':(out/'candidate_terrain.npz').relative_to(ROOT).as_posix(),'scope_bounds':list(rect.bounds),'existing_outline_holes_preserved_in_existing_mesh':sum(len(d['rings'])-1 for d in bounds['domains']),'traces':traces,'targets':landmark_rows,'routes':routes}
    (out/'candidate_scene.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
    report={'schema':data['schema'],'source_scene':bounds['source'],'xy_controls':controls['controls'],'relative_alignment_checked':True,'absolute_georeference_verified':False,'existing_projected_boundary_review':projection_diagnostics,'terrain_vertices':len(xyz),'terrain_triangles':len(faces),'spacing_design_m':spacing,'native_resolution_verified':False,'interpolation':'bilinear, original Terrarium values preserved','source_dem_changed':False,'global_z_scale_or_offset_applied':False,'local_transition':{'classification':'ADAPT_LOCAL','width_design_m':transition,'reason':'Continuidade com os anéis reais das duas superfícies existentes; não é calibração altimétrica absoluta','max_abs_delta_z':float(np.max(np.abs(correction))),'affected_vertices':int(np.sum(abs(correction)>1e-6))},'traces':len(traces),'road_widths_invented':False,'roads_final_built':False,'targets':[{'id':t['osm_id'],'location_id':t['location_id'],'inner_rings':len(t['inner'])} for t in landmark_rows],'routes':[{'location_id':t['location_id'],'status':t['status'],'widths_verified':t.get('widths_verified'),'length_blender_units':t.get('length_blender_units')} for t in routes],'geometry_finite':True,'degenerate_triangles':0,'production_ready':False}
    (report_dir/'candidate_derivation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='xy_controls'},ensure_ascii=True))

if __name__=='__main__':main()
