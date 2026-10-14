"""B93: cotas/apoios da frente inferior na única sessão visível."""
import bpy,bmesh,json,hashlib,runpy,os,shutil
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parents[2]; out=root/'docs/reports/blender/lacerda-lower-structure-b93'
scene=bpy.context.scene; base=Path(bpy.data.filepath)
assert base.name=='salvador_lacerda_r30b92_ponte_estrutural_consolidada.blend'
assert scene.name=='SALVADOR | ESBOCO OFICIAL' and os.getpid()==16912
dest=root/'blender/salvador_lacerda_r30b93_estrutura_inferior_documental.blend'
assert not dest.exists() and not bpy.app.is_job_running('RENDER')
assert shutil.disk_usage(root).free>base.stat().st_size*1.5
catpath=root/'world/areas/mvp-centro-lacerda/blender-revisions.json'; cat=json.loads(catpath.read_text())
with base.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest==cat['authoring_source']['sha256']
cfg=json.loads((out/'controls.json').read_text()); rows={r['object']:r for r in json.loads((out/'before.json').read_text())['rows']}
ssot=hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest(); assert ssot==cfg['ssot_sha256']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py')); wm=h['world_matrix']; sig=h['signature']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']); inv=M.inverted()

def plain(v):
    if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
    if hasattr(v,'to_list'):return v.to_list()
    return v
proxy={o.name:{'signature':sig(o),'properties':{k:plain(v) for k,v in o.items()}} for o in bpy.data.collections['GAMEPLAY_PROXY | Lacerda B82'].objects}
terrain=sig(scene.objects['MVP | terreno corrigido | colisão estática'])
roof='INFERIOR | cobertura do saguão'; wallnames=['INFERIOR | parede lateral','INFERIOR | parede lateral.001']; core='CASCA | parede lateral'
mutate=[roof]+wallnames+[core]
# Identificados pela genealogia R30B02/03/07 e seus limites no inventário, não
# pela proximidade de algum elemento da cidade. Não são o proxy B82 nem colliders.
legacy=[r['object'] for r in rows.values() if r['visible'] and (
    r['object'].startswith('FACHADA INFERIOR |') or
    r['object'].startswith('LAC R30B03 | Cidade Baixa |') or
    r['object'].startswith('LAC R30B07 | Cidade Baixa |') or
    r['object'].startswith('LAC R30B02 | Rodape escuro | INFERIOR |') or
    r['object']=='CALIBRADO | marquise baixa')]
assert legacy and all(n not in proxy for n in mutate+legacy)
for n in mutate+legacy:assert sig(scene.objects[n])==rows[n]['signature'],n
assert all(rows[n]['bounds'][0][1]<-57 and rows[n]['bounds'][2][1]<13 for n in legacy)
protected={o.name:(o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None) for o in scene.objects if o.name not in mutate+legacy}

def stats(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    d={'vertices':len(bm.verts),'faces':len(bm.faces),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'signed_volume':bm.calc_volume(signed=True)}
    bm.free();return d
def check(mesh,label):
    q=stats(mesh)
    if q['degenerate_faces']:
        bm=bmesh.new();bm.from_mesh(mesh)
        (out/'staged-degeneracy.json').write_text(json.dumps({'object':label,'faces':[{'area':f.calc_area(),'points':[list(v.co) for v in f.verts]} for f in bm.faces if f.calc_area()<1e-9]},indent=2))
        bm.free()
    assert q['degenerate_faces']==q['nonmanifold_edges']==q['inconsistent_winding_edges']==0,(label,q)
    assert q['signed_volume']>0,(label,q);return q

def triangulate_boundary(p):
    # Ear clipping em double: não deixa diagonal passar por outro vértice
    # da borda. O triangulador float32 criava triângulo nulo no canto recuado.
    cross=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    pending=list(range(len(p))); result=[]
    while len(pending)>3:
        found=False
        for j,b in enumerate(pending):
            a=pending[j-1];c=pending[(j+1)%len(pending)]
            if cross(p[a],p[b],p[c])<=1e-10:continue
            if any(all(cross(p[u],p[v],p[k])>=-1e-10 for u,v in ((a,b),(b,c),(c,a))) for k in pending if k not in (a,b,c)):continue
            result.append((a,b,c));pending.pop(j);found=True;break
        assert found,'Contorno CAD não admite triangulação simples sem degeneração'
    assert cross(*(p[i] for i in pending))>1e-10
    result.append(tuple(pending))
    total=sum(cross(*(p[i] for i in t))/2 for t in result)
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1]))/2
    assert abs(total-area)<1e-8
    return result

