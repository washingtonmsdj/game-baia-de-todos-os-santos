"""Conferência localizada após reabrir: fontes, footprints, materiais e biblioteca."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/cidade_baixa_r30b31.json';report=json.loads(path.read_text(encoding='utf8'));before=json.loads((root/'docs/reports/blender/cidade_baixa_building_before.json').read_text(encoding='utf8'))
file=root/report['candidate_file'];assert Path(bpy.data.filepath).resolve()==file.resolve()
scene=bpy.context.scene;results=[]
for row in report['buildings']:
    body=scene.objects[row['body']];old=next(o for o in before['objects'] if o['name']==body.name)
    original=old['mesh_vertices_world'][:old['vertices']//2];controls=row['footprint_controls_xy']
    delta=max(min((Vector(v[:2])-Vector(p)).length for p in controls) for v in original)
    assert delta<.001
    live=json.loads(body['boas_footprint_controls']);assert live==controls
    pts=[body.matrix_world@v.co for v in body.data.vertices]
    for axis in (0,1):
        assert abs(min(v[axis] for v in pts)-min(v[axis] for v in original))<.001
        assert abs(max(v[axis] for v in pts)-max(v[axis] for v in original))<.001
    results.append({'osm_way_id':row['osm_way_id'],'footprint_delta_m':delta,'mesh_vertices':len(body.data.vertices),'mesh_faces':len(body.data.polygons),'children':len(body.children),'height_status':'candidate'})
instance=scene.objects['MARIO CRAVO | Fonte da Rampa do Mercado'];collection=instance.instance_collection;assert collection.library and collection.library.filepath.startswith('//');assert len(collection.objects)==4
glass=next(o for o in scene.objects if o.name.startswith('BAIXA R31 |') and o.name.endswith(' | Vidros'))
p=next(n for n in glass.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED');assert p.inputs['Transmission Weight'].default_value>.6
report['reopened']=True;report['reopen_review']={'scene':scene.name,'buildings':results,'facade_components':sum(o.name.startswith('BAIXA R31 |') for o in scene.objects),'monument_relative_library':collection.library.filepath.replace('\\','/'),'monument_components':len(collection.objects),'glass_transmission':p.inputs['Transmission Weight'].default_value,'terrain_vertices':len(scene.objects['MVP | terreno corrigido | colisão estática'].data.vertices),'terrain_proxy_vertices':len(scene.objects['R30A5 | COLLISION | terrain proxy'].data.vertices)}
report['visual_review']={'status':'partial_modeling_reviewed','images':['artifacts/cidade-baixa/r30b31_predios.png','artifacts/cidade-baixa/r30b31_cravo.png'],'scope':'Vistas isoladas de modelagem com piso temporário de estúdio; não runtime nem cenário fictício de produção.','limitations':['Identidade por foto e alturas candidatas; dimensões reais não medidas.','Sete parcelas receberam fachadas; parcela 1220650874 mantém blockout anterior.','Fundos, laterais não fotografadas e interiores comerciais não concluídos.','Forma/rotação da escultura e implantação da bacia ainda candidatas; não asset aprovado.']}
report['candidate_sha256']=hashlib.file_digest(file.open('rb'),'sha256').hexdigest();path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'reopened':True,'buildings':len(results),'footprints_preserved':True,'monument_components':len(collection.objects),'source_hash':report['candidate_sha256']}))
