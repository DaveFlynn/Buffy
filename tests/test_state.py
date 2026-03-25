import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buffy.state import ActiveSessionStore, NotificationState


class StateStoreTests(unittest.TestCase):
    def test_save_and_load_active_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            store = ActiveSessionStore(path)
            store.save(
                NotificationState(
                    active_session_ids={"session-2", "session-1"},
                    recent_notification_times={"Dave:123": 100.0},
                    pending_session_times={"session-2": 90.0},
                )
            )
            state = store.load()
            self.assertEqual(state.active_session_ids, {"session-1", "session-2"})
            self.assertEqual(state.recent_notification_times, {"Dave:123": 100.0})
            self.assertEqual(state.pending_session_times, {"session-2": 90.0})

    def test_load_old_state_file_without_recent_notification_times(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            path.write_text('{"active_session_ids": ["session-1"]}', encoding="utf-8")
            store = ActiveSessionStore(path)
            state = store.load()
            self.assertEqual(state.active_session_ids, {"session-1"})
            self.assertEqual(state.recent_notification_times, {})
            self.assertEqual(state.pending_session_times, {})


if __name__ == "__main__":
    unittest.main()
