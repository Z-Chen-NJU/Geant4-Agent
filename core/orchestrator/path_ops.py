from __future__ import annotations

from copy import deepcopy
from typing import Any


def get_path(data: dict, path: str, default: Any = None) -> Any:
    cur: Any = data
    for token in path.split("."):
        if not isinstance(cur, dict) or token not in cur:
            return default
        cur = cur[token]
    return cur


def set_path(data: dict, path: str, value: Any) -> None:
    cur = data
    tokens = path.split(".")
    for token in tokens[:-1]:
        nxt = cur.get(token)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[token] = nxt
        cur = nxt
    cur[tokens[-1]] = value


def remove_path(data: dict, path: str) -> None:
    cur = data
    tokens = path.split(".")
    for token in tokens[:-1]:
        nxt = cur.get(token)
        if not isinstance(nxt, dict):
            return
        cur = nxt
    cur.pop(tokens[-1], None)


def flatten(data: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            p = f"{prefix}.{key}" if prefix else key
            out.update(flatten(value, p))
    else:
        out[prefix] = data
    return out


def diff_paths(before: dict, after: dict) -> list[str]:
    b = flatten(before)
    a = flatten(after)
    changed: list[str] = []
    for key in sorted(set(b.keys()) | set(a.keys())):
        if b.get(key) != a.get(key):
            changed.append(key)
    return changed


def deep_copy(data: dict) -> dict:
    return deepcopy(data)
