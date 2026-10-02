"""Finalizar componentes arquitetônicos e vincular a fonte reutilizável; mesma janela."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/cidade_baixa_r30b31.json';report=json.loads(path.read_text(encoding='utf8'))
if Path(bpy.data.filepath).resolve()!=(root/report['candidate_file']).resolve():raise RuntimeError('Revisão de trabalho incorreta')
for row in report['buildings']:
    oid=row['osm_way_id']
    if oid not in (1220650665,1220650857,1220650885,574235995):continue
    poly=[Vector((*p,0)) for p in row['footprint_controls_xy']];a,b=poly[:2];t=(b-a).normalized();L=(b-a).length
    o=scene.objects[f'BAIXA R31 | {oid} | Cobertura'];body=o.parent;top=row['ground_source_z']-.20+row['candidate_height_m']+.04
    # Duas águas longitudinais em vez de ápice piramidal genérico.
    halves=[]
    for side in (-1,1):
        result=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dp=(p-a).dot(t)-L/2;dq=(q-a).dot(t)-L/2
            if side*dp>=-1e-6:result.append(p)
            if dp*dq<0:result.append(p+(q-p)*(-dp/(dq-dp)))
        halves.append(result)
    vv=[];ff=[];inv=o.matrix_world.inverted()
    for half in halves:
        indices=[]
        for p in half:
            s=(p-a).dot(t);height=1.7*max(0,1-abs(s-L/2)/(L/2));indices.append(len(vv));vv.append(tuple(inv@(p+Vector((0,0,top+height)))))
        ff.append(tuple(indices))
    roof_faces=len(ff)
    for p,q in zip(poly,poly[1:]+poly[:1]):
        sp=(p-a).dot(t);sq=(q-a).dot(t);hp=1.7*max(0,1-abs(sp-L/2)/(L/2));hq=1.7*max(0,1-abs(sq-L/2)/(L/2))
        # Inserir vértice da cumeeira também na empena, sem fresta.
        boundary=[(p,hp)]
        if (sp-L/2)*(sq-L/2)<0:boundary.append((p+(q-p)*((L/2-sp)/(sq-sp)),1.7))
        boundary.append((q,hq))
        if not any(h>.0001 for point,h in boundary):continue
        indices=[]
        for point,h in [(p,0),(q,0)]+list(reversed(boundary)):
            indices.append(len(vv));vv.append(tuple(inv@(point+Vector((0,0,top+h)))))
        ff.append(tuple(indices))
    mat=o.data.materials[0];me=bpy.data.meshes.new(o.data.name+' | duas águas');me.from_pydata(vv,[],ff);me.materials.append(mat);me.materials.append(body.data.materials[0]);me.update()
    for face in list(me.polygons)[roof_faces:]:face.material_index=1
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o.data=me;o['roof_status']='candidate: duas águas pela vista fornecida; fundos não confirmados'
    row['roof_status']=o['roof_status']
# A biblioteca externa é a autoridade da escultura; composição usa vínculo relativo.
instance=scene.objects['MARIO CRAVO | Fonte da Rampa do Mercado'];old=instance.instance_collection
assetfile=root/report['monument']['asset_file']
if old.library is None:
    assetname=old.name
    with bpy.data.libraries.load(str(assetfile),link=True,relative=True) as (available,wanted):wanted.collections=[assetname]
    linked=wanted.collections[0]
    if linked is None:raise RuntimeError('Falha ao vincular biblioteca da fonte')
    instance.instance_collection=linked
    for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(old)
    linked.library.filepath=bpy.path.relpath(str(assetfile))
report['monument']['composition']='collection_instance_relative_linked_library'
report['reference_media_ids'].append('monumento-mario-cravo-oblique_right-84c7c6bb89db')
instance['boas_reference_media_ids']=json.dumps(report['reference_media_ids'])
# Enquadramento na janela visível, sem ocultar o resto da cidade.
target=Vector((-24,79,17));pos=Vector((-89,164,36));rotation=(target-pos).to_track_quat('Z','Y')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.region_3d.view_location=target;space.region_3d.view_distance=(target-pos).length;space.region_3d.view_rotation=rotation;space.clip_end=4000;space.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(root/report['candidate_file']))
report['candidate_sha256']=hashlib.file_digest((root/report['candidate_file']).open('rb'),'sha256').hexdigest();path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':report['candidate_file'],'monument_linked':instance.instance_collection.library.filepath,'roofs':'duas águas candidatas','terrain_changed':False},ensure_ascii=False))
