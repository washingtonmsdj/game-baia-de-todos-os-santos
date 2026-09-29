"""Refino das cabeceiras pelo concept Torino fornecido; execução ao vivo no MCP."""
import bpy, math
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v02',s.name
root=bpy.data.objects['BUS02_ROOT']; col=bpy.data.collections['BUS02 | EXTERIOR']
out=Path(bpy.data.filepath).parent/'assets'/'onibus_torino_31065_v03.blend'
assert not out.exists(),'Preservar revisão existente'
remove=['Mascara frontal amarela','Parachoque frontal branco','Testeira amarela','Para-brisa borracha','Para-brisa bipartido','Coluna frontal','Letreiro alojamento','Destino','Frota frente','Integra frente','Salvador frente','Mascara farol','Aro farol','Lente farol','Rebaixo neblina','Farol neblina','Braco limpador','Palheta','Entrada ar frontal','Placa moldura','Placa','Placa texto','Aro emblema','Raio emblema','Traseira inferior','Traseira superior','Vidro traseiro moldura','Vidro traseiro','Lanterna traseira base','Lente traseira','Parachoque traseiro','Veneziana traseira','Frota traseira','Canto frontal curvo','Torino frontal']
for o in list(s.objects):
    if o.name.startswith('BUS02 | ') and o.name[8:].split('.')[0] in remove:
        bpy.data.objects.remove(o,do_unlink=True)
def material(part):return bpy.data.materials['BUS02 | '+part]
yellow=material('Amarelo carroceria');dark=material('Moldura preta');glass=material('Vidro fumê');silver=material('Aluminio');chrome=material('Refletor');red=material('Lanterna vermelha');amber=material('Indicador âmbar');white=material('Branco perolado');blue=material('Azul acessibilidade');black=material('Borracha');lens=material('Lente farol')
def depth(x,z,end,offset=0):
    taper=.20*(abs(x)/1.25)**4
    if end<0:return -6.05+taper+.13*max(0,z-1.30)-offset
    return 6.045-taper-.045*max(0,z-2.25)+offset
def obj(name,v,f,ma,solid=0):
    me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
    o=bpy.data.objects.new('BUS03 | '+name,me);col.objects.link(o);o.parent=root;me.materials.append(ma)
    if solid:
        mod=o.modifiers.new('Espessura','SOLIDIFY');mod.thickness=solid;mod.offset=0
    return o
def smooth(points,n=5):
    out=[];m=len(points)
    for i in range(m):
        p0=Vector(points[(i-1)%m]);p1=Vector(points[i]);p2=Vector(points[(i+1)%m]);p3=Vector(points[(i+2)%m])
        for j in range(n):
            t=j/n
            p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
            out.append(tuple(p))
    return out
def patch(name,points,ma,end=-1,offset=.015,curved=True):
    p=smooth(points,4) if curved else points
    cx=sum(x for x,z in p)/len(p);cz=sum(z for x,z in p)/len(p)
    # Várias faixas evitam um n-gon plano sobre a cabeceira curva.
    v=[(cx,depth(cx,cz,end,offset),cz)];f=[]
    for k in range(1,17):
        q=k/16
        for x,z in p:
            xx=cx+(x-cx)*q;zz=cz+(z-cz)*q;v.append((xx,depth(xx,zz,end,offset),zz))
    N=len(p)
    for i in range(N):f.append((0,1+i,1+(i+1)%N))
    for k in range(15):
        a=1+k*N;b=a+N
        for i in range(N):f.append((a+i,b+i,b+(i+1)%N,a+(i+1)%N))
    if end>0:f=[tuple(reversed(q)) for q in f]
    o=obj(name,v,f,ma)
    for face in o.data.polygons:face.use_smooth=True
    return o
