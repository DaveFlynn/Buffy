import unittest
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

requests_stub = types.ModuleType("requests")
requests_stub.RequestException = Exception
requests_stub.HTTPError = Exception
requests_stub.Session = object
sys.modules.setdefault("requests", requests_stub)

from buffy.models import Playback
from buffy.service import (
    _delay_elapsed,
    _notification_key,
    _prune_pending_sessions,
    _prune_recent_notifications,
)


class ServiceTests(unittest.TestCase):
    def test_notification_key_uses_same_user_and_video(self) -> None:
        playback = Playback(
            session_id="abc",
            rating_key="123",
            media_type="movie",
            title="Arrival",
            year=2016,
            duration_ms=None,
            summary=None,
            user_name="Dave",
            player_name=None,
            thumb_path=None,
            grandparent_title=None,
            parent_index=None,
            media_index=None,
            imdb_id=None,
        )
        self.assertEqual(_notification_key(playback), "Dave:123")

    def test_prune_recent_notifications_clears_history_when_disabled(self) -> None:
        self.assertEqual(
            _prune_recent_notifications({"Dave:123": 100.0}, None, now=200.0),
            {},
        )

    def test_prune_recent_notifications_keeps_only_entries_inside_window(self) -> None:
        self.assertEqual(
            _prune_recent_notifications(
                {"Dave:123": 100.0, "Dave:456": 170.0},
                suppression_minutes=1,
                now=200.0,
            ),
            {"Dave:456": 170.0},
        )

    def test_prune_pending_sessions_drops_inactive_sessions(self) -> None:
        self.assertEqual(
            _prune_pending_sessions(
                {"session-1": 100.0, "session-2": 110.0},
                {"session-2"},
            ),
            {"session-2": 110.0},
        )

    def test_delay_elapsed_defaults_to_immediate_when_disabled(self) -> None:
        self.assertTrue(_delay_elapsed(100.0, None, 100.0))

    def test_delay_elapsed_waits_until_threshold(self) -> None:
        self.assertFalse(_delay_elapsed(100.0, 2, 200.0))
        self.assertTrue(_delay_elapsed(100.0, 2, 220.0))


if __name__ == "__main__":
    unittest.main()
