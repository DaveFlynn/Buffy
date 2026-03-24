from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests

from buffy.models import Playback


class PlexClient:
    def __init__(self, base_url: str, token: str, session: requests.Session | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._session = session or requests.Session()

    def get_active_playbacks(self) -> list[Playback]:
        response = self._session.get(
            self._build_url("/status/sessions"),
            params={"X-Plex-Token": self._token},
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json().get("MediaContainer", {})
        videos = payload.get("Metadata", [])
        return [self._to_playback(video) for video in videos if self._is_currently_playing(video)]

    def fetch_artwork(self, thumb_path: str) -> bytes:
        response = self._session.get(
            self._build_url(thumb_path),
            params={"X-Plex-Token": self._token},
            timeout=20,
        )
        response.raise_for_status()
        return response.content

    def _build_url(self, path: str) -> str:
        return urljoin(f"{self._base_url}/", path.lstrip("/"))

    @staticmethod
    def _is_currently_playing(video: dict[str, Any]) -> bool:
        player = video.get("Player") or {}
        return player.get("state") == "playing" and video.get("type") in {"movie", "episode"}

    @staticmethod
    def _extract_imdb_id(video: dict[str, Any]) -> str | None:
        for guid in video.get("Guid", []):
            guid_id = guid.get("id")
            if isinstance(guid_id, str) and guid_id.startswith("imdb://"):
                return guid_id.removeprefix("imdb://")
        return None

    def _to_playback(self, video: dict[str, Any]) -> Playback:
        user = video.get("User") or {}
        player = video.get("Player") or {}
        session = video.get("Session") or {}
        session_id = session.get("id") or str(video.get("sessionKey") or video["ratingKey"])
        return Playback(
            session_id=str(session_id),
            rating_key=str(video["ratingKey"]),
            media_type=video["type"],
            title=video["title"],
            year=video.get("year"),
            duration_ms=video.get("duration"),
            summary=video.get("summary"),
            user_name=user.get("title") or "Unknown user",
            player_name=player.get("title"),
            thumb_path=video.get("thumb"),
            grandparent_title=video.get("grandparentTitle"),
            parent_index=video.get("parentIndex"),
            media_index=video.get("index"),
            imdb_id=self._extract_imdb_id(video),
        )
