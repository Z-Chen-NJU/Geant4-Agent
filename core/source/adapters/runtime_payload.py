from __future__ import annotations

from core.source.spec import SourceSpec


def source_spec_to_runtime_payload(spec: SourceSpec) -> dict[str, object]:
    payload: dict[str, object] = {"source_type": spec.source_type}
    particle = spec.fields.get("particle")
    if particle is not None:
        payload["particle"] = str(particle)
    energy_mev = spec.fields.get("energy_mev")
    if energy_mev is not None:
        payload["energy"] = float(energy_mev)
    position = spec.fields.get("position_mm")
    if isinstance(position, list) and len(position) >= 3:
        payload["position"] = {"x": float(position[0]), "y": float(position[1]), "z": float(position[2])}
    direction = spec.fields.get("direction_vec")
    if isinstance(direction, list) and len(direction) >= 3:
        payload["direction"] = {"x": float(direction[0]), "y": float(direction[1]), "z": float(direction[2])}
    return payload
