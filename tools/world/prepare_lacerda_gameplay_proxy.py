"""Contrato temporário de gameplay B82; não modifica SSOT/referências B76–B81."""
import json, math, hashlib
from pathlib import Path
from lacerda_gameplay_proxy import local_point, validate_round_trip
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/lacerda-gameplay-proxy'


def main():
    context=json.loads((OUT/'b81_context.json').read_text(encoding='utf8'))
    cabin=next(x for x in context['context'] if x['name']=='FUNCIONAL | 3 piso')
    origin=[(cabin['min'][i]+cabin['max'][i])/2 for i in range(2)]
    floor=next(x for x in context['context'] if x['name']=='INFERIOR | piso do saguão')
    angle=math.atan2(floor['matrix'][1][0],floor['matrix'][0][0])
    upper=cabin['max'][2];lower=floor['max'][2]
    base=json.loads((ROOT/'docs/reports/blender/cairu-market-b81/route_candidate.json').read_text(encoding='utf8'))
    controls=base['control_nodes'][:7];points=[]
    for i,node in enumerate(controls):
        uv=local_point(node['blender_xy'],origin,angle)
        nearest=min(base['points'],key=lambda p:math.dist(p[:2],node['blender_xy']))
        z=lower if i<2 else nearest[2]-.015
        points.append([*uv,z])
    config={'schema':'boas/lacerda-gameplay-proxy-v1','status':'GAMEPLAY_PROXY','accuracy':'APPROXIMATE',
            'replacement_required':True,'production_ready':False,
            'historical_gate':'docs/LACERDA_CORRIDOR_B80.md',
            'guide_gate':'docs/LACERDA_LOWER_GUIDE_VISUAL_EVIDENCE_2026-10-06.md',
            'geographic_ssot':'world/geographic-reference.json','geographic_ssot_sha256':hashlib.sha256((ROOT/'world/geographic-reference.json').read_bytes()).hexdigest(),
            'source_file':'blender/salvador_lacerda_r30b81_cairu_colisao_e_rota_parcial.blend',
            'scene_file':'blender/salvador_lacerda_r30b82_gameplay_proxy.blend',
            'scene_name':'BOAS | GAMEPLAY_PROXY B82',
            'local_frame':{'origin_xy':origin,'angle':angle,'source':'B81: centro malha piso cabine 3 e orientação piso inferior; frame derivado, não outro SSOT'},
            'levels':{'upper':upper,'lower':lower},
            'cabin':{'length':3.4,'width':2.6,'height':2.7,'door_width':1.6},
            'spawn':[88.,4.77055194,upper],
            'upper_route':[[88.,4.77055194],[83.,4.77055194],[78.,4.77055194],[70.,0.],[63.,0.],[2.5,0.]],
            'lower_route':[[-3.,0.],[-3.,points[0][1]],*points],
            'floors':[], 'obstacles':[],
            'osm_control_nodes':controls,'topology_source':'docs/reports/blender/cairu-market-b81/route_candidate.json',
            'proxy_traffic_policy':'EXCLUSIVE_PEDESTRIAN_PROTOTYPE_NO_MOVING_TRAFFIC',
            'historical_traffic_permission':None,'historical_movement_enabled':False,
            'gameplay_movement_enabled':True,
            'notes':['Larguras, cabine, posição das guias, conector interno e soleiras são adaptações provisórias, não medidas reais.',
                     'Níveis locais preservados; sem corrigir divergência vertical histórica.',
                     'Via isolada para pedestres neste protótipo; não representa sinal verde real.',
                     'Sem referência temporária usada como textura; geometria substituível.']}
    def floor(id,center,size,angle=0.,slope=0.,source=None):
        config['floors'].append({'id':id,'center':center,'size':size,'angle':angle,'slope':slope,'source':source})
    def box(id,center,size,angle=0.,source=None):
        config['obstacles'].append({'id':id,'center':center,'size':size,'angle':angle,'source':source})
    floor('upper_walkway',[33.,0.,upper],[63.,6.],source='CALIBRADO | passarela piso 28.71 x 6.00m')
    floor('upper_lobby',[74.,0.,upper],[20.,18.],source='SUPERIOR | piso saguão')
    floor('tome_forecourt',[88.,4.77055194,upper],[8.,4.])
    floor('lower_lobby',[-7.95,1.5,lower],[12.5,14.],source='INFERIOR | piso do saguão')
    for i,(a,b) in enumerate(zip(points,points[1:])):
        length=math.dist(a[:2],b[:2]);heading=math.atan2(b[1]-a[1],b[0]-a[0])
        floor(f'osm_path_{i}',[(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2], [length+1.,3.],heading,(b[2]-a[2])/length,source=f'OSM nodes {controls[i]["id"]}/{controls[i+1]["id"]}')
        # Guarda-corpo encerra cada lado antes dos nós; não corta a passagem na curva.
        for side in (-1,1):
            if length<4:continue
            box(f'path_guard_{i}_{side}',[(a[0]+b[0])/2-side*1.57*math.sin(heading),(a[1]+b[1])/2+side*1.57*math.cos(heading),(a[2]+b[2])/2+.55],[length-3.,.12,1.1],heading)
    for i,p in enumerate(points):floor(f'osm_joint_{i}',p,[3.,3.])
    # Guarda-corpos da passarela e limites do saguão superior.
    for side in (-1,1):box(f'upper_guard_{side}',[33,side*3.06,upper+.55],[63,.12,1.1])
    for side in (-1,1):box(f'upper_lobby_side_{side}',[74,side*9.06,upper+1.35],[20,.12,2.7])
    # Abertura superior de 2,4 m junto ao spawn da praça.
    for lo,hi in [(-9.,3.57055194),(5.97055194,9.)]:box(f'upper_entry_wall_{lo}',[84.06,(lo+hi)/2,upper+1.35],[.12,hi-lo,2.7])
    box('upper_lobby_back',[64.,-6.,upper+1.35],[.12,6.,2.7]);box('upper_lobby_back2',[64.,6.,upper+1.35],[.12,6.,2.7])
    for side in (-1,1):box(f'forecourt_guard_{side}',[88,4.77055194+side*2.06,upper+.55],[8,.12,1.1])
    box('forecourt_end',[92.06,4.77055194,upper+.55],[.12,4.,1.1])
    # Guia original fica intacta na cena histórica. Novo par visível na camada proxy.
    box('queue_proxy_1',[-10.,-1.65,lower+.55],[4.,.08,1.1],source='INFERIOR | guia de fila')
    box('queue_proxy_2',[-10.,2.0,lower+.55],[4.,.08,1.1],source='INFERIOR | guia de fila.001')
    box('ticket_island_proxy',[-6.5,0,lower+.65],[2.2,2.,1.3],source='Foto Commons 20250721125707; aproximação de gameplay')
    for side in (-1,1):box(f'lower_lobby_side_{side}',[-7.95,1.5+side*7.06,lower+1.35],[12.5,.12,2.7])
    exit_y=points[0][1]+(points[1][1]-points[0][1])*(-14.2-points[0][0])/(points[1][0]-points[0][0])
    for lo,hi in [(-5.5,exit_y-1.6),(exit_y+1.6,8.5)]:box(f'lower_exit_wall_{lo}',[-14.26,(lo+hi)/2,lower+1.35],[.12,hi-lo,2.7])
    # Poço: paredes permanentes do PROXY; abertura somente na estação correspondente.
    for side in (-1,1):
        box(f'shaft_side_{side}',[0,side*1.62,(upper+lower)/2+1.4],[3.8,.20,upper-lower+3.])
    for landing,side in [('upper',1),('lower',-1)]:
        level=config['levels'][landing]
        for y in (-1.18,1.18):box(f'portal_jamb_{landing}_{y}',[side*1.82,y,level+1.35],[.24,.76,2.7])
        # Frente do poço preenchida fora do desembarque, sem recortar Hero histórico.
        for lo,hi in [(lower-.3,level),(level+2.5,upper+3.)]:
            if hi>lo:box(f'shaft_end_{landing}_{lo}',[side*1.90,0,(lo+hi)/2],[.20,3.4,hi-lo])
    target=ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json'
    target.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    result=validate_round_trip(config)
    (OUT/'round_trip_numeric.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'samples':len(result['trace']),'floors':len(config['floors']),'obstacles':len(config['obstacles'])}))


if __name__=='__main__':main()
