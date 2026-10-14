"""Triagem externa B80 e vínculo topológico OSM; sem mutação da cena."""
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/reports/world/cairu-market-pedestrian"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    osm = ROOT / "world-reference/centro-lapa-tororo-fontenova/source/osm-mapzen-20261005T045222Z/map.osm"
    doc = ET.parse(osm).getroot()
    nodes = {int(n.attrib["id"]): n for n in doc.findall("node")}
    ways = {int(w.attrib["id"]): w for w in doc.findall("way")}
    ids = [395865976, 46348179, 978525930, 1004133497, 312006925, 1423065746]
    ssot = json.loads((ROOT / "world/geographic-reference.json").read_text(encoding="utf-8"))
    transform = ssot["horizontal"]["transform"]
    theta = math.radians(transform["rotation_epsg3857_to_blender_deg"])
    scale = transform["scale_blender_units_per_meter"]
    tx, ty = transform["translation_blender"]

    def point(n):
        lon, lat = float(n.attrib["lon"]), float(n.attrib["lat"])
        x = 6378137*math.radians(lon)
        y = 6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))
        return [scale*(math.cos(theta)*x-math.sin(theta)*y)+tx, scale*(math.sin(theta)*x+math.cos(theta)*y)+ty]

    rows = []
    for ident in ids:
        w = ways.get(ident)
        if w is None:
            rows.append({"osm_id": ident, "status": "SOURCE_LIMITATION"})
            continue
        refs = [int(n.attrib["ref"]) for n in w.findall("nd")]
        row = {"osm_id": ident, "tags": {t.attrib["k"]: t.attrib["v"] for t in w.findall("tag")}, "node_refs": refs, "nodes": [{"id": r, "wgs84": [float(nodes[r].attrib["lat"]), float(nodes[r].attrib["lon"])], "blender_xy": point(nodes[r]), "tags": {t.attrib["k"]: t.attrib["v"] for t in nodes[r].findall("tag")}} for r in refs if r in nodes]}
        if ident == 395865976:
            links = []
            for road in doc.findall("way"):
                tags = {t.attrib["k"]: t.attrib["v"] for t in road.findall("tag")}
                if "highway" not in tags or int(road.attrib["id"]) == ident:
                    continue
                shared = sorted(set(refs) & {int(n.attrib["ref"]) for n in road.findall("nd")})
                if shared:
                    links.append({"way": int(road.attrib["id"]), "shared_nodes": shared, "tags": tags})
            row["topological_connections"] = links
        rows.append(row)
    report = {"source": osm.relative_to(ROOT).as_posix(), "source_sha256": hashlib.sha256(osm.read_bytes()).hexdigest(), "parent_ssot": "world/geographic-reference.json", "ssot_sha256": hashlib.sha256((ROOT/"world/geographic-reference.json").read_bytes()).hexdigest(), "ways": rows, "rule": "Conexão por node ID compartilhado, nunca proximidade. Isso não mede soleira, rampa ou confirma fase atual da sinalização."}
    (OUT / "osm_crossing_binding.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    reference = json.loads((ROOT / "artifacts/structural-pipeline/centro-lapa-tororo-fontenova/structural_reference.json").read_text(encoding="utf-8"))
    features = {int(f["osm_id"]): f for f in reference["features"] if f.get("osm_type") == "way"}
    scene = json.loads((ROOT / "docs/reports/blender/geographic-foundation/structural_scene_after.json").read_text(encoding="utf-8"))
    alignment = []
    for row in rows:
        ident = row["osm_id"]
        feature = features.get(ident)
        residual = None
        if feature and feature["node_refs"] == row["node_refs"]:
            residual = max(math.dist(p["blender_xy"], q) for p, q in zip(row["nodes"], feature["blender_xy"]))
        matches = [{"name": o["name"], "type": o["type"], "collections": o["collections"], "bounds": o.get("bounds"), "osm_ids": o["osm_ids"]} for o in scene["objects"] if ident in o.get("osm_ids", [])]
        alignment.append({"osm_id": ident, "reference_max_xy_residual": residual,
                          "B76_explicit_id_objects": matches,
                          "current_final_surface_alignment": "NEEDS_REVIEW",
                          "reason": "Vínculo por ID comprovado no inventário B76. Bounding box/curva de referência não comprovam pavimento final B80; exportação volumétrica B80 exclui curvas."})
    (OUT / "reference_alignment.json").write_text(json.dumps({"geographic_ssot": report["parent_ssot"], "rows": alignment, "scene_source_revision": "B76; não apresentar como reexportação B80"}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    sweep = json.loads((ROOT / "docs/reports/blender/lacerda-controller-b80/character_sweep_ground_b80.json").read_text(encoding="utf-8"))
    lower = next(r for r in sweep["routes"] if r["route"] == "lower")
    penetrations = [{**hit, "scope": "LACERDA_VERTICAL_INTERFACE" if hit["segment"] in [2, 3] else "CAIRU_MARKET_EXTERNAL", "correction_type_candidate": "ground-following on existing surfaces, no architectural rescale"} for hit in lower["penetrations"]]
    (OUT / "baseline_penetrations.json").write_text(json.dumps({"source": sweep["source"], "witnesses": penetrations, "vertical_interface_witnesses": 2, "external_witnesses": 7, "vertical_movement_enabled": False}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"ways": [{"id": r["osm_id"], "tags": r.get("tags"), "nodes": r.get("nodes"), "connections": r.get("topological_connections")} for r in rows], "baseline_penetrations": len(penetrations)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
