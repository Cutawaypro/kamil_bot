from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


_STORAGE_FILE = Path(__file__).resolve().parent / "audits.json"


def _ensure_file() -> None:
    if not _STORAGE_FILE.exists():
        _STORAGE_FILE.write_text("[]", encoding="utf-8")


def load_audits() -> List[Dict[str, Any]]:
    _ensure_file()
    try:
        data = json.loads(_STORAGE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    if not isinstance(data, list):
        data = []
    return deepcopy(data)


def _write_audits(audits: List[Dict[str, Any]]) -> None:
    _STORAGE_FILE.write_text(json.dumps(audits, ensure_ascii=False, indent=2), encoding="utf-8")


def save_audit(audit: Dict[str, Any]) -> None:
    audits = load_audits()
    payload = deepcopy(audit)
    payload.setdefault("timestamp", datetime.utcnow().isoformat())
    audits.append(payload)
    _write_audits(audits)


def remove_audit(index: int) -> None:
    audits = load_audits()
    if 0 <= index < len(audits):
        audits.pop(index)
        _write_audits(audits)
