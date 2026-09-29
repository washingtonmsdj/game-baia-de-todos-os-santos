"""Acerto das superfícies após comparação visual das quatro vistas, via MCP."""
import bpy,bmesh,math
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v04'
root=bpy.data.objects['TOR04_ROOT'];groups={c.name.split(' | ')[-1]:c for c in s.collection.children}
M=lambda name:bpy.data.materials['TOR04 | '+name]
yellow=M('Amarelo ouro');white=M('Branco pintura');black=M('Borracha EPDM')
def depth(x,z,end):return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)) if end<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8))
def width(z):
    return 1.247*math.sqrt(max(.00001,1-(max(0,z-3.0)/.12)**2))-.06*(max(0,.52-z)/.12)**2
def make(name,vs,fs,ma,group='CARROCERIA',thick=.026):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('TOR04 | '+name,me);groups[group].objects.link(o);o.parent=root;me.materials.append(ma)
    if thick:m=o.modifiers.new('Chapa','SOLIDIFY');m.thickness=thick;m.offset=-1;m.use_rim=False
    for p in me.polygons:p.use_smooth=True
    return o
def repair(o,weld=False,outward=False):
    bm=bmesh.new();bm.from_mesh(o.data)
    if weld:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if outward:
        score=sum(f.normal.dot(f.calc_center_median()-Vector((0,0,1.5)))*f.calc_area() for f in bm.faces)
        if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.data.update()
for o in list(s.objects):
    if o.type=='MESH' and o.name.startswith('TOR04 | '):repair(o,'Painel lateral' in o.name,True)

# Rebuild end panels with scanline quad bands around the actual window opening.
for end,label in [(-1,'Dianteira'),(1,'Traseira')]:
    old=bpy.data.objects['TOR04 | '+label+' chapa envolvente'];bpy.data.objects.remove(old,do_unlink=True)
    gasket=bpy.data.objects['TOR04 | '+label+' vedacao vidro'];n=len(gasket.data.vertices)//2
    contour=[(v.co.x,v.co.z) for v in list(gasket.data.vertices)[:n]]
    low=min(z for x,z in contour);high=max(z for x,z in contour)
    def limits(z):
        z=max(low+1e-7,min(high-1e-7,z));xs=[]
        for (x1,z1),(x2,z2) in zip(contour,contour[1:]+contour[:1]):
            if min(z1,z2)<=z<max(z1,z2):xs.append(x1+(x2-x1)*(z-z1)/(z2-z1))
        return (min(xs),max(xs)) if xs else (0,0)
    zs=sorted(set([.407+i*(3.12-.407)/100 for i in range(101)]+[z for x,z in contour]))
    vs=[];fs=[]
    for za,zb in zip(zs,zs[1:]):
        if low<(za+zb)/2<high:
            la,ra=limits(za);lb,rb=limits(zb);strips=[(-width(za),la,-width(zb),lb),(ra,width(za),rb,width(zb))]
        else:strips=[(-width(za),width(za),-width(zb),width(zb))]
        for a,b,c,d in strips:
            nx=max(2,int(max(b-a,d-c)*22))
            for j in range(nx):
                x0=a+(b-a)*j/nx;x1=a+(b-a)*(j+1)/nx;x2=c+(d-c)*(j+1)/nx;x3=c+(d-c)*j/nx;k=len(vs)
                vs.extend([(x0,depth(x0,za,end),za),(x1,depth(x1,za,end),za),(x2,depth(x2,zb,end),zb),(x3,depth(x3,zb,end),zb)]);fs.append((k,k+1,k+2,k+3))
    o=make(label+' chapa envolvente',vs,fs,yellow);repair(o,True,True)
    # Join end corners to side shell, with smooth width transition into roof.
    for old in list(s.objects):
        if old.name.startswith('TOR04 | '+label+' retorno de canto'):bpy.data.objects.remove(old,do_unlink=True)
    for sign in [-1,1]:
        vs=[];fs=[]
        for j in range(71):
            z=.407+(3.12-.407)*j/70
            for i in range(7):
                t=i/6;x=sign*width(z)
                y=depth(sign*width(z),z,end)*(1-t)+end*5.745*t;vs.append((x,y,z))
        for j in range(70):
            for i in range(6):a=j*7+i;fs.append((a,a+1,a+8,a+7))
        o=make(label+' retorno de canto',vs,fs,yellow);repair(o,False,True)

