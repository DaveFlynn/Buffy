from __future__ import annotations

from typing import Any

import requests

from buffy.models import Playback, RatingInfo


class OmdbClient:
    def __init__(self, api_key: str | None, session: requests.Session | None = None) -> None:
        self._api_key = api_key
        self._session = session or requests.Session()

    def lookup_rating(self, playback: Playback) -> RatingInfo | None:
        if not self._api_key:
            return None

        params: dict[str, Any] = {"apikey": self._api_key, "plot": "short"}
        if playback.imdb_id:
            params["i"] = playback.imdb_id
        else:
            params["t"] = playback.title
            if playback.year is not None:
                params["y"] = playback.year

        response = self._session.get("https://www.omdbapi.com/", params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        if payload.get("Response") != "True":
            return None

        for item in payload.get("Ratings", []):
            if item.get("Source") == "Rotten Tomatoes":
                return RatingInfo(source="Rotten Tomatoes", value=item["Value"])

        imdb_value = payload.get("imdbRating")
        if imdb_value and imdb_value != "N/A":
            return RatingInfo(source="IMDb", value=f"{imdb_value}/10")
        return None

