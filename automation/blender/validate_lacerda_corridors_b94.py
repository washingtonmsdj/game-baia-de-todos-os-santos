"""QA de persistência, malha e encontros dos fechamentos B94 na sessão visível."""
import bpy,bmesh,json,os,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];revision=globals().get('BOAS_ENCLOSURE_REVISION',94)
out=root/({94:'docs/reports/blender/lacerda-closure-b94',95:'docs/reports/blender/lacerda-enclosure-b95',96:'docs/reports/blender/lacerda-body-b96',98:'docs/reports/blender/lacerda-completion-b98',99:'docs/reports/blender/lacerda-structure-b99',100:'docs/reports/blender/lacerda-upper-body-b100',101:'docs/reports/blender/lacerda-floors-b101'}[revision])
r=json.loads((out/'application.json').read_text());before=json.loads((out/'before.json').read_text());scene=bpy.context.scene
closure=json.loads((root/'docs/reports/blender/lacerda-closure-b94/application.json').read_text()) if revision>=95 else r
enclosure=json.loads((root/'docs/reports/blender/lacerda-enclosure-b95/application.json').read_text()) if revision>=95 else None
assert Path(bpy.data.filepath).name==Path(r['file']).name and os.getpid()==r['pid'] and scene.name==r['scene']
proof=json.loads((root/'artifacts/blender-sessions/last-open.json').read_text())
assert proof['file']==r['file'] and proof['sha256']==r['sha256'] and proof['load_post_completed']
h=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'));sig=h['signature'];wm=h['world_matrix']
M=Matrix(json.loads((root/'docs/reports/blender/lacerda-corridor/scene_b78.json').read_text())['measurement_frame']);inv=M.inverted()
cfg=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
z=cfg['levels']['upper_walkable'];zl=z-59.01;rooflow=z-53.17
expected={}
for n in (88,89,90):
    report=json.loads((root/f'docs/reports/blender/lacerda-massing-b{n}/application.json').read_text())
    for row in report['changes']+report.get('added',[]):expected[row['object']]=row.get('after',row).get('signature',row.get('after',row))
for folder in ('lacerda-mesh-b91','lacerda-bridge-b92','lacerda-lower-structure-b93','lacerda-closure-b94')+(('lacerda-enclosure-b95',) if revision>=95 else ())+(('lacerda-body-b96',) if revision>=96 else ())+(('lacerda-vestibules-b97','lacerda-completion-b98') if revision>=98 else ())+(('lacerda-structure-b99',) if revision>=99 else ())+(('lacerda-upper-body-b100',) if revision>=100 else ())+(('lacerda-floors-b101',) if revision>=101 else ()):
    report=json.loads((root/f'docs/reports/blender/{folder}/application.json').read_text())
    for row in report['changes']+report.get('added',[]):expected[row['object']]=row.get('after',row).get('signature',row.get('after',row))
