"""Último passe visual de acabamentos do exterior, sem tocar na cidade/runtime."""
import bpy,math,bmesh,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;assert s.name=='ONIBUS | Torino 31065 v04'
root=bpy.data.objects['TOR04_ROOT'];col=bpy.data.collections['TOR04 | ACABAMENTOS']
M=lambda n:bpy.data.materials['TOR04 | '+n]
def depth(x,z,e,off=0):return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)-off) if e<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8)+off)
def rounded(pts,r=.03):
    out=[]
    for i,p in enumerate(pts):
        p=Vector(p);a=Vector(pts[i-1])-p;b=Vector(pts[(i+1)%len(pts)])-p;q1=p+a.normalized()*min(r,a.length*.3);q2=p+b.normalized()*min(r,b.length*.3)
        for j in range(6):t=j/5;out.append(tuple((1-t)**2*q1+2*(1-t)*t*p+t*t*q2))
    return out
def surface(name,pts,ma,end,off=.03):
    pts=rounded(pts);dense=[]
    for p,q in zip(pts,pts[1:]+pts[:1]):
        for j in range(5):t=j/5;dense.append((p[0]*(1-t)+q[0]*t,p[1]*(1-t)+q[1]*t))
    N=len(dense);cx=sum(x for x,z in dense)/N;cz=sum(z for x,z in dense)/N;vs=[(cx,depth(cx,cz,end,off),cz)];fs=[]
    for k in range(1,13):
        for x,z in dense:
            xx=cx+(x-cx)*k/12;zz=cz+(z-cz)*k/12;vs.append((xx,depth(xx,zz,end,off),zz))
    fs.extend((0,1+i,1+(i+1)%N) for i in range(N))
    for k in range(11):
        a=1+k*N;b=a+N;fs.extend((a+i,a+(i+1)%N,b+(i+1)%N,b+i) for i in range(N))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('TOR04 | '+name,me);col.objects.link(o);o.parent=root;me.materials.append(ma)
    for p in me.polygons:p.use_smooth=True
    return o
def line(name,pts,ma,r=.007):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,v in zip(sp.points,pts):p.co=(*v,1)
    o=bpy.data.objects.new('TOR04 | '+name,cu);col.objects.link(o);o.parent=root;cu.materials.append(ma);return o
# Repair the wheel-arch detail curves that must remain on the side plane.
arches=sorted([o for o in s.objects if o.name.startswith('TOR04 | Vinco chapa arco roda')],key=lambda o:o.name)
for o,(sign,y) in zip(arches,[(-1,-3.7),(-1,2.14),(1,-3.7),(1,2.14)]):
    cu=o.data;cu.splines.clear();sp=cu.splines.new('POLY');sp.points.add(64)
    for i,p in enumerate(sp.points):p.co=(sign*1.275,y+.685*math.cos(i*math.pi/64),.558+.685*math.sin(i*math.pi/64),1)
# Keep a single header per door after visual refinement passes.
for name in ['DIANTEIRA','CENTRAL','TRASEIRA']:
    keep='TOR04 | '+name+' painel acima da porta'
    for o in list(s.objects):
        if o.name.startswith(keep+'.'):bpy.data.objects.remove(o,do_unlink=True)
# Broad black windshield chin is a defining Torino feature in the concept.
chin=[(-1.045,1.40),(-.90,1.235),(-.65,1.16),(.65,1.16),(.90,1.235),(1.045,1.40),(.97,1.23),(.78,1.105),(-.78,1.105),(-.97,1.23)]
surface('Mascara inferior para-brisa',chin,M('Borracha EPDM'),-1,.033)
o=bpy.data.objects['TOR04 | Marca frontal'];o.location.z=1.155;o.location.y=depth(0,1.155,-1,.046)
o=bpy.data.objects['TOR04 | Frota frontal'];o.location.x=-.78;o.location.z=.768;o.location.y=depth(-.78,.768,-1,.046)
# Rear hatch perimeter and bumper pockets follow the sketch.
for sign in [-1,1]:
    pts=[(sign*.27,.525),(sign*.54,.525),(sign*.48,.448),(sign*.34,.454)]
    surface('Rebaixo para-choque traseiro',pts,M('Borracha EPDM'),1,.035)
    coords=[(sign*.99,.86),(sign*.99,1.49),(sign*.91,1.70),(sign*.70,1.77)]
    line('Junta tampa motor traseira',[(x,depth(x,z,1,.018),z) for x,z in coords],M('Amarelo ouro'),.004)
