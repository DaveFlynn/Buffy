from __future__ import annotations

from html import escape

from buffy.models import Playback, RatingInfo


def format_duration(duration_ms: int | None) -> str:
    if duration_ms is None:
        return "Unknown"
    total_minutes = duration_ms // 60000
    hours, minutes = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def build_caption(playback: Playback, rating: RatingInfo | None) -> str:
    lines = [
        "<b>Plex playback started</b>",
        f"<b>Title:</b> {escape(playback.display_title)}",
        f"<b>User:</b> {escape(playback.user_name)}",
    ]
    if playback.player_name:
        lines.append(f"<b>Player:</b> {escape(playback.player_name)}")
    if playback.year is not None:
        lines.append(f"<b>Year:</b> {playback.year}")
    lines.append(f"<b>Length:</b> {format_duration(playback.duration_ms)}")
    if rating is not None:
        lines.append(f"<b>{escape(rating.source)}:</b> {escape(rating.value)}")
    if playback.summary:
        lines.append("")
        lines.append(escape(playback.summary))
    return "\n".join(lines)


def truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3].rstrip() + "..."
