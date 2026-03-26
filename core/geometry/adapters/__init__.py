from core.geometry.adapters.config_fragment import geometry_spec_to_config_fragment
from core.geometry.adapters.diff import diff_geometry_config_fragment
from core.geometry.adapters.runtime_payload import geometry_spec_to_runtime_geometry


def compare_slot_frame_geometry(*args, **kwargs):
    from core.geometry.adapters.legacy_compare import compare_slot_frame_geometry as _impl

    return _impl(*args, **kwargs)


def legacy_geometry_from_candidate(*args, **kwargs):
    from core.geometry.adapters.legacy_compare import legacy_geometry_from_candidate as _impl

    return _impl(*args, **kwargs)

__all__ = [
    "compare_slot_frame_geometry",
    "diff_geometry_config_fragment",
    "geometry_spec_to_config_fragment",
    "geometry_spec_to_runtime_geometry",
    "legacy_geometry_from_candidate",
]
