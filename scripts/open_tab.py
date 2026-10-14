#!/usr/bin/env python3
"""Open the selected ai9s row in a new tab of the current workspace."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import created_pane_id, shell_command, tab_label  # noqa: E402


def main() -> int:
    herdr = os.environ.get("HERDR_BIN_PATH") or "herdr"
    workspace = (os.environ.get("HERDR_WORKSPACE_ID") or "").strip()
    if not workspace:
        notify(herdr, "Select a row from the ai9s sidebar inside Herdr.")
        return 1
    try:
        command, cwd, label = plan()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        notify(herdr, str(exc))
        return 1
    args = ["tab", "create", "--workspace", workspace, "--label", label, "--focus"]
    if cwd:
        args.extend(["--cwd", cwd])
    payload, err = herdr_json(herdr, args)
    if err or not isinstance(payload, dict):
        notify(herdr, err or "Could not open a tab.")
        return 1
    pane_id = created_pane_id(payload)
    if not pane_id:
        notify(herdr, "Herdr created a tab without a pane id.")
        return 1
    code, run_err = run(herdr, ["pane", "run", pane_id, command])
    if code != 0:
        notify(herdr, run_err or "Could not start the agent.")
        return 1
    return 0


def plan() -> tuple[str, str, str]:
    session_id = (os.environ.get("AI9S_ID") or "").strip()
    label = tab_label(os.environ.get("AI9S_LABEL") or os.environ.get("AI9S_HARNESS") or "")
    if session_id:
        if _unsafe(session_id):
            raise ValueError("The session id contains a control character.")
        ai9s = shutil.which("ai9s")
        if not ai9s:
            raise ValueError("ai9s is not on PATH.")
        args = [ai9s, "resume", "--json"]
        if os.environ.get("AI9S_YOLO") == "1":
            args.append("--yolo")
        args.append(session_id)
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stderr or "ai9s could not plan that resume.").strip().splitlines()
            raise ValueError(detail[-1][:300] if detail else "ai9s could not plan that resume.")
        data = json.loads(proc.stdout)
        if not isinstance(data, dict):
            raise ValueError("ai9s resume --json returned an unexpected response.")
        name = data.get("name") or ""
        argv = data.get("args") or []
        cwd = data.get("dir") or os.environ.get("AI9S_CWD") or ""
        if not isinstance(cwd, str):
            cwd = ""
        return shell_command(name, argv), cwd, label
    binary = (os.environ.get("AI9S_BIN") or "").strip()
    return shell_command(binary, []), "", label


def _unsafe(text: str) -> bool:
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in text)


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
