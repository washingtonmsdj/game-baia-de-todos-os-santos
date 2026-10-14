"""Modelo arquitetônico relativo das pranchas 12/17; não substitui o SSOT."""
import json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'docs/reports/blender/lacerda-massing-b88';out.mkdir(parents=True,exist_ok=True)
upper=json.loads((root/'docs/reports/blender/lacerda-layout-b86/layout_source.json').read_text())
scale=upper['scale_pdf_units_per_m'];anchor=upper['placement']['drawing_anchor']
def local(p):return [5.5+(p[0]-anchor[0])/scale,-(p[1]-anchor[1])/scale]
def area(p):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(p,p[1:]+p[:1])))/2
# Contorno EXTERNO da torre nova. Interrupções de portas em planta são unidas
# somente para registrar a envoltória exterior, nunca como prova de instalação.
new_core=[[903.84,789.52],[947.40,802.48],[945.48,808.96],[976.92,818.32],[978.96,811.72],[1022.16,824.56],[1020.,832.24],[1027.08,834.28],[1014.24,877.48],[1005.60,874.84],[1001.88,887.20],[989.16,883.48],
 [988.44,931.12],[985.92,940.],[994.20,942.52],[981.36,986.08],[972.60,983.44],[969.96,992.32],[957.60,988.72],
 [956.76,1036.36],[952.80,1049.68],[961.20,1052.20],[948.48,1095.28],[941.64,1093.24],[939.72,1099.72],[896.52,1086.88],[898.20,1080.88],[866.16,1072.],[864.48,1078.],[821.16,1065.16],[823.44,1057.60],[816.48,1055.56],[829.32,1012.],[840.,1015.24],[843.96,1001.92],[857.04,1005.64],
 [870.,961.96],[856.92,958.12],[859.68,948.64],[849.36,945.64],[862.20,902.44],[873.,905.68],[875.64,896.92],[888.24,900.52],
 [901.08,856.84],[888.60,853.12],[891.84,842.20],[881.28,839.08],[894.12,795.76],[901.44,797.92]]
old_core=[[2109.,979.72],[2235.96,980.80],[2237.40,939.16],[2257.80,939.16],[2257.20,1018.48],[2248.56,1018.48],[2248.68,1026.88],[2229.72,1026.88],
 [2229.72,1148.92],[2248.68,1148.92],[2248.68,1155.52],[2257.08,1155.64],[2256.24,1195.60],[2109.12,1195.60],[2109.,1139.20],[2127.96,1139.20],[2127.96,1036.84],[2109.,1036.84]]
head=[[857.88,699.28],[1113.,772.],[1086.36,855.16],[1138.80,860.08],[1072.08,1085.32],[1058.88,1121.92],[1019.52,1122.16],[1002.96,1181.20],[987.60,1191.40],[732.,1119.52],[748.68,1045.48],[712.20,1021.96],[747.60,902.44],[796.20,766.],[829.08,775.72]]
# Linhas externas contínuas do corredor, separadas da galeria/torre.
bridge=[[1138.80,860.08],[1976.16,962.68],[1977.96,1195.60],[1072.08,1085.32]]
lower=[[545.04,534.28],[773.04,600.28],[769.56,611.44],[1284.48,764.32],[1266.12,888.04],[1299.36,898.48],[2120.88,1012.96],[2089.92,1144.12],[1273.20,1028.92],[1244.40,1032.52],[1214.76,1190.20],[1204.56,1182.52],[1011.48,1153.00],[1007.76,1172.92],[943.80,1173.88],[730.32,1109.80],[567.84,1084.84],[537.96,1105.72],[385.44,1081.12]]
tunnel=[[1299.36,898.48],[2120.88,1012.96],[2089.92,1144.12],[1273.20,1028.92]]
# Espinha do piso inferior: cota documental -59,01; permanece no datum da
# arquitetura atual, sem falsificar a altitude/instalação que está bloqueada.
data={'schema':'boas/lacerda-massing-reference-v1','source_ids':['source:lacerda-issue22-sucop-12','source:lacerda-issue22-sucop-17','source:lacerda-issue22-sucop-23'],
 'source_sha256':{str(n):hashlib.sha256((root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{n}.pdf').read_bytes()).hexdigest() for n in (12,17,23)},
 'parent_ssot':'world/geographic-reference.json','ssot_sha256':hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest(),
 'scale_controls':upper['scale_controls'],'pdf_units_per_m':scale,'drawing_to_architecture':{'origin_pdf':anchor,'origin_scene_local':[5.5,0.],'measurement_frame':'docs/reports/blender/lacerda-corridor/scene_b78.json','kind':'DOCUMENT_DERIVED_RELATIVE_ARCHITECTURE','ssot_registration_accepted':False,'absolute_xy_confidence':'CANDIDATE_EXISTING_UPPER_ACCESS'},
 'polygons':{},'levels':{'upper_walkable':70.12300872802734,'gallery_roof_project_offset':4.,'technical_roof_project_offset':14.,'lower_scene_floor_preserved':7.405999660491943,'lower_project_floor_offset':-59.01,'shaft_project_access_offset':-58.93,'lower_absolute_datum_status':'UNRESOLVED_B80_NOT_REINTERPRETED'},
 'installed_cabin_dimensions':None,'production_ready':False}
sources={'new_core':(17,[1682,1683,1684,1685],new_core),'old_core':(17,[1686,1687],old_core),'new_gallery':(17,[1078,1080,1085,1086,1090,1093,1095,1099],head),'bridge':(17,[1060,1068,1102,1116],bridge),'lower_floor':(12,[20,23,30,31,32,19,79],lower),'lower_tunnel':(12,[19,79],tunnel),'upper_floor':(17,[],upper['outline_pdf'])}
for k,(sheet,ids,p) in sources.items():
    q=[local(x) for x in p]
    data['polygons'][k]={'drawing_id':f'sucop-2023-{sheet}','cad_elements':ids,'points_pdf':p,'points_local':q,'area_m2':area(q),'confidence':'PROJECT_VECTOR_DERIVED','not_proven':['posição geográfica independente','alterações executadas após projeto 2023','dimensões dos ascensores atuais']}
dx,dy=bridge[1][0]-bridge[0][0],bridge[1][1]-bridge[0][1]
theta=math.atan2(-dy,dx)
# Eixo ortogonal da torre extraído de segmento externo permanente 1684.
tx,ty=947.40-903.84,-(802.48-789.52);tower_angle=math.atan2(ty,tx)
data['diagnostic']={'bridge_free_north_length_m':math.hypot(dx,dy)/scale,'bridge_free_south_length_m':math.dist(bridge[2],bridge[3])/scale,'bridge_angle_local_deg':math.degrees(theta),'new_tower_angle_local_deg':math.degrees(tower_angle),'relative_tower_bridge_angle_deg':math.degrees(tower_angle-theta)}
data['new_tower_basis']={'angle':tower_angle,'center_local':local([921.78,944.62]),'source_scene_center':[-62.813546,0.],'source_scene_size':[3.55,7.48]}
(out/'architectural-controls.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(data['diagnostic'],ensure_ascii=False))