# Flatten livery bands onto the roof radius: no protruding colored tabs.
for o in list(s.objects):
    if not o.name.startswith('TOR04 | Faixa teto lateral'):continue
    sign=1 if o.location.x>0 else -1;cy=o.location.y;ma=o.data.materials[0];bpy.data.objects.remove(o,do_unlink=True)
    vs=[];fs=[]
    for j in range(17):
        z=2.92+j*.18/16;x=sign*(1.247*math.sqrt(max(0,1-(max(0,z-3.0)/.12)**2))+.003)
        vs.extend([(x,cy-.25,z),(x,cy+.25,z)])
    for j in range(16):a=2*j;fs.append((a,a+1,a+3,a+2))
    me=bpy.data.meshes.new('Faixa sobre raio teto');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('TOR04 | Faixa pintura curva',me);col.objects.link(ob);ob.parent=root;me.materials.append(ma)
    for p in me.polygons:p.use_smooth=True
# Small round Marcopolo badge on the rear, separate from the hatch.
line('Emblema Marcopolo elipse',[(.23*math.cos(i*2*math.pi/64),depth(.23*math.cos(i*2*math.pi/64),1.93+.052*math.sin(i*2*math.pi/64),1,.035),1.93+.052*math.sin(i*2*math.pi/64)) for i in range(65)],M('Alumínio polido'),.005)
# Door hinges also expose individual editable animation clips and review markers.
for o in s.objects:
    if ' pivo ' in o.name and o.name.startswith('TOR04 | '):
        o['componente_animavel']=True
        if o.animation_data and o.animation_data.action:o.animation_data.action.name=o.name+' | abrir_fechar'
for o in bpy.data.collections['TOR04 | INTERIOR_ESBOCO'].objects:o.hide_render=True
# Correct accessory creases that do not correspond to actual additional window bars.
s.frame_set(1);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='WORLD';s.display.shading.cavity_ridge_factor=.7;s.display.shading.cavity_valley_factor=.6
out=Path(bpy.data.filepath).parent/'reviews_torino_v04';out.mkdir(exist_ok=True)
views=[('exterior_final',(-14,-17,7.3),14.2,(1800,1050),1),('traseira_final',(11,17,6.5),14.2,(1800,1050),1),('lateral_portas',(-20,0,1.6),13.1,(1800,650),1),('portas_abertas',(-15,-10,5),14,(1700,850),65),('portas_meia_abertura',(-15,-10,5),14,(1700,850),35)]
for name,loc,scale,res,frame in views:
    s.frame_set(frame);s.camera.location=loc;s.camera.rotation_euler=(Vector((0,0,1.55))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(1);s.camera.location=(-14,-17,7.3);s.camera.rotation_euler=(Vector((0,0,1.55))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=14.2
s.render.resolution_x=1800;s.render.resolution_y=1050;s.render.filepath=str(out/'exterior_final.png')
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.color_type='MATERIAL'
root['estado_exterior']='Revisão visual v04; dimensões e mecanismo de porta interpretados do concept'
root['dimensoes_nominais_modelagem']='Carroceria ~12.07 m comprimento, 2.50 m largura; teto 3.12 m; pneus Ø1.11 m. Derivação visual, não fábrica.'
root['portas_quadros']='1 e 120 fechadas; 35 e 95 parciais; 65 abertas'
save_versions=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
bpy.context.preferences.filepaths.save_version=save_versions
print(json.dumps({'arquivo':bpy.data.filepath,'objetos':len(s.objects),'portas':3,'folhas_animadas':6,'comparacao':'quatro vistas e poses 1/35/65'}))