checks=[]
for name,state in expected.items():
    o=scene.objects[name];assert sig(o)==state,name
    bm=bmesh.new();bm.from_mesh(o.data);groups={}
    for f in bm.faces:
        key=tuple(sorted(tuple(round(float(c),6) for c in v.co) for v in f.verts));groups.setdefault(key,[]).append(f)
    d={'object':name,'visible':o.visible_get(),'degenerate_faces':sum(f.calc_area()<1e-9 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'duplicate_face_groups':sum(len(fs)>1 for fs in groups.values()),'signed_volume':bm.calc_volume(signed=True)}
    if d['visible']:assert d['degenerate_faces']==d['nonmanifold_edges']==d['inconsistent_winding_edges']==d['duplicate_face_groups']==0,(name,d)
    checks.append(d);bm.free()
changed={row['object'] for row in r['changes']};scoped_preserved=[]
for row in before['rows']:
    if row['object'] not in changed:
        assert sig(scene.objects[row['object']])==row['signature'],row['object'];scoped_preserved.append(row['object'])
assert sig(scene.objects['MVP | terreno corrigido | colisão estática'])==r['terrain_signature']
assert all(sig(bpy.data.objects[n])==s for n,s in r['proxy_signatures'].items())
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']

def tree(name):
    o=scene.objects[name];T=inv@wm(o);return BVHTree.FromPolygons([T@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],all_triangles=False,epsilon=1e-7)
trees={name:tree(name) for name in changed|{v['object'] for v in closure['changes']+closure['added']}}
support=[];wallchecks=[];portal=[]
surface_triangles={}
def surface_height(name,p,level):
    if name not in surface_triangles:
        o=scene.objects[name];T=inv@wm(o);o.data.calc_loop_triangles()
        v=[tuple(float(c) for c in T@vert.co) for vert in o.data.vertices]
        surface_triangles[name]=[[v[i] for i in tri.vertices] for tri in o.data.loop_triangles]
    hits=[]
    # Barycentros em double: BVH float produz erro Z perto de triângulos
    # compridos/estreitos. Não aumentar skin ou tolerância física por isso.
    for a,b,c in surface_triangles[name]:
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12:continue
        u=((b[1]-c[1])*(float(p.x)-c[0])+(c[0]-b[0])*(float(p.y)-c[1]))/den
        v=((c[1]-a[1])*(float(p.x)-c[0])+(a[0]-c[0])*(float(p.y)-c[1]))/den
        w=1.-u-v
        if min(u,v,w)>=-1e-7:
            hit=u*a[2]+v*b[2]+w*c[2]
            if level-.15<=hit<=level+.15:hits.append(hit)
    return max(hits) if hits else None
def support_check(name,p,level,kind):
    if name not in trees:trees[name]=tree(name)
    hit=trees[name].ray_cast(Vector((p.x,p.y,level+.15)),Vector((0.,0.,-1.)),.3)
    measured=surface_height(name,p,level)
    assert measured is not None and abs(measured-level)<1e-4,(name,list(p),measured)
    support.append({'object':name,'xy':list(p),'expected_z':level,'hit_z':measured,'bvh_float_z':hit[0].z if hit[0] else None,'method':'DOUBLE_BARYCENTRIC_TRIANGLE_SURFACE','kind':kind})
def wall_check(name,a,b,height,kind):
    d=(b-a).normalized();normal=Vector((-d.y,d.x))
    for t in (.1,.3,.5,.7,.9):
        p=a.lerp(b,t);start=Vector((p.x+normal.x*.6,p.y+normal.y*.6,height));direction=Vector((-normal.x,-normal.y,0.))
        hit=trees[name].ray_cast(start,direction,1.2)
        assert hit[0] is not None,(name,t,height)
        wallchecks.append({'object':name,'fraction':t,'height':height,'hit_distance_m':hit[3],'kind':kind})

# Os três materiais fecham a lateral em toda a altura; não há tampão no portal.
for side,segment in zip(('norte','sul'),closure['controls']['upper_returns']):
    a,b=map(Vector,segment)
    for band,height in [('peitoril',z+.35),('vidro',z+1.8),('verga',z+3.875)]:
        wall_check(f'B94 | saguão passarela | retorno {side} | {band}',a,b,height,'UPPER_RETURN')
    for t in (.1,.3,.5,.7,.9):
        p=a.lerp(b,t)+Vector((.09,0.))
        support_check('SUPERIOR | piso saguão',p,z,'RETURN_FLOOR_CONTACT')
        support_check('SUPERIOR | cobertura saguão',p,z+4.,'RETURN_ROOF_CONTACT')
bp=[Vector(v) for v in cfg['polygons']['bridge']['points_local']]
for t in (.08,.25,.5,.75,.92):
    p=bp[1].lerp(bp[2],t)
    support_check('LAC R30B | Passarela | piso paginado visual',p-Vector((.1,0.)),z,'BRIDGE_SIDE_OF_UPPER_PORTAL')
    support_check('SUPERIOR | piso saguão',p+Vector((.1,0.)),z,'LOBBY_SIDE_OF_UPPER_PORTAL')
    support_check('CALIBRADO | passarela cobertura 28.71 x 6.00m',p-Vector((.1,0.)),z+4.,'BRIDGE_ROOF_AT_UPPER_PORTAL')
    support_check('SUPERIOR | cobertura saguão',p+Vector((.1,0.)),z+4.,'LOBBY_ROOF_AT_UPPER_PORTAL')
    for dz in (.35,1.8,3.5):
        for row in closure['added']+([{'object':'SUPERIOR | posterior sobre passarela'}] if revision>=95 else []):
            if row['object'] not in trees:trees[row['object']]=tree(row['object'])
            hit=trees[row['object']].ray_cast(Vector((p.x-.45,p.y,z+dz)),Vector((1.,0.,0.)),.9)
            assert hit[0] is None,('Portal obstruído',row['object'],t,dz)
        portal.append({'fraction':t,'height_above_floor':dz,'new_returns_clear':True})

# Apoio em ambos os lados da seam e no conector, sem inferir abertura do poço.
lo=[Vector(v) for v in cfg['polygons']['lower_floor']['points_local']]
stn,sts=map(Vector,closure['controls']['station_face'])
for u in (.1,.3,.5,.7,.9):
    start=lo[6].lerp(lo[7],u);end=stn.lerp(sts,u)
    for v in (.05,.25,.5,.75,.95):
        p=start.lerp(end,v)
        support_check('INFERIOR | piso do saguão',p,zl,'LOWER_CONNECTOR_FLOOR')
        support_check('INFERIOR | cobertura do saguão',p,rooflow,'LOWER_CONNECTOR_ROOF')
    p=start-(end-start).normalized()*.05
    support_check('INFERIOR | piso do saguão',p,zl,'TUNNEL_SIDE_OF_SEAM')
    support_check('INFERIOR | cobertura do saguão',p,rooflow,'TUNNEL_SIDE_OF_SEAM')
for name,a,b in [('INFERIOR | parede lateral.001',lo[6],stn),('INFERIOR | parede lateral',sts,lo[7])]:
    for height in (zl+.15,(zl+rooflow-.25)/2,rooflow-.4):wall_check(name,a,b,height,'TUNNEL_TO_STATION_RETURN')
# Encontros verticais: raio já conferiu a superfície real; estes limites
# conferem a face inferior do teto e a continuidade entre as faixas.
def bounds(name):
    o=scene.objects[name];p=[inv@wm(o)@v.co for v in o.data.vertices];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
contacts=[]
for side in ('norte','sul'):
    names=[f'B94 | saguão passarela | retorno {side} | {s}' for s in ('peitoril','vidro','verga')]
    b=[bounds(n) for n in names]
    for name,gap in [('piso / peitoril',abs(b[0][2][0]-z)),('peitoril / vidro',abs(b[0][2][1]-b[1][2][0])),('vidro / verga',abs(b[1][2][1]-b[2][2][0])),('vidro / teto',abs(b[1][2][1]-(z+3.75)))]:contacts.append({'side':side,'relationship':name,'gap_m':gap})
for name in ('INFERIOR | parede lateral','INFERIOR | parede lateral.001'):
    b=bounds(name);contacts.extend([{'object':name,'relationship':'parede / piso','gap_m':abs(b[2][0]-zl)},{'object':name,'relationship':'parede / teto','gap_m':abs(b[2][1]-(rooflow-.25))}])
assert all(c['gap_m']<1e-4 for c in contacts)
profile=json.loads((root/'world/areas/mvp-centro-lacerda/corridor-slice.json').read_text())
assert scene['boas_historic_movement_enabled'] is False
assert profile['status']=='upper_ground_reconciled_shaft_blocked'
for name in r['invalidated_bindings']:
    assert any(b['object']==name and b['enabled'] is False for b in profile['collision_bindings']),name
limits=[]
if revision>=95:
    for name,key in [('SUPERIOR | parede lateral saguão.001','north_glazing_end'),('SUPERIOR | parede lateral saguão','south_glazing_end')]:
        b=bounds(name);control=enclosure['controls'][key];assert abs(b[0][1]-control[0])<1e-4,(name,b,control)
        limits.append({'object':name,'document_end_x':control[0],'mesh_end_x':b[0][1],'residual_m':abs(b[0][1]-control[0])})
    b=bounds('SUPERIOR | posterior sobre passarela');assert abs(b[2][0]-(z+3.75))<1e-4 and abs(b[2][1]-(z+4.))<1e-4
    for row in enclosure['archived']:
        o=scene.objects[row['object']];assert sig(o)==row['before']['signature'] and o.hide_get() and o.hide_render,o.name
q={'revision':f'R30B.{revision}','file':r['file'],'sha256':r['sha256'],'pid':os.getpid(),'scene':scene.name,'reopened':True,'objects_checked':len(checks),'visible_objects_checked':sum(c['visible'] for c in checks),'mesh_checks':checks,'protected_before_application':r['protected_object_count'],'protected_scoped_after_reopen':scoped_preserved,'surface_checks':support,'wall_checks':wallchecks,'portal_checks':portal,'structural_contacts':contacts,'connector_area_m2':closure['controls']['connector_area_m2'],'portal_width_m':(bp[2]-bp[1]).length,'enclosure_limits':limits,'ssot_preserved':True,'terrain_preserved':True,'proxy_b82_preserved':True,'invalidated_bindings':r['invalidated_bindings'],'LACERDA_VERTICAL':'BLOCKED_EXTERNAL_EVIDENCE','movement_enabled':False,'historic_witnesses':27,'production_ready':False,'scope':'Fechamentos e continuidade das superfícies arquitetônicas relativas; não aprova acesso ao poço, implantação absoluta, CCD ou controller.'}
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8');r['reopened']=True;(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:q[k] for k in ('objects_checked','visible_objects_checked','portal_width_m','connector_area_m2','reopened')},ensure_ascii=False))
