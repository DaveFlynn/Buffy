from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    plex_base_url: str
    plex_token: str
    telegram_bot_token: str
    telegram_chat_id: str
    omdb_api_key: str | None
    poll_interval_seconds: int
    state_file: Path


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")
        if not separator:
            raise RuntimeError(f"Invalid line in {env_path}: {raw_line}")

        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ.setdefault(key, value)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        plex_base_url=_require_env("PLEX_BASE_URL").rstrip("/"),
        plex_token=_require_env("PLEX_TOKEN"),
        telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_require_env("TELEGRAM_CHAT_ID"),
        omdb_api_key=os.getenv("OMDB_API_KEY") or None,
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "15")),
        state_file=Path(os.getenv("STATE_FILE", ".state/active_sessions.json")),
    )
