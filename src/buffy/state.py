from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NotificationState:
    active_session_ids: set[str]
    recent_notification_times: dict[str, float]
    pending_session_times: dict[str, float]


@dataclass
class ActiveSessionStore:
    path: Path

    def load(self) -> NotificationState:
        if not self.path.exists():
            return NotificationState(
                active_session_ids=set(),
                recent_notification_times={},
                pending_session_times={},
            )
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        session_ids = payload.get("active_session_ids", [])
        recent_notification_times = payload.get("recent_notification_times", {})
        pending_session_times = payload.get("pending_session_times", {})
        return NotificationState(
            active_session_ids={str(item) for item in session_ids},
            recent_notification_times={
                str(key): float(value) for key, value in recent_notification_times.items()
            },
            pending_session_times={
                str(key): float(value) for key, value in pending_session_times.items()
            },
        )

    def save(self, state: NotificationState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "active_session_ids": sorted(state.active_session_ids),
            "recent_notification_times": state.recent_notification_times,
            "pending_session_times": state.pending_session_times,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
