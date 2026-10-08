"""Classifica contato vertical somente se as duas malhas existirem no mesmo XY.

A cota máxima global do piso é referência descritiva, não um hit de superfície.
Nenhum resultado certifica circulação, colisão de personagem ou implantação.
"""
import math


def finite_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{field}: valor numérico finito obrigatório")
    return float(value)


def evaluate_samples(samples, floor_top_z, *, step_limit_m=0.25, baseline_tolerance_m=0.02):
    reference = finite_number(floor_top_z, "floor_top_z")
    step = finite_number(step_limit_m, "step_limit_m")
    tolerance = finite_number(baseline_tolerance_m, "baseline_tolerance_m")
    if step <= 0 or tolerance < 0:
        raise ValueError("Limites físicos inválidos")
    if not isinstance(samples, list) or not samples:
        raise ValueError("É obrigatório medir ao menos um controle físico")
    observations = []
    for i, row in enumerate(samples):
        if not isinstance(row, dict):
            raise ValueError(f"Controle {i}: inválido")
        xy = row.get("world_xy")
        if not isinstance(xy, (list, tuple)) or len(xy) != 2:
            raise ValueError(f"Controle {i}: world_xy inválido")
        position = [finite_number(v, f"world_xy[{i}]") for v in xy]
        terrain = row.get("terrain_world_z")
        floor = row.get("floor_world_z")
        baseline = row.get("terrain_world_z_baseline")
        terrain_z = finite_number(terrain, f"terrain_world_z[{i}]") if terrain is not None else None
        floor_z = finite_number(floor, f"floor_world_z[{i}]") if floor is not None else None
        baseline_z = finite_number(baseline, f"baseline[{i}]") if baseline is not None else None
        baseline_delta = (terrain_z - baseline_z if terrain_z is not None and baseline_z is not None else None)

        if terrain_z is None and floor_z is None:
            state, height_delta = "NO_BOTH_SURFACES_HIT", None
        elif terrain_z is None:
            state, height_delta = "NO_TERRAIN_HIT", None
        elif floor_z is None:
            state, height_delta = "NO_FLOOR_HIT", None
        else:
            height_delta = floor_z - terrain_z
            if height_delta > step:
                state = "FLOOR_ABOVE_TERRAIN"
            elif height_delta < -step:
                state = "TERRAIN_ABOVE_FLOOR"
            else:
                state = "LOCALLY_SIMILAR_LEVEL"

        changed = baseline_delta is not None and abs(baseline_delta) > tolerance
        if changed and height_delta is not None:
            state = "TERRAIN_CHANGED_SINCE_BASELINE"

        observations.append({
            "world_xy": position,
            "state": state,
            "floor_hit": floor_z is not None,
            "terrain_hit": terrain_z is not None,
            "floor_world_z": floor_z,
            "terrain_world_z": terrain_z,
            "height_delta_m": round(height_delta, 6) if height_delta is not None else None,
            "baseline_delta_m": round(baseline_delta, 6) if baseline_delta is not None else None,
            "baseline_changed": changed,
            "floor_polygon": row.get("floor_polygon"),
            "terrain_polygon": row.get("terrain_polygon"),
        })
    alerts = sum(item["state"] != "LOCALLY_SIMILAR_LEVEL" or item["baseline_changed"]
                 for item in observations)
    valid_pairs = sum(item["floor_hit"] and item["terrain_hit"] for item in observations)
    return {
        "schema": "boas/terrain-interface-qa-v2",
        "observations": observations,
        "floor_reference_top_z": reference,
        "valid_pairs": valid_pairs,
        "missing_floor_count": sum(not item["floor_hit"] for item in observations),
        "missing_terrain_count": sum(not item["terrain_hit"] for item in observations),
        "step_limit_m": step,
        "baseline_tolerance_m": tolerance,
        "alerts": alerts,
        "status": "NEEDS_GEOMETRIC_AND_ROUTE_REVIEW" if alerts else "LOCAL_LEVELS_ONLY_NOT_ROUTE_CERTIFIED",
        "route_certified": False,
        "terrain_modified": False,
    }
