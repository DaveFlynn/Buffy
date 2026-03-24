import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buffy.formatting import build_caption, format_duration, truncate_text
from buffy.models import Playback, RatingInfo


class FormattingTests(unittest.TestCase):
    def test_format_duration(self) -> None:
        self.assertEqual(format_duration(90 * 60 * 1000), "1h 30m")
        self.assertEqual(format_duration(45 * 60 * 1000), "45m")
        self.assertEqual(format_duration(None), "Unknown")

    def test_build_caption_includes_core_fields(self) -> None:
        playback = Playback(
            session_id="abc",
            rating_key="1",
            media_type="movie",
            title="Arrival",
            year=2016,
            duration_ms=116 * 60 * 1000,
            summary="A linguist communicates with aliens.",
            user_name="Dave",
            player_name="Living Room TV",
            thumb_path="/library/metadata/1/thumb/1",
            grandparent_title=None,
            parent_index=None,
            media_index=None,
            imdb_id="tt2543164",
        )
        caption = build_caption(playback, RatingInfo(source="Rotten Tomatoes", value="94%"))
        self.assertIn("Arrival", caption)
        self.assertIn("Dave", caption)
        self.assertIn("1h 56m", caption)
        self.assertIn("Rotten Tomatoes", caption)

    def test_truncate_text(self) -> None:
        self.assertEqual(truncate_text("abc", 3), "abc")
        self.assertEqual(truncate_text("abcdef", 5), "ab...")


if __name__ == "__main__":
    unittest.main()
