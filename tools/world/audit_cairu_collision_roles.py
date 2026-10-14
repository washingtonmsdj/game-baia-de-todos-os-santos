"""Separa pintura comprovadamente visual de colisão; sem mudar cena/CCD B80."""
import hashlib
import json
from pathlib import Path

import numpy as np

import audit_slice_volume_b79 as audit

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/reports/world/cairu-market-pedestrian'


def main():
    d = json.loads((ROOT/'artifacts/lacerda-controller/geometry_b80.json').read_text(encoding='utf-8'))
    prepared = json.loads((OUT/'ground_following_candidates.json').read_text(encoding='utf-8'))
    # Correspondência exata à operação de criação documentada: malha plana,
    # visual_environment, ID e separação para evitar z-fighting. Não generalizar
    # exclusão por nome de pintura ou material, nem excluir meios-fios.
    name = 'LAC R30B06 | fundo verde travessia 3178050253'
    row = next(r for r in d['objects'] if r['name'] == name)
    props = row['properties']
    vertices = np.asarray(row['geometry']['vertices'])
    assert props['boas_role'] == 'visual_environment'
    assert props['osm_node_id'] == '3178050253'
    assert props['surface_separation_m'] == .003
    assert np.ptp(vertices[:, 2]) < 1e-8 and row['geometry']['complete_mesh']
    creator = ROOT/'automation/blender/refine_lacerda_r30b06_public_space.py'
    evidence = {'object': name, 'physical_role': 'render_only_paint',
                'osm_node_id': props['osm_node_id'], 'source_media_id': props['source_media_id'],
                'creator': creator.relative_to(ROOT).as_posix(),
                'creator_sha256': hashlib.sha256(creator.read_bytes()).hexdigest(),
                'geometry_planar': True, 'render_offset': .003,
                'geometry_changed': False, 'live_collision_binding_applied': False,
                'reason': 'Script cria pintura sem volume, não laje. A malha continua visual; colisão é fornecida pelo chão existente.'}
    d['objects'] = [r for r in d['objects'] if r['name'] != name]
    for r in d['objects']:
        g = r['geometry']
        r['tri'] = np.asarray(g['vertices'], dtype=float)[np.asarray(g['triangles'], dtype=int)]
    d['qa']['routes']['osm_crossing_candidate'] = {'points': prepared['routes']['osm_crossing_candidate']['points']}
    audit.OUT = OUT
    audit.SUFFIX = 'crossing_collision_roles'
    result = audit.character_sweep(d, [('osm_crossing_candidate', 'closed_lower')])
    evidence['sweep_status'] = result['routes'][0]['status']
    evidence['remaining_penetrations'] = len(result['routes'][0]['penetrations'])
    (OUT/'collision_role_evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == '__main__':
    main()
