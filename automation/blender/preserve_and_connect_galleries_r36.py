"""Preserva galerias B35 e acrescenta somente o encontro faltante com o terraço.

Restauro exato dos componentes anteriores; extensão arquitetônica candidata,
identificada separadamente. Uma só janela Blender, sem alterar ruas/planta.
"""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json';r=json.loads(rp.read_text(encoding='utf8'));a=r['access_connection_correction'];scene=bpy.context.scene
assert 'preserved_gallery_connection' not in r and a['terrain_stage']!='pending'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
names=[n for n in a['updated_objects'] if n.startswith(('GAL ','COLLISION '))]
known_objects=set(bpy.data.objects);known_meshes=set(bpy.data.meshes);known_mats=set(bpy.data.materials)
restored={}
try:
    with bpy.data.libraries.load(str(root/r['source_before']['file']),link=False) as (available,data):
        assert all(n in available.objects for n in names);data.objects=list(names)
    for name,original in zip(names,data.objects):
        o=scene.objects[name];old=o.data;mats=list(old.materials);o.data=original.data.copy();o.data.transform(wm(o).inverted()@wm(original));o.data.materials.clear()
        for material in mats:o.data.materials.append(material)
        for key in ('r36_connection_control','r36_world_correction_matrix'):
            if key in o:del o[key]
        o['boas_revision']=original.get('boas_revision','R30B.35');o['r36_preservation']='Galeria existente restaurada da fonte B35; não deslocar para fechar lacuna. Ligação acrescentada em componentes separados.'
        s=sig(o);assert s==a['updated_objects'][name]['before'],'Restauro divergente: '+name
        restored[name]=s;r['protected_signatures'][name]=s
        if not old.users:bpy.data.meshes.remove(old)
finally:
    for o in set(bpy.data.objects)-known_objects:
        if not o.users_scene:bpy.data.objects.remove(o,do_unlink=True)
    for table,known in ((bpy.data.meshes,known_meshes),(bpy.data.materials,known_mats)):
        for item in set(table)-known:
            if not item.users:table.remove(item)

S=Matrix(r['layout']['frame_world']);SI=S.inverted();center=r['layout']['palace_edge_length_m']/2
old=a['gallery_before'];end=Vector(old['origin_world']);start=S@Vector((center+5.8,3.8,end.z));u=end-start;u.z=0;length=u.length;u.normalize();n=Vector((-u.y,u.x,0));up=Vector((0,0,1));depth=old['depth_candidate_m'];height=old['height_candidate_m'];spring=old['spring_candidate_m'];top=old['top_plaza_m']
col=bpy.data.collections.new('ENVIRONMENT_FINAL | Ligação galerias terraço R36');scene.collection.children.link(col);col['boas_role']='visual_structure';col['reference_status']='partial'
cc=bpy.data.collections['COLLISION | Terraços Rio Branco R36'];stone=bpy.data.materials['GAL R34 | alvenaria mista de pedra'];brick=bpy.data.materials['GAL R34 | tijolo exposto dos arcos'];ivory=bpy.data.materials['GAL R34 | argamassa e guarda-corpo claro'];iron=bpy.data.materials['GAL R34 | grade de ferro escuro']
wall,inside,vault,arch,grilles,slab,rail=(G() for j in range(7))
# O trecho é acréscimo, nunca substituição dos três arcos originais. O número
# exato na parte encoberta não está verificado: candidato, sem aprovação Hero.
count=2;pitch=length/count;width=pitch*.73;rad=width/2
for j in range(count):
    x=(j+.5)*pitch;left=x-rad;right=x+rad
    wall.panel(start,u,n,j*pitch,left,0,height,depth);wall.panel(start,u,n,right,(j+1)*pitch,0,height,depth);wall.arch(start+u*x,u,n,width,spring,0,height,depth,32)
    arch.arch_ring(start+u*x,u,n,rad,spring,.20,.07,32)
    inside.box(start+u*x-n*(depth-.08)+up*(spring+rad)/2,(width,.16,spring+rad),(u,n,up));inside.box(start+u*x-n*depth/2-up*.08,(width,depth,.16),(u,n,up))
    for y in (.65,2.35,depth-.25):vault.arch_ring(start+u*x-n*y,u,n,rad-.04,spring,.055,.07,32)
    for k in range(max(3,round(width/.17))+1):
        xx=left+.09+k*(width-.18)/max(3,round(width/.17));ztop=spring+math.sqrt(max(0,rad*rad-(xx-x)**2));grilles.bar(start+u*xx-n*.15+up*.13,start+u*xx-n*.15+up*(ztop-.08),.018,6)
    for z in (.7,1.5,2.3):grilles.bar(start+u*(left+.06)-n*.15+up*z,start+u*(right-.06)-n*.15+up*z,.025,8)
