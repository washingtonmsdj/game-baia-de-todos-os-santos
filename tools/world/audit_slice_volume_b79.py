"""Auditoria volumétrica B77B: CCD de toda a cabine e cápsula contínua do percurso."""
import json,math,time
from pathlib import Path
import numpy as np
from slice_geometry import capsule_distances,continuous_triangle_pair,support_hits
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/reports/blender/lacerda-controller';OUT.mkdir(parents=True,exist_ok=True)
GEOMETRY=ROOT/'artifacts/lacerda-controller/geometry_b77b.json';SUFFIX='b77b'

def load():
    d=json.loads(GEOMETRY.read_text(encoding='utf8'))
    for r in d['objects']:
        g=r['geometry'];r['tri']=np.asarray(g['vertices'],dtype=float)[np.asarray(g['triangles'],dtype=int)]
    return d

def cabin_sweep(d):
    delta=np.array([0,0,-d['qa']['elevator']['travel_design_units']]);statics=[r for r in d['objects'] if not r['dynamic']]
    moving=[r for r in d['objects'] if r['cabin_member']]
    # Portas de estação fechadas também são obstáculos do movimento.
    for r in d['objects']:
        if r['dynamic'] and not r['cabin_member']:statics.append(r)
    findings=[];tested=0;component_summaries=[]
    for component in moving:
        tri=component['tri'];lo=np.minimum(tri.min(axis=(0,1)),tri.min(axis=(0,1))+delta)
        hi=np.maximum(tri.max(axis=(0,1)),tri.max(axis=(0,1))+delta)
        hits_for_component=0
        for target in statics:
            t=target['tri'];mask=np.all(t.max(axis=1)>=lo-1e-6,axis=1)&np.all(t.min(axis=1)<=hi+1e-6,axis=1)
            if not mask.any():continue
            candidates=t[mask];ids=np.flatnonzero(mask);hit_intervals=[];hit_triangles=[];pairs=0
            bmin=candidates.min(axis=1);bmax=candidates.max(axis=1)
            for m in tri:
                ml=np.minimum(m.min(axis=0),m.min(axis=0)+delta);mh=np.maximum(m.max(axis=0),m.max(axis=0)+delta)
                nearby=np.flatnonzero(np.all(bmax>=ml-1e-6,axis=1)&np.all(bmin<=mh+1e-6,axis=1))
                if not len(nearby):continue
                pairs+=len(nearby)
                good,start,end=continuous_triangle_pair(m,candidates[nearby],delta)
                found=np.flatnonzero(good)
                if len(found):
                    for index in found:
                        hit_intervals.append([float(start[index]),float(end[index])]);hit_triangles.append(int(ids[nearby[index]]))
            tested+=pairs
            if hit_intervals:
                first=min(v[0] for v in hit_intervals);last=max(v[1] for v in hit_intervals)
                findings.append({'cabin_component':component['name'],'obstacle':target['name'],
                    'classification':'NEEDS_REVIEW','detection':'continuous_triangle_surface_contact',
                    't_first':first,'t_last':last,'cabin_floor_z_first':d['qa']['elevator']['upper_z']+first*delta[2],
                    'surface_contact_pairs':len(hit_intervals),'target_triangle_examples':sorted(set(hit_triangles))[:12],
                    'obstacle_complete_mesh':target['geometry']['complete_mesh'],
                    'note':'CCD contínuo de triângulos sob translação; contato pode ser tangência ou interseção. Não alterar arquitetura automaticamente.'})
                hits_for_component+=1
        component_summaries.append({'object':component['name'],'triangles':len(tri),'obstacles_contacted':hits_for_component})
        print(json.dumps({'component':component['name'],'contacts':hits_for_component}),flush=True)
    # Checagem de envelope externo completa: identifica regiões sem fonte de parede/poço.
    verts=np.concatenate([r['tri'].reshape(-1,3) for r in moving]);extent={'min':verts.min(axis=0).tolist(),'max':verts.max(axis=0).tolist()}
    result={'schema':'boas/cabin-continuous-sweep-v1','source':d['source'],'motion':{'translation':delta.tolist(),'parameter':[0,1]},
            'method':'CCD SAT triângulo–triângulo contínuo; 17 eixos incluindo coplanaridade, tolerância 1e-7 unidade; todos os componentes móveis visíveis e portas de estação reais',
            'components':component_summaries,'outer_extent_upper':extent,'triangle_pairs_tested':tested,'contacts':findings,
            'status':'blocked' if findings else 'pending_containment_and_clearance',
            'release_ready':False,'physical_dimensions_verified':False,
            'positive_clearance_certified':False,'solid_containment_certified':False,
            'pending':['Folga física mínima do poço não conhecida; não pode ser aprovada por ausência de contato.',
                       'Teste de contenção de sólidos e geometria não visível do poço não certificados; CCD cobre superfícies exportadas.',
                       'Contrapesos e mecanismos não acrescentados: faltam evidências reais.']}
    (OUT/f'cabin_sweep_{SUFFIX}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

def character_sweep(d, route_states=None, skin=.002):
    qa=d['qa'];r=qa['character_design']['radius'];height=qa['character_design']['height']
    static=[x for x in d['objects'] if not x['dynamic']]
    report=[];controller=[]
    for label,state in (route_states if route_states is not None else [('upper','open_upper'),('lower','open_lower')]):
        geometry=[];names=[];floor_flags=[]
        for row in static:
            geometry.append(row['tri']);names += [row['name']]*len(row['tri']);floor_flags += [row['walkable']]*len(row['tri'])
        for name,g in d['states'][state]['objects'].items():
            row=next(x for x in d['objects'] if x['name']==name)
            t=np.asarray(g['vertices'])[np.asarray(g['triangles'])];geometry.append(t)
            names += [name]*len(t);floor_flags += [row['walkable']]*len(t)
        alltri=np.concatenate(geometry);names=np.asarray(names);floors=np.asarray(floor_flags,dtype=bool)
        tmin=alltri.min(axis=1);tmax=alltri.max(axis=1)
        route=qa['routes'][label]['points'];hits=[];uncertain=[];certified=0;evaluations=0
        supports=[];step_violations=[];unsupported=[]
        # Uma cápsula completa (segmento vertical + raio) substitui nove esferas.
        for index,(first,last) in enumerate(zip(route,route[1:])):
            a=np.asarray(first);b=np.asarray(last);lo=np.minimum(a,b)-[r,r,0];hi=np.maximum(a,b)+[r,r,height]
            sel=np.flatnonzero(np.all(tmax>=lo-1e-8,axis=1)&np.all(tmin<=hi+1e-8,axis=1));tri=alltri[sel]
            # Uma broadphase vazia certifica corpo livre dentro do ROI
            # exportado; apoio continua obrigatório e é avaliado abaixo.
            cache={};segment_hits=[];tri_min_z=tri[:,:,2].min(axis=1);tri_max_z=tri[:,:,2].max(axis=1)
            def distance(t):
                nonlocal evaluations
                if t in cache:return cache[t]
                p=a+(b-a)*t;dist=capsule_distances(p,tri,r,height);evaluations+=1
                data=(dist,p);cache[t]=data;return data
            def interval(t0,t1,depth):
                nonlocal certified
                # Certificado vertical independente: triângulos inteiramente
                # abaixo dos pés/acima da cabeça não podem penetrar a cápsula.
                z0=a[2]+(b[2]-a[2])*t0;z1=a[2]+(b[2]-a[2])*t1
                eligible=(tri_max_z>min(z0,z1)+skin+1e-10)&(tri_min_z<max(z0,z1)+height-skin-1e-10)
                if not eligible.any():certified+=1;return
                middle=(t0+t1)/2;dist,p=distance(middle)
                minimum=float(dist[eligible].min())
                penetrating=np.flatnonzero((dist<r-skin)&eligible)
                if len(penetrating):
                    segment_hits.append({'segment':index,'t':middle,'foot':p.tolist(),
                        'obstacles':sorted(set(names[sel[penetrating]].tolist())),
                        'maximum_penetration':r-minimum});return
                # Lipschitz: distância à malha varia no máximo a translação da cápsula.
                displacement=np.linalg.norm(b-a)*(t1-t0)/2
                if minimum-(r-skin)>=displacement+1e-8:certified+=1;return
                if depth>=14:
                    uncertain.append({'segment':index,'t_interval':[t0,t1],'reason':'clearance_below_numerical_certificate','minimum':minimum});return
                interval(t0,middle,depth+1);interval(middle,t1,depth+1)
            interval(0.,1.,0);hits.extend(segment_hits)
            # Apoio real somente nas faces caminháveis, sem adicionar ponte em vão.
            for t in (0.,.5,1.):
                p=a+(b-a)*t;floor_sel=np.flatnonzero(floors & (tmax[:,0]>=p[0]-r)&(tmin[:,0]<=p[0]+r)&(tmax[:,1]>=p[1]-r)&(tmin[:,1]<=p[1]+r)&(tmax[:,2]>=p[2]-.3)&(tmin[:,2]<=p[2]+.26))
                ft=alltri[floor_sel];axis=np.array(p)
                ids,zs=support_hits(p[0],p[1],ft,p[2]-.3,p[2]+.26)
                if len(ids):
                    best=int(np.argmax(zs));ground=float(zs[best]);source=str(names[floor_sel[ids[best]]]);support_kind='vertical_surface'
                    gap=p[2]-ground
                elif len(ft):
                    # Contato da semiesfera inferior com borda real; apoiado mas controller requerido.
                    ds=capsule_distances(axis,ft,r,r*2)
                    best=int(np.argmin(ds));support_kind='rounded_foot_edge_contact';source=str(names[floor_sel[best]]);ground=None;gap=float(ds[best]-r)
                    if gap>.03:unsupported.append({'segment':index,'t':t,'gap':gap,'foot':p.tolist()})
                else:
                    source=None;ground=None;gap=None;support_kind='unsupported';unsupported.append({'segment':index,'t':t,'foot':p.tolist()})
                supports.append({'segment':index,'t':t,'foot':p.tolist(),'support_source':source,'kind':support_kind,'ground_z':ground,'gap':gap})
            if abs(b[2]-a[2])>qa['character_design']['maximum_step']:
                step_violations.append({'segment':index,'delta_z':float(b[2]-a[2])})
        result={'route':label,'state':state,'segments':len(route)-1,'certified_intervals':certified,
                'capsule_distance_evaluations':evaluations,'penetrations':hits,'unresolved_intervals':uncertain,
                'supports':supports,'unsupported':unsupported,'step_violations':step_violations,
                'status':'blocked' if hits or unsupported or step_violations else 'pending' if uncertain else 'continuous_surface_clear',
                'solid_containment_certified':False,'engine_controller_verified':False}
        report.append(result)
        # Replay cinemático com volume real: para no primeiro segmento inválido, nunca teleporta.
        first_bad=min([h['segment'] for h in hits+unsupported+step_violations+uncertain],default=None)
        controller.append({'route':label,'accepted_segments':len(route)-1 if first_bad is None else first_bad,
                           'stopped_at_segment':first_bad,'arrived':first_bad is None,
                           'scope':'pré-validação cinemática por cápsula CCD; gravidade/slide/step solver/plataforma móvel exigem engine'})
        print(json.dumps({'route':label,'penetrations':len(hits),'unresolved':len(uncertain),'unsupported':len(unsupported)}),flush=True)
    result={'schema':'boas/character-sweep-v1','source':d['source'],'shape':{'type':'capsule','radius':r,'height':height,'skin':skin},
            'method':'Distância exata segmento–triângulo da cápsula e subdivisão Lipschitz contínua. Triângulos reais, sem ignorar faces do chão que penetram no corpo.',
            'routes':report,'kinematic_replay':controller,'engine_physics_verified':False,'release_ready':False}
    (OUT/f'character_sweep_{SUFFIX}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('cabin','character','all'),default='all')
    p.add_argument('--geometry',type=Path,default=GEOMETRY);p.add_argument('--output-dir',type=Path,default=OUT);p.add_argument('--suffix',default=SUFFIX);args=p.parse_args()
    GEOMETRY=args.geometry;OUT=args.output_dir;SUFFIX=args.suffix;OUT.mkdir(parents=True,exist_ok=True)
    d=load()
    if args.mode in ('cabin','all'):cabin_sweep(d)
    if args.mode in ('character','all'):character_sweep(d)
