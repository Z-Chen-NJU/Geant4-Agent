from __future__ import annotations

from dataclasses import dataclass, field

from core.orchestrator.types import Intent


@dataclass
class GeometrySlots:
    kind: str | None = None
    size_triplet_mm: list[float] | None = None
    radius_mm: float | None = None
    half_length_mm: float | None = None


@dataclass
class MaterialsSlots:
    primary: str | None = None


@dataclass
class SourceSlots:
    kind: str | None = None
    particle: str | None = None
    energy_mev: float | None = None
    position_mm: list[float] | None = None
    direction_vec: list[float] | None = None


@dataclass
class PhysicsSlots:
    explicit_list: str | None = None
    recommendation_intent: str | None = None


@dataclass
class OutputSlots:
    format: str | None = None
    path: str | None = None


@dataclass
class SlotFrame:
    intent: Intent = Intent.OTHER
    confidence: float = 0.0
    normalized_text: str = ""
    target_slots: list[str] = field(default_factory=list)
    geometry: GeometrySlots = field(default_factory=GeometrySlots)
    materials: MaterialsSlots = field(default_factory=MaterialsSlots)
    source: SourceSlots = field(default_factory=SourceSlots)
    physics: PhysicsSlots = field(default_factory=PhysicsSlots)
    output: OutputSlots = field(default_factory=OutputSlots)
    notes: list[str] = field(default_factory=list)

    def has_content(self) -> bool:
        return any(
            [
                self.geometry.kind,
                self.geometry.size_triplet_mm,
                self.geometry.radius_mm is not None,
                self.geometry.half_length_mm is not None,
                self.materials.primary,
                self.source.kind,
                self.source.particle,
                self.source.energy_mev is not None,
                self.source.position_mm,
                self.source.direction_vec,
                self.physics.explicit_list,
                self.physics.recommendation_intent,
                self.output.format,
                self.output.path,
            ]
        )