top=cfg['levels']['roof_world']; floor=cfg['levels']['hall_floor_world']; thickness=cfg['levels']['roof_thickness_inherited_candidate']
oldtop=rows[roof]['bounds'][2][1]; oldbottom=rows[roof]['bounds'][2][0]; delta=top-oldtop
assert abs(delta-.08)<1e-4 and abs((oldtop-oldbottom)-thickness)<1e-4
assert abs(rows['INFERIOR | piso do saguão']['bounds'][2][1]-floor)<1e-4
assert abs(rows[core]['bounds'][2][0]-oldtop)<1e-4
buffers={}
for name in mutate:
    o=scene.objects[name]; mesh=o.data.copy(); tr=inv@wm(o); back=wm(o).inverted()@M
    for v in mesh.vertices:
        p=tr@v.co
        if name==roof:p.z+=delta
        elif name in wallnames:
            assert floor-1e-4<=p.z<=oldbottom+1e-4
            p.z=floor+(p.z-floor)*(top-thickness-floor)/(oldbottom-floor)
        else:
            if abs(p.z-oldtop)<1e-4:p.z=top
        v.co=back@p
    mesh.update();check(mesh,name);buffers[name]=mesh

added=[]; collection=bpy.data.collections['HERO | Lacerda | estrutura documental B88']
material=scene.objects[core].data.materials[0]
for row in cfg['pillars']:
    name='B93 | frente inferior | pilar documental '+row['id'].rsplit('_',1)[1]
    assert name not in scene.objects
    pts=list(row['points_local'])
    # Remover apenas subdivisões exatamente colineares do hatch, em double
    # antes da conversão float32. A envoltória física permanece idêntica.
    again=True
    while again:
        again=False
        for i,b in enumerate(pts):
            a=pts[i-1]; c=pts[(i+1)%len(pts)]
            if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<1e-10:
                pts.pop(i);again=True;break
    if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1]))<0:pts.reverse()
    p=[Vector((v[0],v[1],0.)) for v in pts]
    N=len(p); z0=rows['INFERIOR | piso do saguão']['bounds'][2][0]; z1=top-thickness
    vertices=[(v.x,v.y,z) for z in (z0,z1) for v in p]; faces=[]
    for indices in triangulate_boundary(pts):
        faces.extend([tuple(reversed(indices)),tuple(i+N for i in indices)])
    faces.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(material)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();check(mesh,name)
    added.append((name,mesh,row))

before={n:{'signature':sig(scene.objects[n]),'bounds':rows[n]['bounds'],'visible':scene.objects[n].visible_get()} for n in mutate+legacy}
for n,mesh in buffers.items():scene.objects[n].data=mesh
for n in mutate:
    o=scene.objects[n];o['boas_generated_revision']='R30B.93';o['boas_provenance_ids']=json.dumps(['derived:lacerda-lower-structure-b93']);o['replacement_required']=True;o['boas_production_ready']=False
    o['boas_roof_level_source']='SUCOP23 -53.17 relative to upper datum; architectural floor SUCOP12 -59.01'
    o['boas_pending_gate']='ABSOLUTE_SSOT_PLACEMENT_AND_AS_BUILT';o['accuracy']='PRINTED_RELATIVE_LEVELS_INHERITED_THICKNESS'
for n in legacy:
    o=scene.objects[n];o.hide_set(True);o.hide_render=True;o['boas_role']='SUPERSEDED_REFERENCE';o['boas_active_authoring']=False
    o['boas_superseded_reason']='Frente da implantação antiga aproximada; preservada integralmente. Planta12 define quatro apoios e novo contorno relativo; acabamento não migrado por escala visual.'
    o['boas_superseded_by']='B93 | frente inferior documental';o['boas_generated_revision']='R30B.93'
