import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from buffy.config import load_dotenv


class DotenvTests(unittest.TestCase):
    def test_load_dotenv_sets_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "PLEX_BASE_URL=http://plex.local:32400\nTELEGRAM_CHAT_ID='-100123'\n",
                encoding="utf-8",
            )

            original_plex = os.environ.pop("PLEX_BASE_URL", None)
            original_chat = os.environ.pop("TELEGRAM_CHAT_ID", None)
            try:
                load_dotenv(env_path)
                self.assertEqual(os.environ["PLEX_BASE_URL"], "http://plex.local:32400")
                self.assertEqual(os.environ["TELEGRAM_CHAT_ID"], "-100123")
            finally:
                if original_plex is None:
                    os.environ.pop("PLEX_BASE_URL", None)
                else:
                    os.environ["PLEX_BASE_URL"] = original_plex
                if original_chat is None:
                    os.environ.pop("TELEGRAM_CHAT_ID", None)
                else:
                    os.environ["TELEGRAM_CHAT_ID"] = original_chat

    def test_load_dotenv_does_not_override_existing_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("PLEX_TOKEN=file-token\n", encoding="utf-8")

            original = os.environ.get("PLEX_TOKEN")
            os.environ["PLEX_TOKEN"] = "existing-token"
            try:
                load_dotenv(env_path)
                self.assertEqual(os.environ["PLEX_TOKEN"], "existing-token")
            finally:
                if original is None:
                    os.environ.pop("PLEX_TOKEN", None)
                else:
                    os.environ["PLEX_TOKEN"] = original

    def test_load_dotenv_sets_optional_repeat_suppression_minutes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("REPEAT_PLAY_SUPPRESSION_MINUTES=10\n", encoding="utf-8")

            original = os.environ.pop("REPEAT_PLAY_SUPPRESSION_MINUTES", None)
            try:
                load_dotenv(env_path)
                self.assertEqual(os.environ["REPEAT_PLAY_SUPPRESSION_MINUTES"], "10")
            finally:
                if original is None:
                    os.environ.pop("REPEAT_PLAY_SUPPRESSION_MINUTES", None)
                else:
                    os.environ["REPEAT_PLAY_SUPPRESSION_MINUTES"] = original

    def test_load_dotenv_sets_optional_notification_delay_minutes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("NOTIFICATION_DELAY_MINUTES=2\n", encoding="utf-8")

            original = os.environ.pop("NOTIFICATION_DELAY_MINUTES", None)
            try:
                load_dotenv(env_path)
                self.assertEqual(os.environ["NOTIFICATION_DELAY_MINUTES"], "2")
            finally:
                if original is None:
                    os.environ.pop("NOTIFICATION_DELAY_MINUTES", None)
                else:
                    os.environ["NOTIFICATION_DELAY_MINUTES"] = original


if __name__ == "__main__":
    unittest.main()
