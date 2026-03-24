from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Playback:
    session_id: str
    rating_key: str
    media_type: str
    title: str
    year: int | None
    duration_ms: int | None
    summary: str | None
    user_name: str
    player_name: str | None
    thumb_path: str | None
    grandparent_title: str | None
    parent_index: int | None
    media_index: int | None
    imdb_id: str | None

    @property
    def display_title(self) -> str:
        if self.media_type != "episode":
            return self.title
        parts = []
        if self.grandparent_title:
            parts.append(self.grandparent_title)
        if self.parent_index is not None and self.media_index is not None:
            parts.append(f"S{self.parent_index:02d}E{self.media_index:02d}")
        parts.append(self.title)
        return " - ".join(parts)


@dataclass(frozen=True)
class RatingInfo:
    source: str
    value: str

