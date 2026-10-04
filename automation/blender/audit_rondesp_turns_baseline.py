"""Verifica curvas de ligação da rede, incluindo raio e quatro apoios."""
import bpy,json,math,numpy as np
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
audit=json.loads((r/'docs/reports/blender/rondesp_network_audit_b38.json').read_text(encoding='utf8'))
g=json.loads((r/c['staging']['roads']).read_text(encoding='utf8'));edges={e['id']:e for e in g['edges']}
terrain=s.objects[c['export']['road_object']];terrain.data.calc_loop_triangles();tri=list(terrain.data.loop_triangles)
ground=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in tri],all_triangles=True)
slots={i for i,m in enumerate(terrain.data.materials) if m and m.name in c['export']['road_materials']}
contacts=audit['vehicle_contacts_asset_local'];midy=(min(p[1] for p in contacts)+max(p[1] for p in contacts))/2
floor=audit['vehicle_floor_z'];minimum_radius=audit['wheelbase_measured_m']/math.tan(math.radians(35))
def hit(p):
    q,n,index,_=ground.ray_cast(Vector((p.x,p.y,p.z+2)),Vector((0,0,-1)),4)
    return q if q is not None and tri[index].material_index in slots and n.z>.65 else None
incoming=defaultdict(list);outgoing=defaultdict(list)
for row in audit['segments']:
    if row['issues'] or edges[row['edge_id']].get('access')=='restricted':continue
    e=edges[row['edge_id']];pp=row['samples'];a=Vector(pp[0]['point']);b=Vector(pp[-1]['point'])
    orientations=[]
    if e['direction'] in ['forward','both']:orientations.append((e['from'],e['to'],a,b))
    if e['direction'] in ['reverse','both']:orientations.append((e['to'],e['from'],b,a))
    for first,last,start,end in orientations:
        arc={'edge_id':e['id'],'first':first,'last':last,'start':start,'end':end}
        outgoing[first].append(arc);incoming[last].append(arc)
turns=[];counts=Counter()
for node,ins in incoming.items():
    for entry in ins:
        for exit in outgoing.get(node,[]):
            if entry['edge_id']==exit['edge_id']:continue
            issues=set();j1=entry['end'];j2=exit['start']
            if (j1-j2).length>.3:
                turns.append({'node_id':node,'from':entry['edge_id'],'to':exit['edge_id'],'issues':['junction_layer_or_binding_gap'],'approved':False});counts['junction_layer_or_binding_gap']+=1;continue
            f=(j1-entry['start']).to_2d().normalized();nf=(exit['end']-j2).to_2d().normalized();angle=math.acos(max(-1,min(1,f.dot(nf))))
            if angle>math.radians(155):continue
            arm=min(8.,(j1-entry['start']).to_2d().length*.4,(exit['end']-j2).to_2d().length*.4)
            begin=j1-Vector((f.x,f.y,0))*arm;end=j2+Vector((nf.x,nf.y,0))*arm;control=(j1+j2)/2
            steps=max(4,math.ceil((arm*2)/.25));poses=[];radii=[]
            for i in range(steps+1):
                t=i/steps;q=begin*(1-t)**2+control*2*(1-t)*t+end*t*t
                derivative=(control-begin)*2*(1-t)+(end-control)*2*t;second=(end-control*2+begin)*2
                f=derivative.to_2d().normalized();side=Vector((-f.y,f.x));cross=abs(derivative.x*second.y-derivative.y*second.x)
                radius=derivative.to_2d().length**3/cross if cross>1e-9 else 1e9;radii.append(radius)
                if radius<minimum_radius:issues.add('steering_radius_review')
                wheels=[]
                for px,py,pz in contacts:
                    xy=q.to_2d()+side*px-f*(py-midy);w=hit(Vector((xy.x,xy.y,q.z)))
                    if w is None:issues.add('wheel_outside_pavement_or_layer');break
                    wheels.append(w.z)
                if len(wheels)!=4:continue
                A=np.array([[1,px,-(py-midy)] for px,py,pz in contacts]);z,bank,grade=np.linalg.lstsq(A,np.array(wheels),rcond=None)[0]
                residual=float(np.max(np.abs(A@np.array([z,bank,grade])-np.array(wheels))))
                if residual>.08:issues.add('wheel_twist_review')
                if abs(bank)>.15:issues.add('crossfall_review')
                if abs(grade)>.30:issues.add('grade_review')
                up=Vector((-side.x*bank-f.x*grade,-side.y*bank-f.y*grade,1)).normalized();forward=Vector((f.x,f.y,grade)).normalized();right=up.cross(forward).normalized();up=forward.cross(right).normalized()
                rot=Matrix((right,-forward,up)).transposed().to_quaternion()
                poses.append({'location':[q.x-f.x*midy,q.y-f.y*midy,float(z-floor)],'rotation':list(rot),'radius_m':radius})
            for kind in issues:counts[kind]+=1
            turns.append({'node_id':node,'from':entry['edge_id'],'to':exit['edge_id'],'minimum_radius_m':min(radii),'issues':sorted(issues),'poses':poses,'approved':False})
report={'source_file':Path(bpy.data.filepath).relative_to(r).as_posix(),'turns':turns,'counts':dict(counts),'turn_connections_checked':len(turns),'geometry_clear_turns':sum(not t['issues'] for t in turns),'curve_adaptation':'ADAPT_LOCAL: arredondamento usa até 8 m ou 40% de cada braço existente; nenhum alargamento ou alteração do OSM. Trajetória candidata, não fonte geográfica.','minimum_radius_probe_m':minimum_radius,'steering_limit_probe_deg':35,'steering_limit_status':'candidate_not_factory_measurement','scope':'Ligações direcionais entre segmentos com apoio auditado; curva candidata sobre pista existente, sem deformar geografia. Obstáculos, varredura volumétrica e física pendentes.','approved':False}
(r/'artifacts/roads/rondesp/turns_baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:report[k] for k in ['turn_connections_checked','geometry_clear_turns','counts']}))