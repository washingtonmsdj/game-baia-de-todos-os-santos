"""Fecha evidência local do trecho; não aprova toda a cidade nem exporta."""
import bpy,json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];rp=root/'docs/reports/blender/conceicao_binding_r30b38.json';r=json.loads(rp.read_text())
assert r['validation']['visible_replay']['completed']
assert not r['validation']['terrain_body_clearance']['hits'],'Contato persiste; não fechar conferência local'
assert r['validation']['interpolated_missing_support']==0
path=bpy.context.scene.objects['GAMEPLAY | Conceicao | percurso parcial B38']
pts=[list(p.co[:3]) for p in path.data.splines[0].points]
r['validation']['planned_distance_before_clearance_m']=r['validation']['distance_xy_m']
r['validation']['distance_xy_m']=sum(math.dist(a[:2],b[:2]) for a,b in zip(pts,pts[1:]))
r['validation']['local_geometry_review']='Duas vistas locais conferidas. Bordas do pavimento ainda facetadas; não são aprovação visual de toda a via. Contato final do envelope corrigido por adaptação local registrada; curvas seguintes permanecem em revisão.'
r['collision_refinement']['unreliable_projection_policy']='Novos vértices de bordas sem apoio a ±0,5 m conservaram interpolação da face anterior; não foram projetados na pista superior. Nenhum preenchimento de solo ausente.'
r['collision_refinement']['subdivision_without_reprojection_count']=None
r['source_after']['sha256']=hashlib.file_digest((root/r['source_after']['file']).open('rb'),'sha256').hexdigest()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
(root/'artifacts/roads/r38/final_summary.json').write_text(json.dumps({'distance_m':r['validation']['distance_xy_m'],'body_hits':len(r['validation']['terrain_body_clearance']['hits']),'wheel_missing':r['validation']['interpolated_missing_support'],'replay':r['validation']['visible_replay'],'source_after':r['source_after']},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'local_candidate_review_finished':True,'full_route_approved':False}))
