"""Ajustes finais de decalques e vidro do motorista; gravação do asset externo."""
import bpy,math,bmesh,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;assert s.name=='ONIBUS | Torino 31065 v04'
base=Path(bpy.data.filepath).parent;root=bpy.data.objects['TOR04_ROOT']
def depth(x,z,e,off=0):return (-6.045+.205*(abs(x)/1.25)**4+.145*max(0,z-1.12)+.08*max(0,.67-z)-off) if e<0 else (6.025-.19*(abs(x)/1.25)**4-.075*max(0,z-1.8)+off)
def assign(o,vs,fs):
    old=o.data;me=bpy.data.meshes.new(o.name+' final');me.from_pydata(vs,[],fs);me.update();me.materials.append(old.materials[0]);o.data=me
    for p in me.polygons:p.use_smooth=True
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
# Chin uses a strip, preserving its concave U profile without fan self-overlap.
xs=[-1.06,-.94,-.80,-.62,0,.62,.80,.94,1.06];tops=[1.48,1.43,1.33,1.262,1.259,1.262,1.33,1.43,1.48];bots=[1.365,1.245,1.17,1.105,1.105,1.105,1.17,1.245,1.365]
vs=[];fs=[]
for i in range(len(xs)-1):
    for j in range(16):
        t=j/16;u=(j+1)/16
        p=[]
        for q,heights in [(t,bots),(u,bots),(u,tops),(t,tops)]:
            x=xs[i]*(1-q)+xs[i+1]*q;z=heights[i]*(1-q)+heights[i+1]*q;p.append((x,depth(x,z,-1,.027),z))
        k=len(vs);vs.extend(p);fs.append((k,k+1,k+2,k+3))
assign(bpy.data.objects['TOR04 | Mascara inferior para-brisa'],vs,fs)
# Driver window corners are locally rounded, without spline overshoot.
pts=[(-5.73,1.66),(-5.59,2.50),(-5.42,2.625),(-4.67,2.625),(-4.60,2.56),(-4.60,1.82),(-4.75,1.77)]
outline=[]
for i,p in enumerate(pts):
    p=Vector(p);a=Vector(pts[i-1])-p;b=Vector(pts[(i+1)%len(pts)])-p;q1=p+a.normalized()*min(.055,a.length*.3);q2=p+b.normalized()*min(.055,b.length*.3)
    for j in range(7):t=j/6;outline.append(tuple((1-t)**2*q1+2*(1-t)*t*p+t*t*q2))
cy=sum(y for y,z in outline)/len(outline);cz=sum(z for y,z in outline)/len(outline);inner=[(cy+(y-cy)*.94,cz+(z-cz)*.94) for y,z in outline];N=len(outline)
assign(bpy.data.objects['TOR04 | Motorista moldura'],[(1.272,y,z) for y,z in outline+inner],[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)])
assign(bpy.data.objects['TOR04 | Motorista vidro'],[(1.278,cy,cz)]+[(1.278,y,z) for y,z in inner],[(0,1+i,1+(i+1)%N) for i in range(N)])
# Use exact reference pixels only for small painted labels whose typography is visible.
reference=Path(REFERENCE_IMAGE)
img=bpy.data.images.load(str(reference),check_existing=True);img.pack();img.name='TOR04 | Concept fornecido - referência de pintura'
ma=bpy.data.materials.new('TOR04 | Sinalização do concept');ma.use_nodes=True
p=next(n for n in ma.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=ma.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Linear';ma.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.68
Y=lambda u:6-(u-26)*12/1084
for name,sign,rect,cy,cz in [('Aviso cidade lado portas',-1,(627,153,660,191),Y(643.5),1.36),('Municipal lado portas',-1,(94,175,127,199),Y(110.5),1.13),('Aviso cidade lado motorista',1,(558,453,590,488),-Y(574),1.32),('Municipal lado motorista',1,(1035,464,1069,491),-Y(1052),1.13)]:
    u0,v0,u1,v1=rect;w=(u1-u0)*12/1084;h=(v1-v0)*.0117;vs=[(sign*1.285,cy+sign*x,cz+z) for x,z in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,1,2,3)]);me.materials.append(ma);uv=me.uv_layers.new(name='UV concept')
    for loop,coord in zip(uv.data,[(u0/1400,1-v1/646),(u1/1400,1-v1/646),(u1/1400,1-v0/646),(u0/1400,1-v0/646)]):loop.uv=coord
    o=bpy.data.objects.new('TOR04 | '+name,me);bpy.data.collections['TOR04 | ACABAMENTOS'].objects.link(o);o.parent=root;o['reference_usage']='Imagem fornecida para esta modelagem; redistribuição pendente de verificação'
# Pack the font used for labels, so the .blend remains portable.
for font in bpy.data.fonts:
    if font.filepath and font.filepath!='<builtin>':
        try:font.pack()
        except RuntimeError:pass
notes=bpy.data.texts.get('TOR04 | NOTAS DE MODELAGEM')
notes.write('\nV04: carroceria com vãos reais; laterais redesenhadas conforme as quatro vistas; vidro frontal/traseiro com curvatura e contorno corrigido; 3 portas com 6 folhas e pivôs, frames 1/35/65/120; rodas detalhadas com pneus, sulcos, aros vazados, cubos e fixações. Poses de abertura comparadas visualmente no Blender. Medidas proporcionais e cinemática interpretada: o concept não fornece cotas ou desenho mecânico interno. Interior v03 preservado em coleção própria.\n')
s.frame_set(1);s.display.shading.show_shadows=False;s.display.shading.show_cavity=False
s.camera.location=(-13.5,-17.5,6.2);s.camera.rotation_euler=(Vector((0,0,1.48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=14.25
s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.view_settings.view_transform='AgX'
for o in s.objects:
    if o.type=='LIGHT':o.data.energy=650
s.render.filepath=str(base/'reviews_torino_v04'/'exterior_material_final.png')
target=base/'onibus_torino_31065_v04_exterior.blend'
assert not target.exists(),'Preservar arquivo de entrega existente'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
bpy.ops.render.render(write_still=True)
print(json.dumps({'arquivo':str(target),'preview':s.render.filepath,'scene':s.name}))
