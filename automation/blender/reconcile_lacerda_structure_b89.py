"""Fecha encontros e níveis relativos da arquitetura documental B88.

B80 e seu datum de instalação permanecem intactos no histórico.
"""
import bpy,bmesh,json,math,hashlib,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
base=Path(bpy.data.filepath);assert base.name=='salvador_lacerda_r30b88_estrutura_arquitetonica_plantas.blend'
dest=root/'blender/salvador_lacerda_r30b89_conjunto_arquitetonico_niveis.blend';assert not dest.exists()
scene=bpy.context.scene;assert scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
out=root/'docs/reports/blender/lacerda-massing-b89';out.mkdir(parents=True,exist_ok=True)
prior=json.loads((root/'docs/reports/blender/lacerda-massing-b88/application.json').read_text())
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix'];sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
def bounds(o):
    p=[inv@wm(o)@v.co for v in o.data.vertices]
    return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
for r in prior['changes']+prior['added']:assert sig(scene.objects[r['object']])==r.get('after',r)['signature'],r['object']
ssot_hash=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest();assert ssot_hash==cfg['ssot_sha256']
proxy_before={o.name:sig(o) for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain_before=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
upper=cfg['levels']['upper_walkable'];old_lower=cfg['levels']['lower_scene_floor_preserved'];lower=upper+cfg['levels']['lower_project_floor_offset'];delta=lower-old_lower
rows={r['object']:r for r in prior['changes']};changes=[];buffers={}
wall_names=['B88 | galeria nova | peitoril estrutural','B88 | galeria nova | limite envidraçado','B88 | galeria nova | verga estrutural']
head=[Vector(p) for p in cfg['polygons']['new_gallery']['points_local']]
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
if area(head)<0:head.reverse()
source_bridge=[Vector(p) for p in cfg['polygons']['bridge']['points_local']]
ends=[source_bridge[0],source_bridge[3]]
opening=[i for i,a in enumerate(head) if min((a-ends[0]).length,(a-ends[1]).length)<1e-5 and min((head[(i+1)%len(head)]-ends[0]).length,(head[(i+1)%len(head)]-ends[1]).length)<1e-5]
assert len(opening)==1;opening=opening[0]
inner=[]
for i,b in enumerate(head):
    u=(b-head[i-1]).normalized();v=(head[(i+1)%len(head)]-b).normalized();n=Vector((-u.y,u.x));nv=Vector((-v.y,v.x));p=b+n*.10;q=b+nv*.10;cross=u.x*v.y-u.y*v.x
    inner.append(b+(n+nv)*.05 if abs(cross)<1e-6 else p+u*(((q-p).x*v.y-(q-p).y*v.x)/cross))
def wall(o,z0,z1):
    verts=[];faces=[];back=wm(o).inverted()@M
    for i,a in enumerate(head):
        if i==opening:continue
        b=head[(i+1)%len(head)];c=inner[(i+1)%len(head)];d=inner[i];first=len(verts)
        verts.extend(tuple(back@Vector((v.x,v.y,z))) for z in (z0,z1) for v in (a,b,c,d))
        faces.extend(tuple(first+j for j in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    mesh=bpy.data.meshes.new('B89 | '+o.name);mesh.from_pydata(verts,[],faces)
    for mat in o.data.materials:mesh.materials.append(mat)
    return mesh
for name,z in zip(wall_names,[(upper,upper+.7),(upper+.7,upper+3.75),(upper+3.75,upper+4.)]):buffers[name]=wall(scene.objects[name],*z)
for name,row in rows.items():
    domain=row['domain'];o=scene.objects[name]
    if not o.visible_get() and name not in {b['object'] for b in prior['bindings_updated']}:continue
    if domain not in ('LOWER_LOBBY','OLD_TOWER','NEW_TOWER'):continue
    # Técnico superior/capeamento já recebem +14,00 no corpo documental B88.
    if name in ('TORRE | corpo tecnico superior','TORRE | capeamento tecnico'):continue
    mesh=o.data.copy();trans=inv@wm(o);back=wm(o).inverted()@M
    for v in mesh.vertices:
        p=trans@v.co
        if domain=='LOWER_LOBBY':p.z+=delta
        elif domain=='OLD_TOWER':
            top=upper-.33
            if p.z<top:p.z=lower+(p.z-old_lower)*(top-lower)/(top-old_lower)
        elif name.startswith('CASCA |'):
            bottom=old_lower+5.76;top=upper-2.8
            p.z=lower+5.76+(p.z-bottom)*(top-lower-5.76)/(top-bottom)
        elif p.z<=70.:p.z=lower+(p.z-old_lower)*(upper-lower)/(70.-old_lower)
        elif p.z<=74.125:p.z=upper+(p.z-70.)*4./4.125
        else:p.z=upper+4.+(p.z-74.125)*10./(84.56-74.125)
        v.co=back@p
    mesh.update();buffers[name]=mesh
before={n:{'signature':sig(scene.objects[n]),'bounds':bounds(scene.objects[n])} for n in buffers}
for n,mesh in buffers.items():
    bm=bmesh.new();bm.from_mesh(mesh);assert not any(f.calc_area()<1e-9 for f in bm.faces),n
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
for n,mesh in buffers.items():
    o=scene.objects[n];o.data=mesh;o['boas_generated_revision']='R30B.89';o['boas_provenance_ids']=json.dumps(['derived:lacerda-massing-b89']);o['accuracy']='PROJECT_REFERENCE_DERIVED';o['replacement_required']=True;o['boas_production_ready']=False
    o['boas_z_registration_status']='ARCHITECTURAL_RELATIVE_PROJECT_DATUM_NOT_GEOGRAPHIC_ALTITUDE'
    changes.append({'object':n,'domain':rows.get(n,{}).get('domain','NEW_GALLERY'),'before':before[n],'after':{'signature':sig(o),'bounds':bounds(o)}})
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain_before
assert all(sig(bpy.data.objects[n])==s for n,s in proxy_before.items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot_hash
scene['lacerda_revision']='R30B.89 | conjunto estrutural relativo às pranchas 12/17/23';scene['boas_historic_movement_enabled']=False
report={'revision':'R30B.89','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':prior['sha256'],'scene':scene.name,'pid':os.getpid(),'changes':changes,
 'gallery_opening_cad_edge':opening,'upper_relative_datum_scene':upper,'lower_architecture_floor_scene':lower,'architectural_access_difference_m':59.01,'lower_architectural_delta_m':delta,
 'lower_geographic_datum_status':'NOT_REGISTERED_PROJECT_RELATIVE_GEOMETRY','LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','historic_witnesses':27,'movement_enabled':False,'production_ready':False,'ssot_sha256':ssot_hash,'terrain_preserved':True,'proxy_b82_preserved':True,'reopened':False,
 'reason':'Encontro galeria/ponte identificado por endpoints físicos, corrigindo inversão de winding; níveis arquitetônicos relativos 0/-59,01/+4/+14, sem resolver datum do poço B80.'}
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report['sha256']=digest;path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cat_path=root/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cat_path.read_text())
entry={'file':report['file'],'revision':'R30B.89','parent_file':report['parent_file'],'sha256':digest,'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Estrutura relativa SUCOP com níveis e encontro galeria/ponte reconciliados; implantação/datum geográfico e instalação ainda pendentes.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
cat_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B89','changes':len(changes),'lower_floor_level':lower,'document_relative_difference_m':59.01,'file':report['file'],'sha256':digest,'production_ready':False}))
