#!/usr/bin/env python3
"""Open, focus, or close the ai9s sidebar in the current tab."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import decide, plugin_pane_id, target_pane  # noqa: E402

import subprocess


def main() -> int:
    herdr = os.environ.get("HERDR_BIN_PATH") or "herdr"
    plugin = os.environ.get("HERDR_PLUGIN_ID") or "aymanzahran.ai9s"
    context = plugin_context()
    workspace, tab = context_ids(context)
    if not workspace or not tab:
        notify(herdr, "Open the ai9s sidebar from inside a Herdr tab.")
        return 1
    state_path = state_file()
    saved = load_state(state_path).get(tab, "")
    alive = False
    focused = False
    same_tab = False
    if saved:
        payload, err = herdr_json(herdr, ["pane", "get", saved])
        if err is None and isinstance(payload, dict):
            result = payload.get("result", payload)
            pane = result.get("pane") if isinstance(result, dict) else None
            if isinstance(pane, dict) and pane.get("tab_id") == tab:
                alive = True
                same_tab = True
                focused = bool(pane.get("focused"))
    action, pane_id = decide(saved, alive, focused, same_tab)
    if action == "close":
        code, err = run(herdr, ["plugin", "pane", "close", pane_id])
        if code != 0:
            notify(herdr, err or "Could not close the ai9s sidebar.")
            return 1
        state = load_state(state_path)
        state.pop(tab, None)
        save_state(state_path, state)
        return 0
    if action == "focus":
        code, err = run(herdr, ["plugin", "pane", "focus", pane_id])
        if code != 0:
            notify(herdr, err or "Could not focus the ai9s sidebar.")
            return 1
        return 0
    # A split names the pane it divides. Herdr 0.9 rejects --workspace here:
    # "split and zoomed plugin panes target an existing pane".
    pane = target_pane(os.environ.get("HERDR_PANE_ID") or "", context)
    if not pane:
        notify(herdr, "Focus a Herdr pane, then open the ai9s sidebar.")
        return 1
    args = [
        "plugin", "pane", "open",
        "--plugin", plugin,
        "--entrypoint", "sidebar",
        "--placement", "split",
        "--target-pane", pane,
        "--direction", "right",
        "--focus",
    ]
    cwd = focused_cwd(context)
    if cwd:
        args.extend(["--cwd", cwd])
    payload, err = herdr_json(herdr, args)
    if err is not None or not isinstance(payload, dict):
        notify(herdr, err or "Could not open the ai9s sidebar.")
        return 1
    opened = plugin_pane_id(payload)
    if not opened:
        notify(herdr, "Herdr opened the sidebar without a pane id.")
        return 1
    state = load_state(state_path)
    state[tab] = opened
    save_state(state_path, state)
    return 0


def plugin_context() -> dict:
    raw = os.environ.get("HERDR_PLUGIN_CONTEXT_JSON") or ""
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def context_ids(context: dict) -> tuple[str, str]:
    workspace = os.environ.get("HERDR_WORKSPACE_ID") or ""
    tab = os.environ.get("HERDR_TAB_ID") or ""
    workspace = workspace or str(context.get("workspace_id") or "")
    tab = tab or str(context.get("tab_id") or "")
    return workspace.strip(), tab.strip()


def focused_cwd(context: dict) -> str:
    cwd = context.get("focused_pane_cwd") or context.get("workspace_cwd") or ""
    return cwd if isinstance(cwd, str) else ""


def state_file() -> Path:
    root = os.environ.get("HERDR_PLUGIN_STATE_DIR") or ""
    if not root:
        root = str(Path.home() / ".local" / "state" / "herdr-ai9s")
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path / "sidebars.json"


def load_state(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, str):
            out[key] = value
    return out


def save_state(path: Path, state: dict[str, str]) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n")


def herdr_json(herdr: str, args: list[str]) -> tuple[dict | None, str]:
    code, text, err = capture(herdr, args)
    if code != 0:
        return None, err
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None, "Herdr returned a response that is not JSON."
    if not isinstance(data, dict):
        return None, "Herdr returned an unexpected response."
    return data, ""


def run(herdr: str, args: list[str]) -> tuple[int, str]:
    code, _, err = capture(herdr, args)
    return code, err


def capture(herdr: str, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run([herdr, *args], capture_output=True, text=True)
    err = (proc.stderr or proc.stdout or "").strip()
    if err:
        err = err.splitlines()[-1][:300]
    return proc.returncode, proc.stdout, err


def notify(herdr: str, body: str) -> None:
    subprocess.run(
        [herdr, "notification", "show", "ai9s", "--body", body[:300]],
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        notify(os.environ.get("HERDR_BIN_PATH") or "herdr", str(exc))
        print(exc, file=sys.stderr)
        raise SystemExit(1)
