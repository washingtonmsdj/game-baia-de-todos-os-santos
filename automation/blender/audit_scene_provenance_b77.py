"""Inventário de bindings; recurso sem origem não recebe aprovação implícita."""
import bpy,json,runpy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
registry=json.loads((ROOT/'world/data-provenance.json').read_text(encoding='utf8'));known={r['resource_id']:r for r in registry['resources']}
def ids(owner):
    value=owner.get('boas_provenance_ids',[])
    return json.loads(value) if isinstance(value,str) else list(value)
def collection_ids(col,seen=None):
    seen=set() if seen is None else seen
    if col.name in seen:return []
    seen.add(col.name);result=ids(col)
    if not result:
        for parent in bpy.data.collections:
            if col.name in parent.children:result.extend(collection_ids(parent,seen))
    return result
objects=[];unknown=[];bad=[]
for ob in bpy.context.scene.objects:
    resource_ids=ids(ob) or sorted({item for col in ob.users_collection for item in collection_ids(col)})
    if not resource_ids:unknown.append(ob.name)
    bad.extend({'object':ob.name,'id':item} for item in resource_ids if item not in known)
    materials=[m.name for m in getattr(ob.data,'materials',[]) if m]
    objects.append({'object':ob.name,'resource_ids':resource_ids,'materials':materials,'role':ob.get('boas_role'),'hidden_render':ob.hide_render})
raw_hashes={raw['sha256']:r['resource_id'] for r in known.values() for raw in r.get('raw_files',[]) if raw.get('sha256')}
images=[]
for image in bpy.data.images:
    if image.source!='FILE':continue
    path=Path(bpy.path.abspath(image.filepath));sha=None;logical=None
    if path.is_file():
        with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
        try:logical=path.resolve().relative_to(ROOT).as_posix()
        except ValueError:logical=None
    images.append({'image':image.name,'project_file':logical,'external_file':logical is None,'sha256':sha,'resource_ids':ids(image) or ([raw_hashes[sha]] if sha in raw_hashes else [])})
materials=[]
for mat in bpy.data.materials:
    materials.append({'material':mat.name,'resource_ids':ids(mat),'images':[n.image.name for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat.use_nodes else []})
artifact=ROOT/'artifacts/lacerda-corridor/scene_provenance_b77.json';artifact.write_text(json.dumps({'objects':objects,'materials':materials,'images':images},ensure_ascii=False),encoding='utf8')
summary={'schema':'boas/scene-provenance-audit-v1','objects':len(objects),'objects_without_binding':len(unknown),'unknown_examples':unknown[:30],'invalid_resource_ids':bad,'materials':len(materials),'images':images,'inventory_file':'artifacts/lacerda-corridor/scene_provenance_b77.json','release_ready':False,'note':'Binding não equivale a licença aprovada; referências temporárias não foram aplicadas como textura. Exportador deve emitir manifesto completo de objetos, materiais, imagens e arquivos antes de release.'}
(ROOT/'docs/reports/blender/lacerda-corridor/provenance_b77.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:summary[k] for k in ('objects','objects_without_binding','invalid_resource_ids','release_ready')}))
