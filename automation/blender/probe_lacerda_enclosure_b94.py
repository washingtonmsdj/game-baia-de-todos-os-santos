"""Sondagem horizontal das envoltórias da ponte/galeria; não equivale a controller."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-enclosure-b95'
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b94_fechamentos_passarela_tunel.blend'
data=json.loads((out/'before.json').read_text());cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());z=cfg['levels']['upper_walkable']
rows={r['object']:r for r in data['rows']};trees={}
def tree(name):
    if name not in trees:
        r=rows[name];trees[name]=BVHTree.FromPolygons([Vector(p) for p in r['vertices_local']],r['faces'],epsilon=1e-7)
    return trees[name]
def area(p):return sum(a.x*b.y-a.y*b.x for a,b in zip(p,p[1:]+p[:1]))/2
bridge=[Vector(p) for p in cfg['polygons']['bridge']['points_local']];head=[Vector(p) for p in cfg['polygons']['new_gallery']['points_local']]
if area(head)<0:head.reverse()
opening=[i for i,a in enumerate(head) if min((a-bridge[0]).length,(a-bridge[3]).length)<1e-5 and min((head[(i+1)%len(head)]-bridge[0]).length,(head[(i+1)%len(head)]-bridge[3]).length)<1e-5];assert len(opening)==1
segments=[('BRIDGE_NORTH',bridge[0],bridge[1]),('BRIDGE_SOUTH',bridge[2],bridge[3])]
segments += [(f'NEW_GALLERY_{i}',a,head[(i+1)%len(head)]) for i,a in enumerate(head) if i!=opening[0]]
samples=[]
for label,a,b in segments:
    inward=Vector((-(b-a).y,(b-a).x)).normalized()
    if label.startswith('BRIDGE_') and area(bridge)<0:inward=-inward
    for t in (.08,.25,.5,.75,.92):
        p=a.lerp(b,t)
        for height in (.25,.55,.95,1.8,3.5):
            start=Vector((p.x-inward.x*.5,p.y-inward.y*.5,z+height));direction=Vector((inward.x,inward.y,0.));hits=[]
            for n,r in rows.items():
                bb=r['bounds']
                if not (bb[2][0]-1e-4<=start.z<=bb[2][1]+1e-4):continue
                if any(p[i]<bb[i][0]-.6 or p[i]>bb[i][1]+.6 for i in (0,1)):continue
                hit=tree(n).ray_cast(start,direction,1.)
                if hit[0] is not None:hits.append({'object':n,'distance_m':hit[3],'local_hit':list(hit[0])})
            hits.sort(key=lambda v:v['distance_m']);samples.append({'segment':label,'fraction':t,'height_above_floor':height,'hits':hits})
report={'file':data['file'],'scene':data['scene'],'samples':samples,'unclosed':[s for s in samples if not s['hits']],'scope':'Limites laterais CAD; ausência de hit é candidato, não bug automaticamente.'}
(out/'enclosure-before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'samples':len(samples),'unclosed':[{k:s[k] for k in ('segment','fraction','height_above_floor')} for s in report['unclosed']]},ensure_ascii=False))
