"""Classifica desníveis locais de duas superfícies sem aprovar rotas.

O cálculo compara somente a coordenada Z amostrada no mesmo XY.
Uma diferença pequena não garante circulação/collision/navegação reais.
"""
import math


def finite_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{field}: valor numérico finito obrigatório")
    return float(value)


def evaluate_samples(samples, floor_top_z, *, step_limit_m=0.25, baseline_tolerance_m=0.02):
    floor = finite_number(floor_top_z, "floor_top_z")
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
        baseline = row.get("terrain_world_z_baseline")
        if terrain is None:
            observations.append({"world_xy": position, "state": "NO_TERRAIN_HIT",
                                 "height_delta_m": None, "baseline_delta_m": None})
            continue
        height = finite_number(terrain, f"terrain_world_z[{i}]")
        dz = floor - height
        if dz > step:
            state = "FLOOR_ABOVE_TERRAIN"
        elif dz < -step:
            state = "TERRAIN_ABOVE_FLOOR"
        else:
            state = "LOCALLY_SIMILAR_LEVEL"
        historical_difference = None
        if baseline is not None:
            historical_difference = height - finite_number(baseline, f"baseline[{i}]")
            if abs(historical_difference) > tolerance:
                state = "TERRAIN_CHANGED_SINCE_BASELINE"
        observations.append({"world_xy": position, "state": state,
                             "height_delta_m": round(dz, 6),
                             "baseline_delta_m": round(historical_difference, 6)
                             if historical_difference is not None else None})
    alert_count = sum(row["state"] != "LOCALLY_SIMILAR_LEVEL" for row in observations)
    return {
        "schema": "boas/terrain-interface-qa-v1",
        "observations": observations,
        "floor_top_z": floor,
        "step_limit_m": step,
        "baseline_tolerance_m": tolerance,
        "alerts": alert_count,
        "status": "NEEDS_GEOMETRIC_AND_ROUTE_REVIEW" if alert_count else "LOCAL_LEVELS_ONLY_NOT_ROUTE_CERTIFIED",
        "route_certified": False,
        "terrain_modified": False,
    }
