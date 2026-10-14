"""Confere cotas, contornos e vazios da estrutura; sem certificar instalação."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[2]; out=root/'docs/reports/blender/lacerda-floors-b101'
ns=runpy.run_path(str(Path(__file__).with_name('validate_lacerda_corridors_b94.py')),init_globals={'BOAS_ENCLOSURE_REVISION':101})
r=json.loads((out/'application.json').read_text()); cfg=json.loads((out/'controls.json').read_text()); q=json.loads((out/'validation.json').read_text())
scene=bpy.context.scene; sig=ns['sig']; wm=ns['wm']; inv=ns['inv']; z=ns['z']; checks=[]; support=[]
for n,s in r['preserved_signatures'].items():assert sig(scene.objects[n])==s,n
for spec in cfg['floors']:
    o=scene.objects[spec['object']]; pts=[inv@wm(o)@v.co for v in o.data.vertices]; top=spec['top_z']
    actual=[Vector((v.x,v.y)) for v in pts if abs(v.z-top)<1e-4]
    error=max(min((Vector(v)-a).length for a in actual) for v in spec['outline_local'])
    assert error<3e-5,(o.name,error)
    assert abs(max(v.z for v in pts)-z-spec['printed_level_offset_m'])<1e-4
    assert abs(max(v.z for v in pts)-min(v.z for v in pts)-cfg['thickness_candidate_m'])<1e-4
    o.data.calc_loop_triangles()
    for tri in o.data.loop_triangles:
        p=[pts[i] for i in tri.vertices]
        if max(abs(v.z-top) for v in p)>1e-4:continue
        c=sum(p,Vector())/3; height=ns['surface_height'](o.name,Vector((c.x,c.y)),top)
        assert height is not None and abs(height-top)<1e-4,(o.name,c,height)
        support.append({'object':o.name,'xy':[c.x,c.y],'top_z':height})
    checks.append({'object':o.name,'printed_level_offset_m':spec['printed_level_offset_m'],
                   'scene_level_offset_m':max(v.z for v in pts)-z,'contour_max_residual_m':error,
                   'section_candidate_m':cfg['thickness_candidate_m'],'area_document_contour_m2':spec['area_m2']})
# Raios no volume projetado da escada da15: a laje nova não a tampa.
reg=json.loads((root/'docs/reports/blender/lacerda-structure-b99/controls.json').read_text())['registration']['15']['matrix_to_sheet17']
frame=json.loads((root/'docs/reports/blender/lacerda-massing-b88/architectural-controls.json').read_text())
def convert(p):
    x=reg[0][0]*p[0]+reg[0][1]*p[1]+reg[0][2]; y=reg[1][0]*p[0]+reg[1][1]*p[1]+reg[1][2]
    a=frame['drawing_to_architecture']['origin_pdf']; scale=frame['pdf_units_per_m']
    return Vector((5.5+(x-a[0])/scale,-(y-a[1])/scale))
notch=[convert(p) for p in cfg['stair_notch_pdf15']]; tree=ns['tree'](cfg['floors'][0]['object']); clear=[]
for u in (.05,.25,.5,.75,.95):
    for v in (.05,.25,.5,.75,.95):
        p=notch[0].lerp(notch[1],u).lerp(notch[3].lerp(notch[2],u),v)
        hit=tree.ray_cast(Vector((p.x,p.y,cfg['floors'][0]['top_z']+.1)),Vector((0.,0.,-1.)),.5)
        assert hit[0] is None,('STAIR_NOTCH_FILLED',list(p),hit)
        clear.append({'xy':list(p),'floor_over_stair':False})
# Cotas existentes: não assumir que nomes de objetos comprovam tamanho.
levels=[]
for name,offset,index in [
    ('INFERIOR | piso do saguão',-59.01,1),('INFERIOR | cobertura do saguão',-53.17,1),
    ('SUPERIOR | piso saguão',0.,1),('CALIBRADO | passarela piso 28.71 x 6.00m',-.03,1),
    ('SUPERIOR | cobertura saguão',4.,1),('CALIBRADO | passarela cobertura 28.71 x 6.00m',4.,1),
    ('TORRE | teto galeria',4.,1),('B99 | cidade alta | laje subsolo 01 área documentada',-4.97,1),
    ('B100 | cidade alta | laje administrativa 01',4.94,1),('B100 | cidade alta | laje administrativa 02',9.42,1),
    ('SUPERIOR | cobertura corpo elevado',14.,1),('TORRE | capeamento tecnico',14.,1),
    ('B100 | cidade alta | platibanda contorno completo',15.4,1)]:
    measured=ns['bounds'](name)[2][index]-z; residual=measured-offset
    assert abs(residual)<1e-4,(name,measured,offset)
    levels.append({'object':name,'source':'SUCOP23 níveis; camada de acabamento da ponte−0,03 herdada/candidata' if offset==-.03 else 'SUCOP23/18/19/20 níveis relativos impressos',
                   'offset_m':offset,'measured_offset_m':measured,'residual_m':residual,'kind':'PRINTED_RELATIVE_LEVEL' if offset!=-.03 else 'LEGACY_FINISH_THICKNESS_CANDIDATE'})
q.update(reopened=True,preserved_component_signatures=len(r['preserved_signatures']),floor_dimension_checks=checks,
         floor_surface_probes=support,stair_notch_probes=clear,existing_level_checks=levels,
         lower_datum_status='NEEDS_REVIEW_NOT_MOVED',absolute_ssot_registration_accepted=False,
         unknown_sections=cfg['not_proven'],scope='Pisos documentados dos subsolos e controle dimensional relativo. Sem certificar estrutura civil, instalação, escadas ou gameplay.')
# Manifesto dimensional único do modelo: valores documentais não são obtidos
# de rótulos legados, e envelopes de planos não viram dimensões do equipamento.
xy=[]
for key,name in [('new_core','CASCA | parede lateral'),('bridge','CALIBRADO | passarela piso 28.71 x 6.00m'),
                 ('new_gallery','TORRE | teto galeria'),('upper_floor','SUPERIOR | piso saguão')]:
    control=frame['polygons'][key]['points_local']
    o=scene.objects[name]; actual=[inv@wm(o)@v.co for v in o.data.vertices]
    error=max(min(math.hypot(a.x-p[0],a.y-p[1]) for a in actual) for p in control)
    assert error<4e-5,(key,error)
    xy.append({'part':key,'scene_object':name,'drawing_id':frame['polygons'][key]['drawing_id'],
               'source_type':'DOCUMENT_VECTOR_CONTOUR_SCALED_BY_PRINTED_CONTROLS',
               'contour_residual_m':error,'bounds_in_architecture_m':ns['bounds'](name),
               'edges_document_m':[math.dist(a,b) for a,b in zip(control,control[1:]+control[:1])],
               'not_an_installed_shaft_or_cabin_dimension':True})
manifest={'schema':'boas/lacerda-structural-dimensions-v1','revision':r['revision'],'source_file':r['file'],
          'parent_ssot':'world/geographic-reference.json','architectural_frame':'docs/reports/blender/lacerda-corridor/scene_b78.json',
          'relative_levels':levels+checks,'document_contours':xy,
          'upper_body_controls':'docs/reports/blender/lacerda-upper-body-b100/controls.json',
          'basement_controls':'docs/reports/blender/lacerda-structure-b99/controls.json',
          'floor_controls':r['controls_file'],'relative_dimension_pass':'PASS_FOR_LISTED_CONTROLS',
          'complete_model_certified':False,'physical_connections_of_subsolo03':'NEEDS_REVIEW',
          'unknown_dimensions':cfg['not_proven'],'production_ready':False}
(out/'dimensions.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
q['xy_document_checks']=xy
(out/'validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects_checked':q['objects_checked'],'preserved':len(r['preserved_signatures']),
                  'floor_probes':len(support),'clear_stair_probes':len(clear),'existing_levels':len(levels),'reopened':True}))
