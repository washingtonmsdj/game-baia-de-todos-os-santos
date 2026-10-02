"""Correção fotográfica: galeria ligada ao bastião, escadas recuadas e vão interno.

Mesma B36 em elaboração. Sem alterar footprint, torre, DEM ou ruas.
Dimensões arquitetônicas continuam candidatas; não são um levantamento.
"""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/terracos_palacio_r30b36.json'
r=json.loads(rp.read_text(encoding='utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(root/r['source_after']['file']).resolve()
assert 'access_connection_correction' not in r,'Já aplicado; não repetir'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig,wm=h['signature'],h['world_matrix']
G=runpy.run_path(str(root/'automation/blender/architectural_mesh.py'))['Geometry']
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Mudança externa no escopo protegido'
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'))
r35=json.loads((root/'docs/reports/blender/torre_galerias_r30b35.json').read_text(encoding='utf8'))
S=Matrix(r['layout']['frame_world']);SI=S.inverted();up=Vector((0,0,1))
x0,x1,back,front=r['layout']['colonnade_extent_candidate'];floor=r['layout']['colonnade_floor_candidate_m'];roof=r['layout']['colonnade_roof_candidate_m'];levels=r['layout']['garden_levels_candidate_m'];center=r['layout']['palace_edge_length_m']/2
col=bpy.data.collections['HERO | Terraços Rio Branco | fotografia R36'];ivory=bpy.data.materials['RIO R34 | ornatos e cornijas marfim'];stone=bpy.data.materials['RIO R34 | embasamento de pedra'];pave=bpy.data.materials['PRACA R35 | paralelepípedos métricos'];wallmat=bpy.data.materials['RIO R36 | cantaria dos terraços']
changes={}
def replace(name,g):
    o=scene.objects[name];before=sig(o);old=o.data;tmp=g.object('TEMP | encontro R36',col,old.materials[0],S);o.data=tmp.data;o.data.transform(wm(o).inverted()@S);bpy.data.objects.remove(tmp,do_unlink=True)
    if not old.users:bpy.data.meshes.remove(old)
    o['r36_correction']='Acesso interno/ligação arquitetônica conferida nas fotos; dimensões candidatas.';changes[name]={'before':before,'after':sig(o)}

# Um único trecho de três arcos conserva sua extensão e ritmo. A junta terminal
# passa a coincidir com o encontro lateral do bastião; não uma ponte decorativa.
segment=next(s for s in r35['galleries']['segments'] if s['name']=='Palácio')
oldp=Vector(segment['origin_world']);oldu=Vector(segment['along_world']);oldn=Vector(segment['outward_world'])
newp=S@Vector((center+5.8,3.8,oldp.z));newu=S.col[0].xyz;newn=S.col[1].xyz
F=Matrix(((oldu.x,oldn.x,0,oldp.x),(oldu.y,oldn.y,0,oldp.y),(0,0,1,oldp.z),(0,0,0,1)))
T=Matrix(((newu.x,newn.x,0,newp.x),(newu.y,newn.y,0,newp.y),(0,0,1,newp.z),(0,0,0,1)))@F.inverted()
gallery_names=[n for n in r34['galleries']['created_objects']+r35['created_objects'] if '| Palácio |' in n and n.startswith(('GAL ','COLLISION '))]
gallery_names+=['COLLISION R34 | Palácio | Laje superior']
for name in dict.fromkeys(gallery_names):
    o=scene.objects[name];before=sig(o);o.data=o.data.copy();o.data.transform(wm(o).inverted()@T@wm(o))
    o['boas_revision']='R30B.36';o['r36_connection_control']='Face terminal do bastião curvo: centro + 5.8, profundidade 3.8 no referencial arquitetônico.'
    o['r36_world_correction_matrix']=json.dumps([list(row) for row in T]);o['classification']='ADAPT_LOCAL';o['reference_status']='partial'
    changes[name]={'before':before,'after':sig(o)};r['protected_signatures'].pop(name,None)
newsegment={**segment,'origin_world':list(newp),'along_world':list(newu),'outward_world':list(newn),'connection_status':'joined_to_curved_terrace','classification':'ADAPT_LOCAL','placement_status':'photo_relative_candidate','reference_measurements':None}

# O vão fica dentro do terraço: recuo da borda frontal e folga em ambos os lados.
stairy=30.;sw=1.35;startx=center-7.8;endx=center;hole=(center-3.80,center+1.20,stairy-sw/2-.30,stairy+sw/2+.30)
g=G()
for a,b in ((x0,hole[0]),(hole[1],x1)):g.box(((a+b)/2,(back+front)/2,roof-.20),(b-a,front-back,.40))
for a,b in ((back,hole[2]),(hole[3],front)):g.box(((hole[0]+hole[1])/2,(a+b)/2,roof-.20),(hole[1]-hole[0],b-a,.40))
replace('RIO R36 | Laje superior da colunata',g);replace('COL R36 | Laje superior da colunata',g)
g=G();count=30;going=(endx-startx)/count;rise=(roof-floor)/count
for j in range(count):g.box((startx+(j+.5)*going,stairy,floor+(j+1)*rise-.11),(going,sw,.22))
replace('RIO R36 | Escada interna da colunata',g)
g=G();g.box((endx+.60,stairy,roof-.13),(1.20,sw,.26));replace('RIO R36 | Patamar da escada interna',g)
g=G();a=(startx,stairy-sw/2,floor-.22);b=(endx,stairy-sw/2,roof-.22);c=(endx,stairy+sw/2,roof-.22);d=(startx,stairy+sw/2,floor-.22)
g.poly([a,b,c,d]);g.poly([(x,y,z-.22) for x,y,z in reversed([a,b,c,d])])
for p,q in zip((a,b,c,d),(b,c,d,a)):g.poly([p,(p[0],p[1],p[2]-.22),(q[0],q[1],q[2]-.22),q])
replace('RIO R36 | Laje inclinada da escada interna',g)
g=G();g.poly([(startx,stairy-sw/2,floor),(endx,stairy-sw/2,roof),(endx,stairy+sw/2,roof),(startx,stairy+sw/2,floor)]);g.box((endx+.60,stairy,roof-.08),(1.2,sw,.16));replace('COL R36 | Rampa interna e patamar',g)
guard=G()
def railing(g,a,b,z):
    a,b=Vector(a),Vector(b);u=(b-a).normalized();n=Vector((-u.y,u.x,0));L=(b-a).length
    for zz,w,hh in ((z+.12,.24,.18),(z+1.04,.30,.15)):g.box((a+b)/2+up*zz,(L,w,hh),(u,n,up))
    for j in range(max(2,round(L/.42))+1):
        p=a+(b-a)*j/max(2,round(L/.42));g.lathe((p.x,p.y,z+.20),[(.07,0),(.07,.1),(.043,.2),(.078,.38),(.056,.54),(.045,.69),(.065,.77)],8)
    for p in (a,b):g.box((p.x,p.y,z+.60),(.36,.36,1.20));g.box((p.x,p.y,z+1.24),(.46,.46,.13))
for y in (hole[2],hole[3]):railing(guard,(hole[0],y,0),(hole[1],y,0),roof)
railing(guard,(hole[0],hole[2],0),(hole[0],hole[3],0),roof)
replace('RIO R36 | Guarda da escada interna',guard)

# Escadaria do jardim recuada da borda, com o último lanço transversal antes
# da laje: não uma escada longa atravessando o guarda-corpo do terraço.
flights=[{'a':[x1-4,5,levels[0]],'b':[x1-4,13.2,levels[1]]},
         {'a':[x1-6.7,14.2,levels[1]],'b':[x1-6.7,22.4,levels[2]]},
         {'a':[x1-3,25.3,levels[2]],'b':[center,25.3,roof]}]
stairs=G();rails=G();width=1.7;ramps=[];links=[]
for j,f in enumerate(flights):
    a,b=Vector(f['a']),Vector(f['b']);d=b-a;d.z=0;L=d.length;u=d.normalized();n=Vector((-u.y,u.x,0));steps=math.ceil((a.z-b.z)/.18);rise=(a.z-b.z)/steps;going=L/steps
    # Dentes fechados num prisma serrilhado, com intradorso inclinado contínuo.
    points=[(0,a.z-.38)]
    for k in range(steps):points.extend([(k*going,a.z-k*rise),((k+1)*going,a.z-k*rise)])
    points.extend([(L,b.z),(L,b.z-.38)])
    sides=[]
    for offset in (-width/2,width/2):
        poly=[Vector((a.x,a.y,0))+u*t+n*offset+up*z for t,z in points];stairs.poly(poly);sides.append(poly)
    for p,q in zip(range(len(points)),list(range(1,len(points)))+[0]):stairs.poly([sides[0][p],sides[1][p],sides[1][q],sides[0][q]])
    for sign in (-1,1):
        aa=a+n*sign*width/2;bb=b+n*sign*width/2;rails.bar(aa+up,bb+up,.05,8)
        for k in range(11):p=aa+(bb-aa)*k/10;rails.bar(p,p+up,.03,8)
    ramp=G();ramp.poly([a-n*width/2,a+n*width/2,b+n*width/2,b-n*width/2]);ramps.append(ramp)
    f.update({'width_candidate_m':width,'steps':steps,'rise_candidate_m':rise,'going_candidate_m':going})
replace('RIO R36 | Escadas laterais do jardim',stairs);replace('RIO R36 | Guardas das escadas',rails)
# Patamares ligam os lanços pelas cotas de chegada; os dois caminhos estreitos
# permanecem dentro do jardim, sem ligação inventada à via pública.
walk=G();retaining=G();outer=G()
railing(outer,(x0,front,0),(x1,front,0),roof)
for x in (x0,x1):railing(outer,(x,back,0),(x,front,0),roof)
def landing(a,b,z,w=1.7):
    a,b=Vector((*a,0)),Vector((*b,0));u=(b-a).normalized();n=Vector((-u.y,u.x,0));L=(b-a).length
    walk.box((a+b)/2+up*(z-.15),(L,w,.30),(u,n,up));links.append({'a':list(a[:2]),'b':list(b[:2]),'z':z,'width':w})
landing((x1-4,13.7),(x1-6.7,13.7),levels[1]);landing((x1-6.7,22.9),(x1-3,22.9),levels[2]);landing((x1-3,22.9),(x1-3,25.3),levels[2]);landing((center,25.3),(center,27.6),roof)
for y,z,right in ((13.7,levels[1],x1-4),(22.9,levels[2],x1-6.7)):
    left=center-1.6;walk.box(((left+right)/2,y,z-.15),(right-left,1.05,.30));retaining.box(((left+right)/2,y+.70,z-1.2),(right-left,.42,2.4));railing(outer,(left,y+.75,0),(right-.90,y+.75,0),z)
replace('RIO R36 | Passeios dos patamares',walk);replace('RIO R36 | Contenções dos patamares',retaining);replace('RIO R36 | Balaustradas dos terraços',outer);replace('COL R36 | Passeios dos patamares',walk)
for j,g in enumerate(ramps):replace('COL R36 | Rampa jardim '+str(j+1),g)
assert all(sig(scene.objects[n])==s for n,s in r['protected_signatures'].items()),'Mudança fora do escopo'
r['access_connection_correction']={'classification':'ADAPT_LOCAL','reason':'Correção pedida pelo usuário: galerias encostam na lateral do terraço; escadas no interior, não no canto/guarda-corpo. Relocação arquitetônica relativa conforme foto, mantendo três arcos e sua extensão; sem deslocar geografia das vias ou footprint do palácio.','gallery_before':segment,'gallery_after':newsegment,'gallery_world_matrix': [list(row) for row in T],'gallery_join_local':[center+5.8,3.8],'updated_objects':changes,'garden_flights':flights,'garden_landings':links,'internal_stair':{'opening_local':list(hole),'start_local':[startx,stairy,floor],'end_local':[endx,stairy,roof],'width_candidate_m':sw,'outer_front_guard_setback_m':front-hole[3]},'dimensions_verified':None,'terrain_stage':'pending','visual_review':'pending'}
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
with Path(bpy.data.filepath).open('rb') as f:r['source_after']['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'saved':r['source_after'],'gallery_connection_local':r['access_connection_correction']['gallery_join_local'],'stairs_inside_terrace':True},ensure_ascii=False))
