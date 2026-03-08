from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AABB:
    x: float
    y: float
    z: float

    @property
    def half(self) -> Tuple[float, float, float]:
        return (self.x * 0.5, self.y * 0.5, self.z * 0.5)

    def contains(self, other: "AABB", clearance: float = 0.0) -> bool:
        return (
            other.x + 2.0 * clearance <= self.x
            and other.y + 2.0 * clearance <= self.y
            and other.z + 2.0 * clearance <= self.z
        )


def aabb_from_box(x: float, y: float, z: float) -> AABB:
    return AABB(x=x, y=y, z=z)


def aabb_from_tubs(rmax: float, hz: float) -> AABB:
    d = 2.0 * rmax
    return AABB(x=d, y=d, z=2.0 * hz)


def aabb_from_sphere(rmax: float) -> AABB:
    d = 2.0 * rmax
    return AABB(x=d, y=d, z=d)


def aabb_from_orb(rmax: float) -> AABB:
    d = 2.0 * rmax
    return AABB(x=d, y=d, z=d)


def aabb_from_cons(rmax1: float, rmax2: float, hz: float) -> AABB:
    rmax = max(rmax1, rmax2)
    d = 2.0 * rmax
    return AABB(x=d, y=d, z=2.0 * hz)


def aabb_from_trd(x1: float, x2: float, y1: float, y2: float, z: float) -> AABB:
    return AABB(x=max(x1, x2), y=max(y1, y2), z=z)


def aabb_from_polycone(z_planes: Tuple[float, ...], rmax: Tuple[float, ...]) -> AABB:
    if not z_planes or not rmax:
        return AABB(x=0.0, y=0.0, z=0.0)
    zmin = min(z_planes)
    zmax = max(z_planes)
    rr = max(rmax)
    d = 2.0 * rr
    return AABB(x=d, y=d, z=(zmax - zmin))


def aabb_from_cuttubs(rmax: float, hz: float, tilt_x: float = 0.0, tilt_y: float = 0.0) -> AABB:
    # Conservative: cut planes do not enlarge radial bound.
    d = 2.0 * rmax
    base = AABB(x=d, y=d, z=2.0 * hz)
    # Small extra conservative inflation for non-zero tilt.
    if abs(tilt_x) > 1e-9 or abs(tilt_y) > 1e-9:
        inflate = 1.0 + min(0.2, (abs(tilt_x) + abs(tilt_y)) * 0.01)
        return AABB(x=base.x * inflate, y=base.y * inflate, z=base.z * inflate)
    return base


def aabb_from_trap(x1: float, x2: float, x3: float, x4: float, y1: float, y2: float, z: float) -> AABB:
    return AABB(x=max(x1, x2, x3, x4), y=max(y1, y2), z=z)


def aabb_from_para(x: float, y: float, z: float, alpha: float = 0.0, theta: float = 0.0, phi: float = 0.0) -> AABB:
    inflate_x = 2.0 * z * abs(math.tan(math.radians(alpha))) if abs(alpha) > 1e-9 else 0.0
    inflate_y = 2.0 * z * abs(math.tan(math.radians(theta))) if abs(theta) > 1e-9 else 0.0
    inflate_xy = 2.0 * z * abs(math.tan(math.radians(phi))) if abs(phi) > 1e-9 else 0.0
    return AABB(x=x + inflate_x + inflate_xy, y=y + inflate_y + inflate_xy, z=z)


def aabb_from_torus(rtor: float, rmax: float) -> AABB:
    span_xy = 2.0 * (rtor + rmax)
    return AABB(x=span_xy, y=span_xy, z=2.0 * rmax)


def aabb_from_ellipsoid(ax: float, by: float, cz: float) -> AABB:
    return AABB(x=2.0 * ax, y=2.0 * by, z=2.0 * cz)


def aabb_from_elliptical_tube(ax: float, by: float, hz: float) -> AABB:
    return AABB(x=2.0 * ax, y=2.0 * by, z=2.0 * hz)


def aabb_from_polyhedra(z_planes: Tuple[float, ...], rmax: Tuple[float, ...]) -> AABB:
    if not z_planes or not rmax:
        return AABB(x=0.0, y=0.0, z=0.0)
    zmin = min(z_planes)
    zmax = max(z_planes)
    rr = max(rmax)
    d = 2.0 * rr
    return AABB(x=d, y=d, z=(zmax - zmin))


def aabb_apply_transform(base: AABB, rx: float, ry: float, rz: float) -> AABB:
    # Conservative rotation envelope; translation does not change size.
    if abs(rx) < 1e-9 and abs(ry) < 1e-9 and abs(rz) < 1e-9:
        return base
    d = (base.x ** 2 + base.y ** 2 + base.z ** 2) ** 0.5
    return AABB(x=d, y=d, z=d)


def aabb_union_xy(module: AABB, nx: int, ny: int, pitch_x: float, pitch_y: float) -> AABB:
    span_x = (nx - 1) * pitch_x + module.x
    span_y = (ny - 1) * pitch_y + module.y
    return AABB(x=span_x, y=span_y, z=module.z)


def aabb_ring(module: AABB, radius: float) -> AABB:
    span = 2.0 * (radius + 0.5 * max(module.x, module.y))
    return AABB(x=span, y=span, z=module.z)


def aabb_stackz(x: float, y: float, thicknesses: Tuple[float, ...], clearance: float) -> AABB:
    if len(thicknesses) == 0:
        return AABB(x=0.0, y=0.0, z=0.0)
    span_z = sum(thicknesses) + max(0, len(thicknesses) - 1) * clearance
    return AABB(x=x, y=y, z=span_z)


def aabb_union(a: AABB, b: AABB) -> AABB:
    return AABB(x=max(a.x, b.x), y=max(a.y, b.y), z=max(a.z, b.z))


def aabb_intersection(a: AABB, b: AABB) -> AABB:
    return AABB(x=min(a.x, b.x), y=min(a.y, b.y), z=min(a.z, b.z))