def line(name,points,ma,r=.008,end=-1,offset=.04,closed=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,(x,z) in zip(sp.points,points):p.co=(x,depth(x,z,end,offset),z,1)
    sp.use_cyclic_u=closed
    o=bpy.data.objects.new('BUS03 | '+name,cu);col.objects.link(o);o.parent=root;cu.materials.append(ma);return o
def txt(name,body,x,z,size,ma,end=-1):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0005
    o=bpy.data.objects.new('BUS03 | '+name,cu);col.objects.link(o);o.parent=root;cu.materials.append(ma)
    o.location=(x,depth(x,z,end,.07),z);o.rotation_euler=(math.pi/2,0,0 if end<0 else math.pi)
    return o
def rect(x,z,w,h):
    r=min(w,h)*.12
    return [(x-w/2+r,z-h/2),(x+w/2-r,z-h/2),(x+w/2,z-h/2+r),(x+w/2,z+h/2-r),(x+w/2-r,z+h/2),(x-w/2+r,z+h/2),(x-w/2,z+h/2-r),(x-w/2,z-h/2+r)]
def scalepts(p,k):
    cx=sum(x for x,z in p)/len(p);cz=sum(z for x,z in p)/len(p)
    return [(cx+(x-cx)*k,cz+(z-cz)*k) for x,z in p]
# Cascas contínuas, sem as frestas e os dois caixotes sobrepostos da v02.
for end,label in [(-1,'Frente'),(1,'Traseira')]:
    zs=[.40,.43,.50,.65,.85,1.15,1.5,1.9,2.3,2.65,2.9,3.04,3.12,3.18,3.21]
    widths=[1.12,1.19,1.23,1.25,1.25,1.25,1.25,1.25,1.245,1.24,1.225,1.19,1.12,1.01,.86]
    v=[];f=[];N=40
    for z,w in zip(zs,widths):
        for i in range(N+1):
            x=w*(-1+2*i/N);v.append((x,depth(x,z,end),z))
    for j in range(len(zs)-1):
        for i in range(N):
            a=j*(N+1)+i;f.append((a,a+1,a+N+2,a+N+1) if end<0 else (a+N+1,a+N+2,a+1,a))
    o=obj(label+' carenagem continua',v,f,yellow,.035)
    for p in o.data.polygons:p.use_smooth=True
    # Retorno dos cantos até as laterais existentes e fechamento até o teto.
    for sign in [-1,1]:
        v=[]
        for z,w in zip(zs,widths):v.extend([(sign*w,depth(sign*w,z,end),z),(sign*min(w,1.245),end*5.76,z)])
        obj(label+' retorno lateral',v,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(zs)-1)],yellow,.025)
    obj(label+' uniao teto',[(-.87,depth(-.87,3.21,end),3.21),(.87,depth(.87,3.21,end),3.21),(.95,end*5.70,3.225),(-.95,end*5.70,3.225)],[(0,1,2,3)],yellow,.025)
# Frente Torino: faixa negra larga, vidro único com divisão central fina.
wind=[(-1.105,2.70),(-1.145,2.57),(-1.15,1.63),(-1.02,1.38),(-.76,1.25),(.76,1.25),(1.02,1.38),(1.15,1.63),(1.145,2.57),(1.105,2.70)]
patch('Mascara negra para-brisa',scalepts(wind,1.07),dark,offset=.027)
patch('Para-brisa panoramico',wind,glass,offset=.055)
line('Montante central',[(0,1.27),(0,2.70)],black,.012,offset=.072)
display=[(-1.10,2.82),(-1.09,3.035),(-.98,3.08),(.98,3.08),(1.09,3.035),(1.10,2.82)]
patch('Letreiro negro curvo',display,black,offset=.032)
# Concept com letreiro apagado.
for x in [-1.04,1.04]:patch('Marcador superior',rect(x,3.04,.042,.026),white,offset=.049)
txt('Marca frontal','Marcopolo',0,1.20,.065,silver)
for sign in [-1,1]:
    line('Limpador braco',[(sign*.16,2.59),(sign*.66,1.76)],dark,.014,offset=.085)
    line('Limpador palheta',[(sign*.49,2.15),(sign*.85,1.64)],black,.019,offset=.087)
    # Farol alongado: ponta baixa interna, lente prateada acompanhando a máscara.
    p=[(sign*.73,.91),(sign*.90,.96),(sign*1.10,1.13),(sign*1.18,1.39),(sign*1.07,1.33),(sign*.88,1.10)]
    patch('Farol contorno alongado',p,dark,offset=.036)
    patch('Farol refletor alongado',scalepts(p,.87),chrome,offset=.050)
    patch('Farol lente alongada',scalepts(p,.76),lens,offset=.057)
    line('Farol divisao',[(sign*.90,1.03),(sign*1.07,1.19)],silver,.009,offset=.064)
    patch('Pisca frontal',[(sign*.76,.94),(sign*.87,.97),(sign*.94,1.03),(sign*.84,1.01)],amber,offset=.066)
    line('Vinco frontal',[(sign*1.17,.98),(sign*.85,.85),(sign*.59,.81)],yellow,.014,offset=.055)
