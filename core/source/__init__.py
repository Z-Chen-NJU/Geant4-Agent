from core.source.catalog import (
    SourceCatalogEntry,
    SourceFieldDefinition,
    get_source_catalog_entry,
    iter_source_catalog,
    resolve_source_type,
)
from core.source.adapters import (
    compare_slot_frame_source,
    diff_source_config_fragment,
    legacy_source_from_candidate,
    source_spec_to_config_fragment,
    source_spec_to_runtime_payload,
)
from core.source.compiler import (
    SourceCompileResult,
    build_source_intent_from_config,
    build_source_intent_from_semantic_frame,
    build_source_intent_from_slot_frame,
    compile_source_intent,
    compile_source_spec_from_config,
    compile_source_spec_from_semantic_frame,
    compile_source_spec_from_slot_frame,
)
from core.source.spec import SourceEvidence, SourceFieldResolution, SourceIntent, SourceSpec

__all__ = [
    "SourceCatalogEntry",
    "SourceCompileResult",
    "SourceEvidence",
    "SourceFieldDefinition",
    "SourceFieldResolution",
    "SourceIntent",
    "SourceSpec",
    "build_source_intent_from_config",
    "build_source_intent_from_semantic_frame",
    "build_source_intent_from_slot_frame",
    "compare_slot_frame_source",
    "compile_source_intent",
    "compile_source_spec_from_config",
    "compile_source_spec_from_semantic_frame",
    "compile_source_spec_from_slot_frame",
    "diff_source_config_fragment",
    "get_source_catalog_entry",
    "iter_source_catalog",
    "legacy_source_from_candidate",
    "resolve_source_type",
    "source_spec_to_config_fragment",
    "source_spec_to_runtime_payload",
]
