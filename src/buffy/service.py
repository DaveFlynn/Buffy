from __future__ import annotations

import logging
import time

import requests

from buffy.config import load_settings
from buffy.formatting import build_caption, truncate_text
from buffy.omdb import OmdbClient
from buffy.plex import PlexClient
from buffy.state import ActiveSessionStore
from buffy.telegram import TelegramClient

LOGGER = logging.getLogger(__name__)


def run() -> None:
    settings = load_settings()
    plex_client = PlexClient(settings.plex_base_url, settings.plex_token)
    telegram_client = TelegramClient(settings.telegram_bot_token, settings.telegram_chat_id)
    omdb_client = OmdbClient(settings.omdb_api_key)
    state_store = ActiveSessionStore(settings.state_file)
    active_session_ids = state_store.load()

    while True:
        try:
            playbacks = plex_client.get_active_playbacks()
            current_session_ids = {playback.session_id for playback in playbacks}

            for playback in playbacks:
                if playback.session_id in active_session_ids:
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

            active_session_ids = current_session_ids
            state_store.save(active_session_ids)
        except requests.RequestException:
            LOGGER.exception("Polling failed; retrying after %s seconds", settings.poll_interval_seconds)

        time.sleep(settings.poll_interval_seconds)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run()
