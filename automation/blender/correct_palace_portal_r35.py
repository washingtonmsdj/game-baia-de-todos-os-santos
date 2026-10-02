"""Corrige leitura do portal: cornija interrompida e colunas sobre pedestais."""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene;rp=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(rp.read_text(encoding='utf8'))
assert 'palace_portal_correction' not in r
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));T=Matrix(r34['palace']['frame_world']);up=Vector((0,0,1))
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix'];G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
col=bpy.data.collections['HERO | Palácio Rio Branco | relevos R35'];ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];changes={}
def replace(name,g):
    o=scene.objects[name];before=sig(o);tmp=g.object('TEMP | portal',col,o.data.materials[0],T);o.data=tmp.data;o.data.transform(wm(o).inverted()@T);bpy.data.objects.remove(tmp,do_unlink=True)
    changes[name]={'before':before,'after':sig(o)}
    if name in r['protected_signatures']:assert before==r['protected_signatures'].pop(name)
local=[T.inverted()@Vector((*p,70)) for p in r34['palace']['footprint_before_world']]
g=G()
for i,p in enumerate(local):
    q=local[(i+1)%len(local)];u=(q-p).normalized();n=Vector((-u.y,u.x,0));L=(q-p).length
    for z,sx,sz in ((.20,.65,.40),(6.1,.58,.22),(6.4,.56,.22),(13.20,.70,.25),(13.65,.82,.34),(14.13,.96,.32),(14.45,.70,.34)):
        spans=[(0,L)] if i!=1 or z<13 else [(0,L/2-5.62),(L/2+5.62,L)]
        for a,b in spans:g.box(p+u*((a+b)/2)+n*.12+up*z,(b-a,sx,sz),(u,n,up))
replace('RIO R34 | Cornijas contínuas e frisos',g)
g=G()
for x in (-4.95,4.95):
    g.box((x,.53,3.48),(1.02,.72,5.38));g.box((x,.57,.93),(1.30,.91,.28));g.box((x,.57,6.20),(1.32,.94,.28))
    g.lathe((x,.55,6.36),[(.46,0),(.46,.16),(.38,.25),(.34,.40),(.30,6.12),(.42,6.25),(.49,6.40),(.49,6.59)],24)
replace('RIO R34 | Colunas monumentais',g)
# Relevos devem estar na face dos pedestais, não soterrados na coluna anterior.
for name in ('RIO R35 | Painéis em relevo do portal','RIO R35 | Cartelas dos pedestais','RIO R35 | Rosetas dos pedestais'):
    o=scene.objects[name];before=sig(o)
    for v in o.data.vertices:v.co.y+=.42;v.co.x+=.15 if v.co.x>0 else -.15
    o.data.update();changes[name]={'before':before,'after':sig(o)}
# A foto mostra coroamento curvo, não raios salientes como a primeira aproximação.
g=G()
for x in (-16,-7.45,7.45,16):
    for j in range(18):
        a=math.pi*j/18;b=math.pi*(j+1)/18
        pts=[]
        for k in range(9):
            t=a+(b-a)*k/8;radius=1.04+.06*math.sin(math.pi*k/8)
            pts.append((x+radius*math.cos(t),.435,15.30+radius*math.sin(t)))
        for p,q in zip(pts,pts[1:]):g.bar(p,q,.045,8)
replace('RIO R35 | Folhas dos frontões',g)
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items())
r['palace_portal_correction']={'reason':'Comparação direta com a foto frontal: colunas superiores apoiadas em pedestais, cornija das alas interrompida pelo pavilhão e coroamentos curvos sem raios.','objects':changes,'dimensions_status':'candidate','reference':'palacio-rio-branco-front-c207e62d3f85'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
