"""Sondagens do encontro arquitetura/praça; somente leitura da B93 visível."""
import bpy,json,runpy,os,re,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='salvador_lacerda_r30b93_estrutura_inferior_documental.blend' and scene.name=='SALVADOR | ESBOCO OFICIAL'
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text());controls=[]
for key in ('upper_floor','lower_floor','old_core','new_core'):
    p=cfg['polygons'][key]['points_local']
    controls.append({'id':key+'_center','xy':[sum(q[i] for q in p)/len(p) for i in (0,1)],'reason':'Centro do contorno documental relativo, não anchor geográfico'})
    if key in ('upper_floor','lower_floor'):
        controls.extend({'id':key+'_vertex_'+str(i),'xy':q,'reason':'Vértice do contorno documental relativo, sem correspondência absoluta presumida'} for i,q in enumerate(p))
controls.extend({'id':'existing_upper_entry_'+str(i),'xy':p,'reason':'Linha de entrada existente; candidato para sondagem da praça'} for i,p in enumerate(((5.5,0.),(8.,0.),(10.,0.),(12.,0.),(15.,0.))))
deps=bpy.context.evaluated_depsgraph_get();candidates=[];bvhs=[]
for o in scene.objects:
    if o.type!='MESH' or not o.visible_get():continue
    if not re.search(r'piso|praça|terreno|pavimento|calçada|laje|passeio|rebaixo|plataforma',o.name,re.I):continue
    transform=wm(o);pts=[inv@transform@Vector(v) for v in o.bound_box]
    bb=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    if bb[0][0]>20 or bb[0][1]<-85 or bb[1][0]>40 or bb[1][1]<-30:continue
    row={'object':o.name,'bounds':bb,'collections':[c.name for c in o.users_collection], 'properties':{k:v for k,v in o.items() if isinstance(v,(str,int,float,bool))}, 'selection_reason':'Nome/limite usados somente para inventário de superfícies, não associação física'}
    candidates.append(row);bvhs.append((row,transform,transform.inverted(),BVHTree.FromObject(o,deps)))
samples=[]
for control in controls:
    world=M@Vector((*control['xy'],150.));hits=[]
    for row,tr,back,bvh in bvhs:
        xy=control['xy'];bb=row['bounds']
        if not all(bb[i][0]-.001<=xy[i]<=bb[i][1]+.001 for i in (0,1)):continue
        origin=back@world;direction=(back.to_3x3()@Vector((0,0,-1))).normalized()
        # Todas as camadas verticais: não confundir teto com chão ou DEM.
        for _ in range(12):
            hit,normal,idx,dist=bvh.ray_cast(origin,direction,240.)
            if hit is None:break
            wp=tr@hit;wn=(tr.inverted().transposed().to_3x3()@normal).normalized()
            if wn.z>.5:hits.append({'object':row['object'],'world_z':wp.z,'normal':list(wn),'face':idx})
            origin=hit+direction*.005
    samples.append({**control,'hits':sorted(hits,key=lambda v:v['world_z'],reverse=True)})
out=root/'docs/reports/blender/lacerda-placement-b93';out.mkdir(parents=True,exist_ok=True)
data={'file':bpy.data.filepath,'scene':scene.name,'pid':os.getpid(),'ssot_sha256':hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest(),'surfaces':candidates,'samples':samples,'geometry_changed':False,'registration_accepted':False}
(out/'surfaces.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'candidate_surfaces':len(candidates),'sample_count':len(samples),'upper_entry':samples[-5:],'centers':[s for s in samples if s['id'].endswith('center')]},ensure_ascii=False))
