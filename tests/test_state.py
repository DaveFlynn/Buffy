import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buffy.state import ActiveSessionStore


class StateStoreTests(unittest.TestCase):
    def test_save_and_load_active_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            store = ActiveSessionStore(path)
            store.save({"session-2", "session-1"})
            self.assertEqual(store.load(), {"session-1", "session-2"})


if __name__ == "__main__":
    unittest.main()
