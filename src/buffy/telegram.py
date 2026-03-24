from __future__ import annotations

import requests


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str, session: requests.Session | None = None) -> None:
        self._chat_id = chat_id
        self._session = session or requests.Session()
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, caption: str) -> None:
        response = self._session.post(
            f"{self._base_url}/sendMessage",
            data={
                "chat_id": self._chat_id,
                "text": caption,
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
            },
            timeout=15,
        )
        response.raise_for_status()

    def send_photo(self, image_bytes: bytes, caption: str, filename: str = "poster.jpg") -> None:
        response = self._session.post(
            f"{self._base_url}/sendPhoto",
            data={"chat_id": self._chat_id, "caption": caption, "parse_mode": "HTML"},
            files={"photo": (filename, image_bytes)},
            timeout=30,
        )
        response.raise_for_status()