patch('Grade frontal inferior',[(-.77,.77),(-.63,.59),(-.45,.54),(.45,.54),(.63,.59),(.77,.77)],black,offset=.028)
for z,w in [(.72,1.28),(.675,1.14),(.63,.98)]:line('Aleta grade',[(-w/2,z),(w/2,z)],dark,.008,offset=.047)
line('Junta parachoque',[(-1.17,.61),(-.89,.53),(-.65,.44),(.65,.44),(.89,.53),(1.17,.61)],dark,.003,offset=.025)
patch('Placa frente moldura',rect(0,.48,.48,.105),dark,offset=.04)
patch('Placa frente',rect(0,.48,.43,.078),white,offset=.052)
txt('Texto placa frente','PJR7J37',0,.48,.053,dark)
txt('Numero frente','31065',-.66,.87,.105,dark)
ring=[(.045*math.cos(i*2*math.pi/32),.895+.045*math.sin(i*2*math.pi/32)) for i in range(32)]
line('Emblema Torino',ring,silver,.006,offset=.06,closed=True)
# Traseira: vidro abaulado, tampa lisa e lanternas verticais contornadas.
rw=[(-1.055,2.86),(-1.085,2.66),(-1.08,2.18),(-.96,2.125),(0,2.18),(.96,2.125),(1.08,2.18),(1.085,2.66),(1.055,2.86),(0,2.91)]
patch('Borracha vidro traseiro',scalepts(rw,1.05),black,1,.024)
patch('Vidro traseiro abaulado',rw,glass,1,.049)
txt('Marca traseira','Marcopolo',0,1.94,.079,silver,1)
line('Vinco tampa superior',smooth([(-.99,2.02),(-.74,1.87),(0,1.82),(.74,1.87),(.99,2.02)],5),yellow,.016,1,.029)
line('Junta tampa motor',[(-.95,1.84),(-.91,.82),(-.65,.75),(.65,.75),(.91,.82),(.95,1.84)],dark,.003,1,.027)
for sign in [-1,1]:
    p=[(sign*1.18,1.58),(sign*1.07,1.44),(sign*1.025,1.22),(sign*1.02,.79),(sign*1.14,.72),(sign*1.19,.91)]
    patch('Lanterna traseira contorno',p,dark,1,.033)
    patch('Lanterna traseira vermelha',scalepts(p,.83),red,1,.049)
    line('Friso lanterna',[(sign*1.13,1.43),(sign*1.08,1.23),(sign*1.08,.87)],silver,.009,1,.058)
    patch('Re traseira',rect(sign*1.09,.84,.052,.057),white,1,.062)
    patch('Pisca traseiro',[(sign*1.09,1.18),(sign*1.15,1.25),(sign*1.15,1.12),(sign*1.09,1.06)],amber,1,.061)
    patch('Marcador traseiro superior',rect(sign*.99,3.045,.13,.037),red,1,.04)
line('Junta parachoque traseiro',[(-1.15,.69),(-.87,.65),(-.65,.50),(.65,.50),(.87,.65),(1.15,.69)],dark,.004,1,.027)
patch('Placa traseira rebaixo',[(-.46,.64),(-.31,.47),(.31,.47),(.46,.64)],dark,1,.03)
patch('Placa traseira',rect(0,.55,.43,.08),white,1,.047)
txt('Texto placa traseira','PJR7J37',0,.55,.052,dark,1)
txt('Numero traseira','31065',-.69,.84,.13,dark,1)
def access(x,z,end):
    patch('Sinal acessibilidade',rect(x,z,.22,.23),blue,end,.072)
    ring=[(x+.057*math.cos(i*2*math.pi/32),z-.026+.057*math.sin(i*2*math.pi/32)) for i in range(32)]
    line('Acessibilidade roda',ring,white,.006,end,.086,True)
    line('Acessibilidade corpo',[(x-.03,z+.056),(x-.019,z-.012),(x+.049,z-.012),(x+.073,z-.054)],white,.007,end,.088)
    patch('Acessibilidade cabeca',[(x-.038+.015*math.cos(i*2*math.pi/16),z+.079+.015*math.sin(i*2*math.pi/16)) for i in range(16)],white,end,.089,False)
access(.20,1.48,-1);access(.76,.92,1)
s.name='ONIBUS | Torino 31065 v03';s['asset_notes']='v03: cabeceiras refeitas conforme concept Torino, cascas curvas contínuas, faróis alongados, para-brisa arredondado, vidro traseiro e lanternas verticais. Demais partes e acessos preservados. Medidas artísticas aproximadas.'
s.frame_set(1)
bpy.context.view_layer.update()
bpy.data.libraries.write(str(out),{s},fake_user=True,compress=True)
# Prévia leve da geometria, sem render Cycles.
engine=s.render.engine;s.render.engine='BLENDER_WORKBENCH'
s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO';s.display.shading.show_shadows=True
s.render.resolution_x=650;s.render.resolution_y=760;s.render.resolution_percentage=100
cam=s.camera;prevloc=cam.location.copy();prevrot=cam.rotation_euler.copy();prevscale=cam.data.ortho_scale
for end,label in [(-1,'frente'),(1,'traseira')]:
    cam.location=(0,end*12,1.8);cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.9
    s.render.filepath=str(out.with_name('onibus_v03_'+label+'.png'));bpy.ops.render.render(write_still=True)
cam.location=prevloc;cam.rotation_euler=prevrot;cam.data.ortho_scale=prevscale;s.render.engine=engine
print('SALVO '+str(out))
