import sys
import unittest
from pathlib import Path
import schemathesis
from hypothesis import given, settings, HealthCheck

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app

schema = schemathesis.openapi.from_asgi("/openapi.json", app)

class TestSchemathesisStudyAPI(unittest.TestCase):
    """
    OpenAPI property-based contract & fuzzing verification for Phase 3 study orchestration endpoints.
    """

    @classmethod
    def setUpClass(cls):
        import tempfile, shutil, os
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp_path = Path(cls.tmp.name)
        shutil.copyfile(Path(__file__).resolve().parent.parent.parent / "gpat_knowledge.db", cls.tmp_path)
        cls._orig_env = os.environ.get("GPAT_DB_PATH")
        os.environ["GPAT_DB_PATH"] = str(cls.tmp_path)

    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(case=schema["/api/study/today"]["GET"].as_strategy())
    def test_fuzz_study_today(self, case):
        case.call_and_validate()

    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(case=schema["/api/study/review-queue"]["GET"].as_strategy())
    def test_fuzz_study_review_queue(self, case):
        case.call_and_validate()

    @classmethod
    def tearDownClass(cls):
        import os
        if cls._orig_env is not None:
            os.environ["GPAT_DB_PATH"] = cls._orig_env
        else:
            os.environ.pop("GPAT_DB_PATH", None)
        try:
            if cls.tmp_path.exists():
                cls.tmp_path.unlink()
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()
