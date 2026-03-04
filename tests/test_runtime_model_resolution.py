from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nlu.runtime_components import infer as runtime_infer


class RuntimeModelResolutionTest(unittest.TestCase):
    def test_require_local_model_dir_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "ner"
            with self.assertRaises(RuntimeError) as ctx:
                runtime_infer._require_local_model_dir(missing, label="NER")
        self.assertIn("Missing local NER model", str(ctx.exception))

    def test_default_ner_model_raises_when_default_directory_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(runtime_infer, "MODELS_DIR", Path(tmp)):
                with self.assertRaises(RuntimeError) as ctx:
                    runtime_infer._default_ner_model()
        self.assertIn("Train it locally first", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