newrows=[]
for name,mesh,row in added:
    o=bpy.data.objects.new(name,mesh);o.matrix_world=M.copy();collection.objects.link(o)
    for k,v in {'boas_location_id':'elevador-lacerda','boas_role':'ARCHITECTURAL_MODEL_CANDIDATE','boas_architectural_domain':'LOWER_LOBBY','boas_generated_revision':'R30B.93','boas_provenance_ids':json.dumps(['derived:lacerda-lower-structure-b93']),'reference_status':'partial','accuracy':'PROJECT_VECTOR_XY_RELATIVE_Z_INHERITED_THICKNESS','replacement_required':True,'boas_production_ready':False,'boas_pending_gate':'ABSOLUTE_SSOT_PLACEMENT_AND_AS_BUILT','boas_cad_curve_ids':json.dumps(row['cad_curve_ids']),'boas_source_drawing':'sucop-2023-12','boas_physical_enabled':False}.items():o[k]=v
    newrows.append({'object':name,'signature':sig(o),'mesh':stats(mesh),'control':row['id']})
for n,state in protected.items():
    o=scene.objects[n];assert (o.data.as_pointer() if o.data else None,[list(r) for r in o.matrix_basis],o.hide_get(),o.hide_render,o.parent.name if o.parent else None)==state,n
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==terrain
for n,state in proxy.items():
    o=bpy.data.objects[n];assert sig(o)==state['signature'] and {k:plain(v) for k,v in o.items()}==state['properties'],n
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==ssot
changes=[{'object':n,'before':before[n],'after':{'signature':sig(scene.objects[n]),'visible':scene.objects[n].visible_get(),'mesh':stats(scene.objects[n].data)},'operation':'PRESERVE_AS_REFERENCE' if n in legacy else 'RECONCILE_DOCUMENT_ROOF_LEVEL'} for n in mutate+legacy]
# O runtime histórico permanece bloqueado; não aplicar novos sólidos a B82.
profilepath=root/'world/areas/mvp-centro-lacerda/corridor-slice.json'; profile=json.loads(profilepath.read_text()); invalidated=[]
for binding in profile.get('collision_bindings',[]):
    if binding.get('source') in mutate+legacy or binding.get('source_object') in mutate+legacy:
        binding['enabled']=False;binding['validation_status']='INVALIDATED_BY_RELATIVE_STRUCTURE_B93';invalidated.append(binding['object'])
report={'revision':'R30B.93','file':dest.relative_to(root).as_posix(),'parent_file':base.relative_to(root).as_posix(),'parent_sha256':digest,'pid':os.getpid(),'scene':scene.name,'changes':changes,'added':newrows,'protected_object_count':len(protected),'proxy_before':proxy,'terrain_signature':terrain,'ssot_sha256':ssot,'levels':cfg['levels'],'roof_delta_applied':delta,'legacy_front_preserved':len(legacy),'invalidated_bindings':invalidated,'terrain_samples_before':json.loads((out/'before.json').read_text())['terrain_samples'],'absolute_map_placement':'NEEDS_REVIEW','LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'production_ready':False,'reopened':False}
scene['lacerda_revision']='R30B.93 | estrutura inferior relativa documental; implantação/instalação pendentes';scene['boas_historic_movement_enabled']=False
runpy.run_path(str(root/'automation/blender/present_lacerda_map_b91.py'))
path=out/'application.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
profile.setdefault('revision_history',[]).append({'revision':'R30B.93','scope':'Cota documental da cobertura inferior e quatro apoios frontais; sem implantação/controller aprovado','movement_enabled':False,'evidence':path.relative_to(root).as_posix()})
profilepath.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
with dest.open('rb') as f:report['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={'file':report['file'],'revision':'R30B.93','parent_file':report['parent_file'],'sha256':report['sha256'],'scene':scene.name,'status':'architectural_structure_candidate','production_ready':False,'evidence':path.relative_to(root).as_posix(),'notes':'Cota inferior -53.17 e quatro apoios CAD12; implantação absoluta e instalação não aprovadas.'}
cat['revisions'].append(entry)
for key in ('authoring_source','validation_source'):cat[key]=entry.copy()
catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B93','file':report['file'],'sha256':report['sha256'],'roof_delta':delta,'pillars_added':len(newrows),'legacy_front_preserved':len(legacy),'production_ready':False},ensure_ascii=False))
