"""Sondar alturas reais da cena, sem pressupor datum absoluto nem alterar geografia."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];folder=root/'docs/reports/blender/lacerda-corridor';folder.mkdir(parents=True,exist_ok=True)
ground=bpy.data.objects['MVP | terreno corrigido | colisão estática']
trees={}
names=['MVP | terreno corrigido | colisão estática','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa','R30A5 | COLLISION | terrain proxy','INFERIOR | piso do saguão','SUPERIOR | piso saguão','NAV | saguão superior','NAV | passarela superior','CALIBRADO | passarela piso 28.71 x 6.00m','CALIBRADO | piso superior torre','CALIBRADO | piso desembarque baixo','FUNCIONAL | soleira inferior','INFERIOR R21 | passeio da entrada','INFERIOR R21 | rebaixo acessível','TÉRREO | laje','NAV | TÉRREO corredor central']
for name in names:
    ob=bpy.data.objects.get(name)
    if ob is not None:trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
def hits(x,y):
    output=[]
    for name,tree in trees.items():
        hit=tree.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),250)
        if hit[0]:output.append({'object':name,'z':hit[0].z,'normal':list(hit[1])})
    return output
anchors={}
for name in ['SUPERIOR | piso saguão','CALIBRADO | passarela piso 28.71 x 6.00m','FUNCIONAL | 3 piso','FUNCIONAL | 3 soleira superior','FUNCIONAL | 3 soleira inferior','INFERIOR | piso do saguão','INFERIOR R21 | rebaixo acessível','TÉRREO | laje','ACESSO | fachada Praça Cairu | verga']:
    ob=bpy.data.objects[name];v=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    p=Vector([sum(q[i] for q in v)/8 for i in range(3)]);anchors[name]={'center':list(p),'top':max(q.z for q in v),'surface_hits':hits(p.x,p.y),'visible':ob.visible_get()}
lines=[('upper',[12,0],[-1.38,7.12]),('bridge',[-1.38,7.12],[-47.02,47.68]),('lower_hall',[-49.63,50.12],[-59.13,57.88]),('cairu',[-59.13,57.88],[-126.49,154.29])]
profiles=[]
for label,a,b in lines:
    count=math.ceil(math.dist(a,b)/.5);samples=[]
    for i in range(count+1):
        p=[a[k]+(b[k]-a[k])*i/count for k in range(2)];samples.append({'xy':p,'hits':hits(*p)})
    profiles.append({'name':label,'samples':samples,'purpose':'Linha de inspeção entre componentes; não define rota aprovada'})
report={'anchors':anchors,'profiles':profiles,'ground_geometry_changed':False,'absolute_datum_verified':False,'profile_step_design_units':.5}
(folder/'height_profiles_b76.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'anchors':anchors,'profiles':[{'name':p['name'],'samples':len(p['samples'])} for p in profiles]},ensure_ascii=False))
