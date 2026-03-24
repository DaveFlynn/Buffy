from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ActiveSessionStore:
    path: Path

    def load(self) -> set[str]:
        if not self.path.exists():
            return set()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        session_ids = payload.get("active_session_ids", [])
        return {str(item) for item in session_ids}

    def save(self, session_ids: set[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"active_session_ids": sorted(session_ids)}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

