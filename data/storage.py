from __future__ import annotations

from typing import Dict, Iterable, Optional


_known_users: Dict[int, str] = {}


def register_user(user_id: Optional[int], username: Optional[str] = None) -> None:
    if user_id is None:
        return
    handle = username or _known_users.get(user_id) or ""
    _known_users[user_id] = handle


def get_known_user_ids() -> Iterable[int]:
    return list(_known_users.keys())
