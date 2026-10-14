"""Diagnóstico externo derivado da B80; não salva Blender nem altera arquitetura.

Mantém a rota antiga como diagnóstico e audita separadamente a travessia OSM
comprovada. Não liga automaticamente seus extremos ao Mercado ou ao saguão.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

import audit_slice_volume_b79 as audit
from slice_geometry import capsule_distances, support_hits

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/reports/world/cairu-market-pedestrian'
GEOMETRY = ROOT / 'artifacts/lacerda-controller/geometry_b80.json'


def densify(points, spacing=.1):
    result = []
    for a, b in zip(points, points[1:]):
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        count = max(1, math.ceil(np.linalg.norm(b[:2]-a[:2])/spacing))
        result.extend((a+(b-a)*i/count).tolist() for i in range(count))
    result.append(list(points[-1]))
    return result


def ground_follow(d, points, state, skin=.002):
    triangles, names = [], []
    for row in d['objects']:
        if not row['walkable'] or row['name'].startswith(('NAV |', 'B80 |')):
            continue
        g = d['states'][state]['objects'].get(row['name'], row['geometry'])
        t = np.asarray(g['vertices'])[np.asarray(g['triangles'], dtype=int)]
        triangles.append(t)
        names.extend([row['name']]*len(t))
    tri = np.concatenate(triangles)
    names = np.asarray(names)
    lo, hi = tri.min(axis=1), tri.max(axis=1)
    radius, height = d['qa']['character_design']['radius'], d['qa']['character_design']['height']
    max_step = d['qa']['character_design']['maximum_step']
    result, records, pending = [], [], []
    for index, original in enumerate(densify(points)):
        p = np.asarray(original, dtype=float)
        sel = np.flatnonzero(np.all(hi[:, :2] >= p[:2]-radius, axis=1) &
                            np.all(lo[:, :2] <= p[:2]+radius, axis=1) &
                            (hi[:, 2] >= p[2]-max_step) & (lo[:, 2] <= p[2]+max_step))
        local = tri[sel]
        ids, zs = support_hits(p[0], p[1], local, p[2]-max_step, p[2]+max_step)
        if not len(ids):
            pending.append({'point': index, 'reason': 'NO_REAL_CENTER_SUPPORT', 'position': p.tolist()})
            result.append(p.tolist())
            continue
        best = int(np.argmax(zs))
        ground = float(zs[best])
        source = str(names[sel[ids[best]]])
        # Casco arredondado em contato com a superfície existente: nenhuma
        # rampa/piso é criado. Apoio central e resolução de degraus são gates.
        lower, upper = ground, ground+max_step
        for _ in range(26):
            mid = (lower+upper)/2
            p[2] = mid
            if float(capsule_distances(p, local, radius, height).min()) < radius+skin:
                lower = mid
            else:
                upper = mid
        p[2] = upper
        gap = upper-ground
        if gap > .03:
            pending.append({'point': index, 'reason': 'STEP_SOLVER_REQUIRED',
                            'ground_source': source, 'central_support_gap': gap})
        result.append(p.tolist())
        records.append({'point': index, 'position': p.tolist(), 'original_z': original[2],
                        'ground_z': ground, 'support_source': source, 'central_support_gap': gap})
    return result, records, pending


def distance_to_polyline(point, polyline):
    a, b = polyline[:-1, :2], polyline[1:, :2]
    delta = b-a
    t = np.clip(np.sum((point-a)*delta, axis=1)/np.maximum(np.sum(delta*delta, axis=1), 1e-15), 0, 1)
    return float(np.linalg.norm(a+t[:, None]*delta-point, axis=1).min())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = json.loads(GEOMETRY.read_text(encoding='utf-8'))
    baseline = np.asarray(d['qa']['routes']['lower']['points'])
    binding = json.loads((OUT/'osm_crossing_binding.json').read_text(encoding='utf-8'))
    crossing = next(w for w in binding['ways'] if w['osm_id'] == 395865976)
    diagnostics = []
    for n in crossing['nodes']:
        diagnostics.append({'node_id': n['id'], 'xy': n['blender_xy'],
                            'distance_to_old_route_units': distance_to_polyline(np.asarray(n['blender_xy']), baseline)})
    # Z não vem de OSM; busca local limitada nas faces visuais da B80.
    # A cota 7,256 é somente seed de busca, nunca altitude certificada.
    seeds = [n['blender_xy']+[7.255668640136719] for n in crossing['nodes']]
    results = {}
    specs = [('lower_ground_diagnostic', baseline.tolist(), 'open_lower'),
             ('osm_crossing_candidate', seeds, 'closed_lower')]
    for label, points, state in specs:
        new, records, pending = ground_follow(d, points, state)
        d['qa']['routes'][label] = {'points': new, 'status': 'candidate',
                                  'scope': 'diagnóstico geométrico; não habilita movimento/runtime'}
        results[label] = {'points': new, 'samples': records, 'pending': pending, 'state': state}
    for row in d['objects']:
        g = row['geometry']
        row['tri'] = np.asarray(g['vertices'], dtype=float)[np.asarray(g['triangles'], dtype=int)]
    audit.OUT = OUT
    audit.SUFFIX = 'external_ground_candidate'
    sweep = audit.character_sweep(d, [(label, state) for label, _, state in specs])
    report = {'schema': 'boas/cairu-ground-diagnostic-v1', 'source': d['source'],
              'geometry_export': GEOMETRY.relative_to(ROOT).as_posix(),
              'geometry_sha256': hashlib.sha256(GEOMETRY.read_bytes()).hexdigest(),
              'geographic_ssot': binding['parent_ssot'], 'ssot_sha256': binding['ssot_sha256'],
              'old_route_crossing_comparison': diagnostics, 'routes': results,
              'geometry_changed': False, 'engine_controller_verified': False,
              'movement_enabled': False, 'release_ready': False,
              'note': 'Rota antiga não ganha vínculo OSM por ground-following. Travessia isolada não prova seus acessos, sinal verde, rampa existente nem entrada do Mercado.'}
    (OUT/'ground_following_candidates.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'routes': [{'name': k, 'samples': len(v['points']), 'pending': len(v['pending'])} for k, v in results.items()],
                      'crossing_distances': diagnostics,
                      'sweep': [{'route': r['route'], 'status': r['status'], 'penetrations': len(r['penetrations']),
                                 'unsupported': len(r['unsupported']), 'unresolved': len(r['unresolved_intervals'])} for r in sweep['routes']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
