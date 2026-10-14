# herdr-ai9s

ai9s in a [Herdr](https://herdr.dev) sidebar. `prefix+i` toggles it. Enter on a session resumes that agent in a new tab of the current workspace. Enter on a harness starts that program in a new tab. The sidebar stays where it is.

This follows the same shape as [herdr-nvim](https://github.com/ChmaraX/herdr-nvim) and [herdr-gitview](https://github.com/ChmaraX/herdr-gitview): a `herdr-plugin.toml` manifest, one sidebar pane, and one action you bind yourself. Herdr does not bind plugin keys.

## Requirements

Herdr 0.8 or newer, Python 3, and `ai9s` on `PATH`. The sidebar prefers `~/.local/bin/ai9s` when that file exists. The installed ai9s needs `AI9S_HERDR_OPEN` support (`ai9s resume --json`).

## Install

From a local checkout:

```sh
herdr plugin link /path/to/herdr-ai9s
```

From GitHub, once the repository is public and tagged `herdr-plugin`:

```sh
herdr plugin install AymanZahran/herdr-ai9s
```

Bind a free prefix key in `~/.config/herdr/config.toml`. `prefix+e` is the nvim sidebar and `prefix+a` is Herdr's agent list, so this uses `prefix+i`:

```toml
[[keys.command]]
key = "prefix+i"
type = "plugin_action"
command = "aymanzahran.ai9s.toggle"
description = "ai9s sidebar"
```

Then `herdr server reload-config`. Press the prefix (`ctrl+a` on this machine), release it, then press `i`.

## What Enter does

Inside the sidebar, ai9s sets `AI9S_HERDR_OPEN` to `scripts/open_tab.py`.

- A session row runs `ai9s resume --json` and starts that command in a new tab, in the session directory. `y` passes `--yolo`.
- A harness row starts that program with no resume arguments. Herdr chooses the directory from the current tab.
- A directory, branch, or model row still pins that value inside the list.

Outside the sidebar, Enter resumes in the current terminal.

## Layout

```
herdr-plugin.toml
scripts/sidebar.sh    pane entrypoint
scripts/toggle.py     prefix action
scripts/open_tab.py   Enter hook
scripts/lib.py
tests/test_lib.py
```
