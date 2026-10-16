"""Synthetic fixtures test evidence invariants, not scientific conclusions."""

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills/ideascientist"
spec = importlib.util.spec_from_file_location("audit_report", SKILL / "scripts/audit_report.py")
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


def synthetic_value(schema):
    kind = schema["type"]
    if kind == "object":
        return {key: synthetic_value(value) for key, value in schema.get("properties", {}).items()}
    if kind == "array":
        return [synthetic_value(schema["items"])]
    if kind == "boolean":
        return False
    return "Synthetic test value; not a research claim."


class EvidenceAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.report = synthetic_value(json.loads((SKILL / "assets/report.schema.json").read_text()))
        self.report["key_terms"] = {"test": "Synthetic fixture"}
        self.report["related_work"][0]["citations"] = ["P001"]
        self.report["core_problem"]["problem_statement"] = "Synthetic evidence [P001]."
        (self.run / "papers").mkdir()
        (self.run / "papers/P001.md").write_text("Synthetic reading digest. Section 1. No real paper.")
        self.sources = [{
            "id": "P001", "title": "Synthetic fixture", "location": "https://example.org/paper",
            "version_date": "2025-12-31", "read_status": "body_read", "digest": "papers/P001.md",
            "evidence": [{"claim": "Synthetic claim", "locator": "Section 1"}],
        }]

    def audit(self, cutoff=None):
        (self.run / "report.json").write_text(json.dumps(self.report))
        (self.run / "sources.json").write_text(json.dumps(self.sources))
        return audit_module.audit(self.run, cutoff)

    def test_valid_record_is_only_mechanical_success(self):
        result = self.audit(date(2026, 1, 1))
        self.assertTrue(result["ok"])
        self.assertIn("No verification of truth", result["scope"])

    def test_unknown_inline_citation_rejected(self):
        self.report["title"] += " [P999]"
        self.assertFalse(self.audit()["ok"])

    def test_abstract_is_not_body_evidence(self):
        self.sources[0]["read_status"] = "abstract_only"
        self.assertFalse(self.audit()["ok"])

    def test_empty_evidence_rejected(self):
        self.sources[0]["evidence"] = []
        self.assertFalse(self.audit()["ok"])

    def test_duplicate_ids_rejected(self):
        self.sources.append(dict(self.sources[0]))
        self.assertFalse(self.audit()["ok"])

    def test_missing_digest_rejected(self):
        (self.run / "papers/P001.md").unlink()
        self.assertFalse(self.audit()["ok"])

    def test_path_escape_rejected(self):
        self.sources[0]["digest"] = "../outside.md"
        self.assertFalse(self.audit()["ok"])

    def test_cutoff_is_exclusive(self):
        self.sources[0]["version_date"] = "2026-01-01"
        self.assertFalse(self.audit(date(2026, 1, 1))["ok"])

    def test_unknown_date_only_allowed_outside_temporal_mode(self):
        self.sources[0]["version_date"] = None
        self.assertTrue(self.audit()["ok"])
        self.assertFalse(self.audit(date(2026, 1, 1))["ok"])

    def test_missing_falsification_condition_rejected(self):
        del self.report["falsifiable_predictions"][0]["kill_condition"]
        self.assertFalse(self.audit()["ok"])

    def test_duplicate_json_keys_rejected(self):
        self.audit()
        (self.run / "sources.json").write_text('[{"id":"P001","id":"P002"}]')
        self.assertFalse(audit_module.audit(self.run)["ok"])

    def test_invalid_date_rejected(self):
        self.sources[0]["version_date"] = "2025-02-30"
        self.assertFalse(self.audit()["ok"])


if __name__ == "__main__":
    unittest.main()
