"""Malhas/encontros B94–B96 e cobertura real da face posterior corrigida."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-body-b96'
ns=runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':96})
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());before=json.loads((out/'before.json').read_text());rows={v['object']:v for v in before['rows']};bounds=ns['bounds'];wm=ns['wm'];inv=ns['inv'];scene=bpy.context.scene;delta=Vector(r['controls']['common_frame_delta'])
translation=[]
for row in r['changes']:
    name=row['object'];o=scene.objects[name];pts=[inv@wm(o)@v.co for v in o.data.vertices];old=[Vector(v) for v in rows[name]['vertices_local']]
    if 'BUTT_JOINT_CROP' in row.get('operation',''):continue
    assert len(pts)==len(old)
    error=max((p-a-delta).length for p,a in zip(pts,old));assert error<2e-5,(name,error)
    assert [list(f.vertices) for f in o.data.polygons]==rows[name]['faces'],name
    translation.append({'object':name,'max_common_delta_error_m':error,'topology_preserved':True})
wall='EDIFICIO | parede posterior alta';b=bounds(wall);roof='SUPERIOR | cobertura corpo elevado';rb=bounds(roof)
assert abs(b[0][0]-r['controls']['target_west_face_local_x'])<1e-4
assert abs(b[2][0]-r['controls']['target_wall_levels'][0])<1e-4 and abs(b[2][1]-r['controls']['target_wall_levels'][1])<1e-4
coverage=[]
for u in (.1,.3,.5,.7,.9):
    for v in (.04,.2,.4,.6,.8,.96):
        p=Vector((b[0][0]+(b[0][1]-b[0][0])*u,b[1][0]+(b[1][1]-b[1][0])*v))
        ns['support_check'](roof,p,rb[2][1],'REAR_WALL_ROOF_COVERAGE')
        coverage.append({'xy':list(p),'roof_top_z':rb[2][1]})
corners=[]
for name,direction in [('SUPERIOR | lateral corpo elevado',Vector((0.,1.,0.))),('SUPERIOR | lateral corpo elevado.001',Vector((0.,-1.,0.)))]:
    bb=bounds(name);overlap=[min(b[i][1],bb[i][1])-max(b[i][0],bb[i][0]) for i in range(3)];assert overlap[0]>.05 and overlap[2]>.05 and abs(overlap[1])<1e-4,(name,overlap)
    assert abs(bb[2][1]-rb[2][0])<1e-4,(name,'Topo da lateral não coincide com face inferior da cobertura')
    tree=ns['tree'](name);x=sum(b[0])/2;level=sum(b[2])/2;outside=bb[1][0]-.3 if direction.y>0 else bb[1][1]+.3
    hit=tree.ray_cast(Vector((x,outside,level)),direction,1.)
    assert hit[0] is not None,(name,x,level)
    corners.append({'sidewall':name,'overlap_xyz_m':overlap,'physical_ray_hit':list(hit[0]),'classification':'EXPECTED_CONTACT / BUTT_JOINT'})
q['body_checks']={'common_group_translation':translation,'rear_wall_limits':b,'roof_limits':rb,'roof_coverage_samples':coverage,'sidewall_contacts':corners,'xy_classification':'ADAPT_LOCAL / CANDIDATE_ENVELOPE_CONTINUITY','as_built_not_certified':True,'passed':True}
q['surface_checks']=ns['support'];q['scope']='Malhas e encontros dos corredores, cobertura e cantos posteriores. Não aprova instalação, implantação absoluta ou controller.'
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'revision':'B96','roof_coverage_samples':len(coverage),'sidewall_contacts':len(corners),'common_translation_objects':len(translation),'passed':True},ensure_ascii=False))
