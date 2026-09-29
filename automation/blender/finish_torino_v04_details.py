"""Acabamento de vidros/cabeceiras e comparação das portas, na sessão MCP."""
import bpy,math,bmesh
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v04'
def depth(x,z,end,off=0):
    return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)-off) if end<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8)+off)
def normal(x,z,end):
    e=.0001;dx=(depth(x+e,z,end)-depth(x-e,z,end))/(2*e);dz=(depth(x,z+e,end)-depth(x,z-e,end))/(2*e)
    return tuple(Vector((-end*dx,end,-end*dz)).normalized())
for name,end,offset in [('Dianteira vidro curvo',-1,.025),('Traseira vidro curvo',1,.025),('Letreiro eletronico alojamento',-1,.034)]:
    o=bpy.data.objects['TOR04 | '+name];old=o.data
    N=(len(old.vertices)-1)//8
    pts=[(v.co.x,v.co.z) for v in list(old.vertices)[-N:]]
    dense=[]
    for p,q in zip(pts,pts[1:]+pts[:1]):
        for j in range(8):t=j/8;dense.append((p[0]*(1-t)+q[0]*t,p[1]*(1-t)+q[1]*t))
    cx=sum(x for x,z in dense)/len(dense);cz=sum(z for x,z in dense)/len(dense);N=len(dense)
    vs=[(cx,depth(cx,cz,end,offset),cz)];fs=[]
    for k in range(1,25):
        for x,z in dense:
            xx=cx+(x-cx)*k/24;zz=cz+(z-cz)*k/24;vs.append((xx,depth(xx,zz,end,offset),zz))
    fs.extend((0,1+(i+1)%N,1+i) for i in range(N))
    for k in range(23):
        a=1+k*N;b=a+N;fs.extend((a+i,b+i,b+(i+1)%N,a+(i+1)%N) for i in range(N))
    me=bpy.data.meshes.new(name+' superficie densa');me.from_pydata(vs,[],fs);me.update();me.materials.append(old.materials[0]);o.data=me
    for p in me.polygons:p.use_smooth=True
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    me.normals_split_custom_set_from_vertices([normal(v.co.x,v.co.z,end) for v in me.vertices])
    for mod in o.modifiers:
        if mod.type=='SOLIDIFY':mod.use_rim=False

# Rings also follow the curvature, instead of bridging the arc with long flat faces.
for o in s.objects:
    if o.type!='MESH' or not o.name.startswith('TOR04 | '):continue
    if not any(k in o.name for k in ['Dianteira vedacao vidro','Traseira vedacao vidro','Dianteira filete vidro','Traseira filete vidro','Letreiro aro']):continue
    old=o.data;N=len(old.vertices)//2;end=1 if 'Traseira' in o.name else -1
    offset=.04 if 'Letreiro' in o.name else (.029 if 'filete' in o.name else .024)
    vs=[]
    for loop in [list(old.vertices)[:N],list(old.vertices)[N:]]:
        for p,q in zip(loop,loop[1:]+loop[:1]):
            for j in range(8):
                v=p.co.lerp(q.co,j/8);vs.append((v.x,depth(v.x,v.z,end,offset),v.z))
    N*=8;fs=[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    me=bpy.data.meshes.new(o.name+' curvatura');me.from_pydata(vs,[],fs);me.update();me.materials.append(old.materials[0]);o.data=me
    for p in me.polygons:p.use_smooth=True
    me.normals_split_custom_set_from_vertices([normal(v.co.x,v.co.z,end) for v in me.vertices])
    for mod in o.modifiers:
        if mod.type=='SOLIDIFY':mod.use_rim=False

# Body panel crease curves: subdivide to conform to the body, preventing embedded chords.
for o in s.objects:
    if o.type!='CURVE' or not o.name.startswith('TOR04 | '):continue
    if not any(k in o.name for k in ['Vinco','Junta para-choque','Grade frontal aleta','VW aro','VW V','VW W']):continue
    for sp in o.data.splines:
        pts=[p.co.copy() for p in sp.points];new=[]
        end=1 if pts[0].y>0 else -1
        for p,q in zip(pts,pts[1:]):
            off=abs(p.y-depth(p.x,p.z,end))
            for j in range(12):
                v=p.lerp(q,j/12);new.append((v.x,depth(v.x,v.z,end,max(.018,off)),v.z,1))
        new.append(tuple(pts[-1]));sp.points.add(len(new)-len(sp.points))
        for p,v in zip(sp.points,new):p.co=v

# Side door window split and instruction headers are part of each physical assembly.
# Review real motion in Blender: closed / partial / fully open.
s.render.engine='BLENDER_WORKBENCH';s.display.shading.show_cavity=False;s.display.shading.show_shadows=False
out=Path(bpy.data.filepath).parent/'reviews_torino_v04'
for name,loc,scale,res,frame in [('frente',(0,-20,1.55),3.9,(900,900),1),('traseira',(0,20,1.55),3.9,(900,900),1),('portas_meia_abertura',(-15,-10,6),14,(1700,850),35),('portas_abertas',(-15,-10,6),14,(1700,850),65)]:
    s.frame_set(frame);s.camera.location=loc;s.camera.rotation_euler=(Vector((0,0,1.55))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(1)
print('Vidros curvos refinados; vistas das portas geradas.')
