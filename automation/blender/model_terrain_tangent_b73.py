"""Aplicar B73 na única janela: continuidade local de tangente da encosta."""
import bpy,json,hashlib,runpy,shutil,numpy as np
from pathlib import Path
from array import array
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
cp=r/'world/areas/mvp-centro-lacerda/blender-revisions.json';cat=json.loads(cp.read_text(encoding='utf8'));src=cat['validation_source'];assert src['revision']=='R30B.72'
assert Path(bpy.data.filepath).resolve()==(r/src['file']).resolve()
assert hashlib.sha256((r/src['file']).read_bytes()).hexdigest()==src['sha256']
out=r/'blender/salvador_lacerda_r30b73_tangente_encosta_costura.blend';assert not out.exists()
assert shutil.disk_usage(r).free>(r/src['file']).stat().st_size*2
p=json.loads((r/'docs/reports/blender/terrain_tangent_b73_candidate.json').read_text(encoding='utf8'));assert p['finite'] and p['source']['sha256']==src['sha256']
assert p['metrics']['slope_discontinuity_after']['p95']<p['metrics']['slope_discontinuity_before']['p95'] and p['max_delta_z_m']<4.1
data=np.load(r/'artifacts/waterfront/terrain_tangent_b73.npz')
ob=s.objects['B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa'];partner=s.objects[ob['boas_collision_partner']]
xyz=np.array([v.co for v in ob.data.vertices],float);assert np.array_equal(xyz,data['xyz'])
sig=runpy.run_path(str(r/'automation/blender/component_fingerprint.py'))['signature']
prior=json.loads((r/'docs/reports/blender/city_seam_r30b72.json').read_text(encoding='utf8'))
protected_names=set(prior['protected_signatures'])|{n for n in prior['modified_after'] if n!=ob.name}
protected={n:sig(s.objects[n]) for n in protected_names};old=ob.data;me=old.copy();coords=xyz.copy();coords[:,2]=data['z']
assert np.array_equal(coords[data['locked']],xyz[data['locked']])
me.vertices.foreach_set('co',coords.astype(np.float32).ravel());me.update();me.calc_loop_triangles()
assert sum(t.area<1e-9 for t in me.loop_triangles)==0 and np.isfinite(coords).all()
ob.data=me;partner.data=me.copy()
for o in [ob,partner]:o['boas_revision']='R30B.73';o['boas_source_report']='docs/reports/blender/terrain_tangent_r30b73.json';o['boas_gameplay_approved']=False
changes=[n for n,old_sig in protected.items() if sig(s.objects[n])!=old_sig];assert not changes
s['boas_validation_revision']='R30B.73';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);sha=hashlib.sha256(out.read_bytes()).hexdigest()
report={'source_before':src,'source_after':{'file':out.relative_to(r).as_posix(),'revision':'R30B.73','sha256':sha},'candidate':p,'protected_signatures':protected,'protected_changes':changes,'modified_after':sig(ob),'collision_after':sig(partner),'locked_roads_sidewalks_preserved':True,'xy_changed':False,'topology_changed':False,'source_dem_changed':False,'source_reopened':False,'approved':False,'geographic_fit_verified':False,'source_core_degenerate_triangles_pending':94,'runtime_exported':False,'pending':['Georreferenciamento e datum ainda não validados','Larguras reais, bordas serrilhadas do pavimento e acabamento fora desta faixa','Altimetria original Aleph ausente; ajuste não é levantamento da encosta','Travessia física na engine e tráfego não validados']}
rp=r/'docs/reports/blender/terrain_tangent_r30b73.json';rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
entry={**report['source_after'],'status':'validation_candidate','parent_file':src['file'],'evidence':rp.relative_to(r).as_posix(),'notes':'Tangente local na costura da encosta; mesmas vias/XY e extremos; adaptação 8m não levantada, cidade permanece parcial.'}
for e in cat['revisions']:
 if e['file']==src['file']:e.update(status='superseded_validation',source_reopened=True,validation_evidence='docs/reports/blender/city_seam_r30b72_validation.json',local_geometry_checks_passed=True)
cat['revisions'].append(entry);cat['validation_source']=entry.copy();cp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