# Close the band above each doorway; the glass cannot substitute for a header.
Y=lambda u:6-(u-26)*12/1084
for name,u0,u1 in [('DIANTEIRA',1077,984),('CENTRAL',624,519),('TRASEIRA',270,181)]:
    a,b=Y(u0),Y(u1);za=(286-70)*.0117;zb=(286-48)*.0117
    o=make(name+' painel acima da porta',[(-1.245,a,za),(-1.245,b,za),(-1.245,b,zb),(-1.245,a,zb)],[(0,1,2,3)],white if name=='CENTRAL' else yellow);repair(o,False,True)

# Thin, continuous roof belts instead of protruding separate box caps.
for o in s.objects:
    if o.name.startswith('TOR04 | Cinta superior'):
        sign=1 if o.location.x>0 else -1
        o.location.x=sign*1.222
        for m in o.modifiers:
            if m.type=='BEVEL':m.width=.007
        o.location.z=2.922;o.scale.z=.62
    if o.name.startswith('TOR04 | Faixa teto lateral'):
        o.location.x=math.copysign(1.245,o.location.x)
    if o.type=='MESH' and o.name.startswith('TOR04 | ') and 'vidro' in o.name.lower():
        for p in o.data.polygons:p.use_smooth=True
s.frame_set(1)
s.display.shading.show_cavity=False
s.display.shading.show_shadows=False
# Planar panels retain planar normals at their section edges.
for o in s.objects:
    if o.type=='MESH' and o.name.startswith('TOR04 | Painel lateral'):
        for p in o.data.polygons:p.use_smooth=False
    if o.type=='MESH' and o.name.startswith(('TOR04 | Dianteira','TOR04 | Traseira','TOR04 | Letreiro')):
        for m in o.modifiers:
            if m.type=='SOLIDIFY':m.use_rim=False
        # Analytic surface normals prevent interpolation pinching along scanline boundaries.
        if 'chapa envolvente' in o.name or 'retorno de canto' in o.name:
            end=-1 if 'Dianteira' in o.name else 1
            normals=[]
            for v in o.data.vertices:
                x,z=v.co.x,v.co.z;eps=.0001
                dx=(depth(x+eps,z,end)-depth(x-eps,z,end))/(2*eps)
                dz=(depth(x,z+eps,end)-depth(x,z-eps,end))/(2*eps)
                normals.append(tuple(Vector((-end*dx,end,-end*dz)).normalized()))
            o.data.normals_split_custom_set_from_vertices(normals)
roof=bpy.data.objects['TOR04 | Teto transversal abaulado']
for v in roof.data.vertices:v.co.z=3.0+.12*math.sqrt(max(0,1-(v.co.x/1.247)**2))
for o in s.objects:
    if o.name.startswith('TOR04 | Escotilha borracha'):o.location.z=3.124
    if o.name.startswith('TOR04 | Escotilha capa'):o.location.z=3.155
# Preserve the interior, but keep it out of exterior review renders.
groups['INTERIOR_ESBOCO'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
out=Path(bpy.data.filepath).parent/'reviews_torino_v04'
for name,loc,scale,res in [('lateral_portas',(-20,0,1.55),13.1,(1800,650)),('frente',(0,-20,1.55),3.9,(850,850)),('traseira',(0,20,1.55),3.9,(850,850)),('lateral_motorista',(20,0,1.55),13.1,(1800,650))]:
    s.camera.location=loc;s.camera.rotation_euler=(Vector((0,0,1.55))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=res;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('Superfícies corrigidas e quatro vistas geradas.')
