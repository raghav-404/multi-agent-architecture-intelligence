import tempfile
import unittest
from unittest.mock import patch

from utils import get_history_item, load_history, save_history


class StorageTests(unittest.TestCase):
    def test_structured_result_is_saved_for_impact_analysis(self):
        with tempfile.TemporaryDirectory() as directory, patch("utils.DATA_DIR", directory):
            analysis_id = save_history("student", "Booking app", {
                "report": "# Report", "analysis": {"traceability": {"nodes": [], "edges": []}}
            })
            records = load_history("student")
            self.assertEqual(records[0]["id"], analysis_id)
            self.assertIn("analysis", records[0]["result"])
            self.assertEqual(get_history_item("student", analysis_id)["project"], "Booking app")


if __name__ == "__main__":
    unittest.main()
