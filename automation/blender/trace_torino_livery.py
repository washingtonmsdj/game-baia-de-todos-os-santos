"""Extrai somente os contornos da marca pintada do concept fornecido para a modelagem.
Uso: python automation/blender/trace_torino_livery.py CAMINHO_IMAGEM
Não altera a imagem; envia curvas vetoriais editáveis à janela Blender MCP 9876.
"""
import sys,json
import cv2
from tools.blendmcp.healthcheck import request
image=cv2.imread(sys.argv[1]);assert image is not None
assert image.shape[1]==1400, 'Usar concept original de 1400 pixels'
crop=image[150:191,660:800]
hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
mask=cv2.inRange(hsv,(12,95,70),(42,255,255))
contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
paths=[]
for y,row in enumerate(mask):
    start=None
    for x,value in enumerate(list(row)+[0]):
        if value and start is None:start=x
        if not value and start is not None:paths.append([start,x,y,y+1]);start=None
code='''import bpy,math,json
from mathutils import Matrix,Vector
s=bpy.context.scene
assert s.name=='ONIBUS | Torino 31065 v04'
paths=json.loads(DATA)
for o in list(s.objects):
 if o.name.startswith(('TOR04 | Integra lateral','TOR04 | Integra pintura vetorial')):bpy.data.objects.remove(o,do_unlink=True)
for sign,cy in [(-1,6-(730-26)*12/1084),(1,-(6-(476-26)*12/1084))]:
 vs=[];fs=[]
 for x0,x1,y0,y1 in paths:
  i=len(vs);vs.extend([((x-70)*.0108,(20.5-y)*.0108,0) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]);fs.append((i,i+1,i+2,i+3))
 cu=bpy.data.meshes.new('Integra desenho preenchido');cu.from_pydata(vs,[],fs);cu.update()
 o=bpy.data.objects.new('TOR04 | Integra pintura vetorial '+str(sign),cu);bpy.data.collections['TOR04 | ACABAMENTOS'].objects.link(o);o.parent=bpy.data.objects['TOR04_ROOT'];cu.materials.append(bpy.data.materials['TOR04 | Amarelo ouro'])
 o.location=(sign*1.29,cy,1.40);right=Vector((0,sign,0));up=Vector((0,0,1));normal=right.cross(up);o.rotation_euler=Matrix((right,up,normal)).transposed().to_euler()
 o['reference']='Contornos extraídos do concept do usuário; uso/licença pendente de verificação'
print('Marca Integra vetorial aplicada nas duas laterais')
'''.replace('DATA',repr(json.dumps(paths)))
print(request('127.0.0.1',9876,{'type':'execute_code','params':{'code':code}},60))
