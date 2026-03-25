from __future__ import annotations

import logging
import time

import requests

from buffy.config import load_settings
from buffy.formatting import build_caption, truncate_text
from buffy.models import Playback
from buffy.omdb import OmdbClient
from buffy.plex import PlexClient
from buffy.state import ActiveSessionStore, NotificationState
from buffy.telegram import TelegramClient

LOGGER = logging.getLogger(__name__)


def _notification_key(playback: Playback) -> str:
    return f"{playback.user_name}:{playback.rating_key}"


def _prune_recent_notifications(
    recent_notification_times: dict[str, float],
    suppression_minutes: int | None,
    now: float,
) -> dict[str, float]:
    if suppression_minutes is None:
        return {}

    cutoff = now - (suppression_minutes * 60)
    return {
        key: notified_at
        for key, notified_at in recent_notification_times.items()
        if notified_at >= cutoff
    }


def _prune_pending_sessions(
    pending_session_times: dict[str, float],
    current_session_ids: set[str],
) -> dict[str, float]:
    return {
        session_id: first_seen_at
        for session_id, first_seen_at in pending_session_times.items()
        if session_id in current_session_ids
    }


def _delay_elapsed(first_seen_at: float, delay_minutes: int | None, now: float) -> bool:
    if delay_minutes is None:
        return True
    return now - first_seen_at >= (delay_minutes * 60)


def run() -> None:
    settings = load_settings()
    plex_client = PlexClient(settings.plex_base_url, settings.plex_token)
    telegram_client = TelegramClient(settings.telegram_bot_token, settings.telegram_chat_id)
    omdb_client = OmdbClient(settings.omdb_api_key)
    state_store = ActiveSessionStore(settings.state_file)
    notification_state = state_store.load()

    while True:
        try:
            now = time.time()
            playbacks = plex_client.get_active_playbacks()
            current_session_ids = {playback.session_id for playback in playbacks}
            recent_notification_times = _prune_recent_notifications(
                notification_state.recent_notification_times,
                settings.repeat_play_suppression_minutes,
                now,
            )
            pending_session_times = _prune_pending_sessions(
                notification_state.pending_session_times,
                current_session_ids,
            )
            next_active_session_ids = {
                session_id
                for session_id in notification_state.active_session_ids
                if session_id in current_session_ids
            }

            for playback in playbacks:
                if playback.session_id in next_active_session_ids:
                    continue

                first_seen_at = pending_session_times.setdefault(playback.session_id, now)
                if not _delay_elapsed(first_seen_at, settings.notification_delay_minutes, now):
                    LOGGER.info(
                        "Notification delay active for %s by %s",
                        playback.display_title,
                        playback.user_name,
                    )
                    continue

                notification_key = _notification_key(playback)
                if (
                    settings.repeat_play_suppression_minutes is not None
                    and notification_key in recent_notification_times
                ):
                    LOGGER.info(
                        "Repeat playback suppressed for %s by %s",
                        playback.display_title,
                        playback.user_name,
                    )
                    pending_session_times.pop(playback.session_id, None)
                    next_active_session_ids.add(playback.session_id)
                    continue

                LOGGER.info("New playback detected for %s by %s", playback.display_title, playback.user_name)
                rating = omdb_client.lookup_rating(playback)
                caption = build_caption(playback, rating)

                if playback.thumb_path:
                    try:
                        image_bytes = plex_client.fetch_artwork(playback.thumb_path)
                    except requests.HTTPError as exc:
                        status_code = exc.response.status_code if exc.response is not None else None
                        if status_code not in {401, 403, 404}:
                            raise
                        LOGGER.warning(
                            "Poster fetch failed for rating_key=%s with status=%s; falling back to text message",
                            playback.rating_key,
                            status_code,
                        )
                        telegram_client.send_message(truncate_text(caption, 4096))
                    else:
                        telegram_client.send_photo(
                            image_bytes=image_bytes,
                            caption=truncate_text(caption, 1024),
                        )
                else:
                    telegram_client.send_message(truncate_text(caption, 4096))

                if settings.repeat_play_suppression_minutes is not None:
                    recent_notification_times[notification_key] = now
                pending_session_times.pop(playback.session_id, None)
                next_active_session_ids.add(playback.session_id)

            notification_state = NotificationState(
                active_session_ids=next_active_session_ids,
                recent_notification_times=recent_notification_times,
                pending_session_times=pending_session_times,
            )
            state_store.save(notification_state)
        except requests.RequestException:
            LOGGER.exception("Polling failed; retrying after %s seconds", settings.poll_interval_seconds)

        time.sleep(settings.poll_interval_seconds)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run()
