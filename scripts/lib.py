"""Pure helpers for the ai9s Herdr plugin."""

from __future__ import annotations

import shlex


def shell_command(name: str, args: list[str] | None) -> str:
    """Return one shell command Herdr can run in a new pane."""
    if not isinstance(name, str) or name == "" or name != name.strip():
        raise ValueError("missing command")
    if args is None:
        args = []
    if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
        raise ValueError("bad arguments")
    for part in [name, *args]:
        if _unsafe(part):
            raise ValueError("command contains a control character")
    return shlex.join([name, *args])


def tab_label(text: str) -> str:
    cleaned = "".join(ch for ch in (text or "") if not _unsafe(ch))
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > 48:
        cleaned = cleaned[:47].rstrip() + "…"
    return cleaned or "ai9s"


def decide(pane_id: str, alive: bool, focused: bool, same_tab: bool) -> tuple[str, str]:
    """Return close, focus, or open for the sidebar in this tab."""
    if pane_id and alive and same_tab:
        if focused:
            return "close", pane_id
        return "focus", pane_id
    return "open", ""


def plugin_pane_id(payload: dict) -> str:
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return ""
    plugin_pane = result.get("plugin_pane") or {}
    pane = plugin_pane.get("pane") if isinstance(plugin_pane, dict) else {}
    if not isinstance(pane, dict):
        return ""
    pane_id = pane.get("pane_id") or ""
    return pane_id if isinstance(pane_id, str) else ""


def created_pane_id(payload: dict) -> str:
    result = payload.get("result", payload)
    if not isinstance(result, dict):
        return ""
    pane = result.get("root_pane") or {}
    if not isinstance(pane, dict):
        return ""
    pane_id = pane.get("pane_id") or ""
    return pane_id if isinstance(pane_id, str) else ""


def pane_tab(payload: dict) -> tuple[str, bool]:
    result = payload.get("result", payload)
    pane = result.get("pane") if isinstance(result, dict) else None
    if not isinstance(pane, dict):
        return "", False
    tab_id = pane.get("tab_id") or ""
    focused = bool(pane.get("focused"))
    if not isinstance(tab_id, str):
        tab_id = ""
    return tab_id, focused


def _unsafe(text: str) -> bool:
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in text)