slab.box(start+u*length/2-n*depth/2+up*((end.z+height+top)/2-start.z),(length,depth,top-end.z-height),(u,n,up))
for z,w in ((top+.13,.24),(top+1.08,.18)):rail.box(start+u*length/2+up*(z-start.z),(length,.38,w),(u,n,up))
num=round(length/.55)
for j in range(num+1):p=start+u*(j*length/num)+up*(top-start.z+.25);rail.bar(p,p+up*.70,.065,10)
for j in range(num):
    c=start+u*((j+.5)*length/num)+up*(top-start.z+.58)
    for k in range(18):
        t=k*math.pi/9;t2=(k+1)*math.pi/9;rail.bar(c+u*(.22*math.cos(t))+up*(.30*math.sin(t)),c+u*(.22*math.cos(t2))+up*(.30*math.sin(t2)),.034,6)
props={'boas_revision':'R30B.36','boas_role':'visual_structure','boas_location_candidate':'praca-tome-de-sousa','classification':'ADAPT_LOCAL','reference_status':'partial','dimensions_status':'candidatas; encontro entre controles geométricos existentes','arch_count_verified':False,'reference_media_ids':json.dumps(r['reference_media_ids'])}
created=[]
for label,g,mat in (('Alvenaria vazada',wall,stone),('Interiores e pisos',inside,stone),('Abóbadas',vault,stone),('Aduelas',arch,brick),('Grades',grilles,iron),('Laje da praça',slab,ivory),('Balaustrada contínua',rail,ivory)):
    o=g.object('GAL R36 | Ligação terraço | '+label,col,mat,props=props);created.append(o.name);r['created_objects'].append(o.name)
for label,g in (('Laje da praça',slab),('Piso das galerias',G())):
    if not g.v:g.box(start+u*length/2-n*depth/2-up*.08,(length,depth,.16),(u,n,up))
    o=g.object('COL R36 | Ligação terraço | '+label,cc,stone,props={**props,'boas_role':'static_collider'});o.hide_render=True;o.hide_set(True);r['colliders'].append(o.name)
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['preserved_gallery_connection']={'reason':'Correção do usuário: manter todas as galerias existentes; acrescentar o encontro, não deslocar o trecho anterior. Restauro exato a partir da B35.','restored_components':restored,'added_components':created,'segment':{**old,'name':'Ligação terraço','origin_world':list(start),'along_world':list(u),'outward_world':list(n),'length_from_existing_controls_m':length,'arch_count':count,'arch_width_candidate_m':width,'arch_count_verified':None,'classification':'ADAPT_LOCAL','placement_status':'candidate_architectural_connection'},'terrain_stage':'pending','visual_review':'pending','limitations':['Número de vãos/ritmo no trecho de ligação ainda candidato: parte encoberta na referência. Não é contagem medida.']}
a['gallery_relocation_status']='reverted_to_preserve_existing';a['gallery_after']=old
scene['architecture_revision']='R30B.36 | terraços, galerias preservadas e encontro acrescido | candidato'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'restored_original_components':len(restored),'added_components':len(created),'saved':r['source_after']},ensure_ascii=False))
