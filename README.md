# herdr-ai9s

[![CI](https://github.com/AymanZahran/herdr-ai9s/actions/workflows/ci.yml/badge.svg)](https://github.com/AymanZahran/herdr-ai9s/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/AymanZahran/herdr-ai9s)](https://github.com/AymanZahran/herdr-ai9s/releases)
[![License: MIT](https://img.shields.io/github/license/AymanZahran/herdr-ai9s)](LICENSE)

[ai9s](https://ai9scli.io) in a [Herdr](https://herdr.dev) sidebar. One prefix key opens the session finder on the right of the current tab. Enter on a session or a harness starts that program in a **new tab of the same workspace** and focuses the new tab. The sidebar stays in the tab you were already in.

This is the same shape as [herdr-nvim](https://github.com/ChmaraX/herdr-nvim) and [herdr-gitview](https://github.com/ChmaraX/herdr-gitview): a `herdr-plugin.toml` manifest, one sidebar pane, and one action you bind yourself. Herdr does not bind plugin keys.

[Install](#install) · [Key](#key-binding) · [Sidebar](#the-sidebar) · [Enter](#opening-a-row) · [Labels](#tab-labels) · [Environment](#environment) · [Troubleshooting](#troubleshooting)

## Features

- **Sidebar per tab.** `prefix+i` opens ai9s in a right-hand split, focuses it when it is already open, or closes it when it already has focus. Each tab keeps its own sidebar.
- **Enter leaves the list.** A session row resumes that session in a new tab, in the session's directory. A harness row starts that program in a new tab. Focus moves to the new tab. The finder stays open behind you.
- **The list still filters.** Enter on a directory, branch, or model pins that row inside ai9s. Those views do not open a tab.
- **Yolo is the same key.** `y` on a session asks ai9s for the auto-approve resume, when that harness has one, and starts it in the new tab.

## Requirements

| Tool | Version |
| --- | --- |
| [Herdr](https://herdr.dev/docs/install/) | 0.8.0 or newer (`min_herdr_version` in the manifest). Developed against 0.9.3. |
| [ai9s](https://github.com/AymanZahran/ai9s) | 1.0.8 or newer. That release adds `AI9S_HERDR_OPEN` and `ai9s resume --json`. |
| Python | 3.10 or newer. The standard library is enough. |
| Platform | macOS or Linux. |

`ai9s` must be on `PATH` inside the sidebar. When `$HOME/.local/bin/ai9s` exists and is executable, the sidebar puts `$HOME/.local/bin` in front of `PATH`, so a user install is the one that runs.

## Install

From GitHub:

```sh
herdr plugin install AymanZahran/herdr-ai9s
```

Herdr clones the default branch, shows the manifest and the commands it will run, and registers plugin id `aymanzahran.ai9s`. Confirm the preview. Add `--yes` only when you already trust this repository. Pin this release with `--ref v0.1.0`.

The GitHub topic `herdr-plugin` is what lists the repository in the [Herdr marketplace](https://herdr.dev/plugins/). It is a topic, not a git tag. Install does not require a tag named `herdr-plugin`.

Update a GitHub install with:

```sh
herdr plugin update aymanzahran.ai9s
```

A later `herdr plugin install AymanZahran/herdr-ai9s` also replaces the managed checkout. Config and state directories survive both.

From a local checkout, while you are changing the plugin:

```sh
git clone https://github.com/AymanZahran/herdr-ai9s.git
cd herdr-ai9s
herdr plugin link "$PWD"
```

`plugin link` does not run a build. Herdr refuses to install from GitHub over a plugin that is still linked. Unlink or uninstall the linked copy first:

```sh
herdr plugin unlink aymanzahran.ai9s
```

Check that the action is registered:

```sh
herdr plugin action list --plugin aymanzahran.ai9s
```

You should see `aymanzahran.ai9s.toggle`.

## Key binding

Add this to `~/.config/herdr/config.toml`. The suggested key is `prefix+i`:

```toml
# Toggle the ai9s finder. Enter in that pane opens the row in a new tab.
[[keys.command]]
key = "prefix+i"
type = "plugin_action"
command = "aymanzahran.ai9s.toggle"
description = "ai9s sidebar"
```

Reload Herdr:

```sh
herdr server reload-config
```

Press the prefix, release it, then press `i`. On a setup whose prefix is `ctrl+a`, that is Ctrl-a, then i.

`prefix+i` is free in the usual Herdr layout. These keys are already taken by Herdr or by the plugins this one sits next to:

| Key | Owner |
| --- | --- |
| `prefix+e` | herdr-nvim sidebar |
| `prefix+shift+f` | herdr-nvim file picker, on some configs |
| `prefix+a` | Herdr agent list |
| `prefix+\` | Herdr workspace sidebar |
| `prefix+ctrl+g` | herdr-gitview sidebar |
| `prefix+ctrl+shift+g` | herdr-gitview tab |

Any other free key works. Change `key` and keep `command = "aymanzahran.ai9s.toggle"`.

## Quick start

1. Install ai9s 1.0.8 or newer and confirm `ai9s version` prints that version. A copy that is already running keeps its old binary until you quit it and start it again.
2. Install or link this plugin.
3. Bind `prefix+i` and reload the Herdr config.
4. From a Herdr tab, press the prefix, then `i`. ai9s opens on the right.
5. Move to a session and press Enter. A new tab in this workspace starts that agent and takes focus. Press the prefix, then the previous tab's number, to return to the finder.
6. Press the prefix, then `i`, while the sidebar is focused, to close it.

## The sidebar

The action id is `toggle`. Herdr runs `python3 scripts/toggle.py` with the plugin directory as the working directory.

The script looks up this tab in its state file, then asks Herdr whether that pane is still alive:

| Saved pane | Result |
| --- | --- |
| Missing, closed, or living in another tab | Open a new right-hand split in this workspace, focus it, and remember its pane id. |
| Alive in this tab, and some other pane is focused | Focus the sidebar. |
| Alive in this tab, and the sidebar is focused | Close the sidebar and forget the pane id. |

The open command is:

```text
herdr plugin pane open \
  --plugin aymanzahran.ai9s \
  --entrypoint sidebar \
  --placement split \
  --direction right \
  --focus \
  --workspace "$HERDR_WORKSPACE_ID" \
  --cwd "$CWD"
```

`$CWD` is `focused_pane_cwd` from `HERDR_PLUGIN_CONTEXT_JSON`, or `workspace_cwd` when the focused pane has no directory. The flag is omitted when both are empty.

The pane entrypoint is `sidebar`. Its command is a shell one-liner because Herdr starts pane commands in the project directory, not in the plugin directory:

```toml
command = ["sh", "-c", "exec \"$HERDR_PLUGIN_ROOT/scripts/sidebar.sh\""]
```

`scripts/sidebar.sh` exports `AI9S_HERDR_OPEN` to `scripts/open_tab.py`, prefers `$HOME/.local/bin/ai9s`, and replaces itself with `ai9s`. The finder is a real terminal. Its own keys (`/`, `1` through `6`, `y`, `?`, and the rest) are ai9s keys. This plugin adds the Enter hook and the toggle.

Closing the split from Herdr's pane close, rather than from the toggle, leaves a stale pane id in the state file. The next toggle sees that the pane is gone and opens a fresh sidebar.

## Which sessions you see

ai9s limits the list to the directory it was started in, and to children of that directory, whenever that directory is not your home directory. The sidebar starts in the focused pane's directory, so a sidebar opened from a project tab lists sessions under that project.

Open the sidebar from a pane whose directory is your home directory when you want every indexed session. `ai9s search` on a shell still searches the whole index. That command is separate from the sidebar list.

A new ai9s process reads the index when it starts. Quit the sidebar and toggle it open again after you upgrade the `ai9s` binary. An already-open finder keeps the binary it started with.

## Opening a row

Inside the sidebar, ai9s sees `AI9S_HERDR_OPEN`. Enter on a session or a harness starts `scripts/open_tab.py` in the background and leaves the list on screen. ai9s does not suspend and does not resume in the sidebar pane.

`open_tab.py` refuses to run without `HERDR_WORKSPACE_ID`, so the hook only opens a tab from inside Herdr.

### Session

1. ai9s plans the resume with `act.Plan` and passes the result to the hook. `AI9S_ID` is the ai9s session id. `AI9S_YOLO` is `1` when you pressed `y`, and `0` when you pressed Enter.
2. The hook runs `ai9s resume --json` for that id, plus `--yolo` when `AI9S_YOLO` is `1`. `--json` prints the command and does not run it:

   ```json
   {"name": "/path/to/claude", "args": ["--resume", "…"], "dir": "/path/to/repo"}
   ```

   `name` is the full path ai9s resolved. `args` is `[]` when the plan has no arguments. `dir` is the session directory.
3. The hook creates a tab in `HERDR_WORKSPACE_ID` with that directory, a short label, and focus.
4. `herdr pane run` submits one shell string to the new pane. Arguments are quoted with Python `shlex`, so a session id that contains spaces stays one argument.

The shell string is the plan. A Claude session becomes a `claude --resume` invocation. Other harnesses use the flags ai9s already knows (Pi `--session`, OMP `--resume=<id>`, and the rest). This plugin does not keep its own copy of that table.

### Harness

Enter on the harness list (`2` in ai9s) starts the installed program with no resume arguments. ai9s sends an empty `AI9S_ID` and an empty `AI9S_CWD`. `AI9S_BIN` is the program name ai9s found on `PATH` (`claude`, `agy`, `cursor-agent`, and so on). The new tab is created without a directory, and Herdr applies the working directory it uses for a new tab. The shell string is that program name alone.

A harness that is not on `PATH` never reaches the hook. ai9s reports that in the list.

### Rows that stay in the list

Enter on a directory, a branch, or a model still pins that value and returns to the session list. `y` on a harness does the same thing `y` does in a normal ai9s: it asks you to switch to sessions before resuming. An empty session selection consumes Enter and does not open a tab.

Outside the sidebar, `AI9S_HERDR_OPEN` is unset. Enter resumes in the current terminal, and quitting the agent returns to the list.

## Tab labels

ai9s builds `AI9S_LABEL` before it starts the hook.

| Row | Label |
| --- | --- |
| Session with a name set in ai9s (`n`) | Harness display name, a middle dot, then that name. Example shape: `Claude Code · api`. |
| Session with no name | Harness display name. |
| Harness row | Harness display name. |

The name is the name stored in ai9s. Transcript titles are not tab labels.

The hook then cleans the label: control characters and DEL are removed, runs of whitespace collapse to one space, and a label longer than 48 characters is cut to 47 characters plus `…`. An empty result becomes `ai9s`. The same cleaning applies when the hook falls back to `AI9S_HARNESS`.

## Yolo

Press `y` on a session in the sidebar. ai9s sets `AI9S_YOLO=1`, plans the auto-approve command, and the hook asks `ai9s resume --json --yolo` for that same command. The new tab runs it.

ai9s adds an auto-approve flag only for harnesses that have one. The 1.0.8 set includes OMP `--auto-approve`, Devin `--permission-mode dangerous`, Kilo `--auto`, Qoder `--dangerously-skip-permissions`, and Maki `--yolo`, plus the flags the earlier harnesses already used. Codex, Pi, Droid, Letta, MastraCode, and Amp have no auto-approve flag, so `y` and Enter plan the same arguments for those rows. The live list is the ai9s README.

## Environment

ai9s strips control characters from hook values with `VisibleLine` before the hook starts. The hook rejects a session id, a program name, or an argument that still contains a byte below 32 or DEL.

### Set by the sidebar

| Variable | Value |
| --- | --- |
| `AI9S_HERDR_OPEN` | Absolute path of `scripts/open_tab.py`. ai9s runs this program on Enter. |
| `AI9S_HERDR_SIDEBAR` | `1`. Marker for the sidebar process. Current ai9s builds do not read it. |
| `PATH` | `$HOME/.local/bin` prepended when `$HOME/.local/bin/ai9s` is executable. |

### Set by ai9s for a session

| Variable | Meaning |
| --- | --- |
| `AI9S_ID` | ai9s session id. The hook passes this to `ai9s resume`. |
| `AI9S_NATIVE_ID` | Harness-native id. The hook does not read it. `ai9s resume` does. |
| `AI9S_AGENT` | Harness id, such as `claude` or `kilo`. |
| `AI9S_HARNESS` | Display name, such as `Claude Code` or `Kilo Code`. |
| `AI9S_BIN` | Full path of the program `ai9s resume` will run. |
| `AI9S_CWD` | Session directory. Used when the JSON plan has no `dir`. |
| `AI9S_LABEL` | Tab label described above. |
| `AI9S_YOLO` | `1` or `0`. |

### Set by ai9s for a harness row

`AI9S_ID` and `AI9S_CWD` are empty. `AI9S_BIN` is the program name on `PATH`. `AI9S_LABEL` and `AI9S_HARNESS` are the display name. `AI9S_YOLO` is `0`. `AI9S_NATIVE_ID` is unset.

### Read from Herdr

| Variable | Use |
| --- | --- |
| `HERDR_BIN_PATH` | Herdr binary. Falls back to `herdr` on `PATH`. |
| `HERDR_PLUGIN_ID` | Plugin id. Falls back to `aymanzahran.ai9s`. |
| `HERDR_PLUGIN_ROOT` | Installed or linked plugin directory. The pane command finds `sidebar.sh` here. |
| `HERDR_PLUGIN_STATE_DIR` | Directory for `sidebars.json`. |
| `HERDR_WORKSPACE_ID` | Workspace that receives the new tab, and the sidebar split. |
| `HERDR_TAB_ID` | Tab whose sidebar is toggled. |
| `HERDR_PLUGIN_CONTEXT_JSON` | Fills in workspace id, tab id, `focused_pane_cwd`, and `workspace_cwd` when the matching variable is empty. |

Herdr also injects `HERDR_SOCKET_PATH`, `HERDR_ENV`, `HERDR_PLUGIN_CONFIG_DIR`, `HERDR_PANE_ID`, and `HERDR_PLUGIN_ACTION_ID`. This plugin does not read those.

## Notifications

Failures raise a Herdr notification titled `ai9s`. The body is the error text, capped at 300 characters. The hook does not put session titles or prompts in that body.

| Situation | What you see |
| --- | --- |
| Toggle used outside a Herdr tab | "Open the ai9s sidebar from inside a Herdr tab." |
| Herdr could not open, focus, or close the split | The last line Herdr printed, or a short fallback sentence. |
| Enter while the hook has no workspace id | "Select a row from the ai9s sidebar inside Herdr." |
| `ai9s` missing from `PATH` | "ai9s is not on PATH." |
| `ai9s resume --json` failed | The last line of its stderr. |
| The plan contains a control character | The hook stops before it asks Herdr to run anything. |
| Tab create or pane run failed | The last line Herdr printed. |

A resume ai9s itself rejects (unknown id, unsafe path, missing binary) is reported by ai9s in the sidebar, and the hook is not started.

## State

The toggle stores one pane id per tab:

```text
$HERDR_PLUGIN_STATE_DIR/sidebars.json
```

When `HERDR_PLUGIN_STATE_DIR` is unset, the file is `$HOME/.local/state/herdr-ai9s/sidebars.json`. The JSON object maps a Herdr tab id to a pane id. Deleting the file is safe. The next toggle opens a new sidebar.

There is no config file. Placement is always a right-hand split. The manifest pane id is `sidebar`, the action id is `toggle`, and the plugin id is `aymanzahran.ai9s`.

## Repository layout

```text
herdr-plugin.toml     manifest: id, pane, action, platforms
scripts/sidebar.sh    pane entrypoint; execs ai9s
scripts/toggle.py     prefix action
scripts/open_tab.py   Enter hook
scripts/lib.py        quoting, labels, toggle decision
tests/test_lib.py     unit tests for lib.py
```

`scripts/lib.py` is the part covered by tests:

- `shell_command` joins a program and arguments with `shlex` and rejects empty names, untrimmed names, non-strings, and control characters.
- `tab_label` cleans and clips a label.
- `decide` returns `open`, `focus`, or `close`.
- `plugin_pane_id` reads `result.plugin_pane.pane.pane_id` from `plugin pane open`.
- `created_pane_id` reads `result.root_pane.pane_id` from `tab create`.

## Platforms

The manifest lists `macos` and `linux`. Herdr will not install the plugin on a platform outside that list.

Windows is omitted because the sidebar starts through `sh`, and Herdr pane commands on Windows can resolve a bare program name to a same-named directory on `PATH` ([herdrdev/herdr#5267](https://github.com/herdrdev/herdr/issues/5267)). Actions on Windows do not hit that bug. The sidebar is a pane, so it would.

## Tests

From the repository root:

```sh
PYTHONPATH=scripts python3 tests/test_lib.py
```

Run the file directly. `python3 -m unittest tests/test_lib.py` looks for a `tests` package and fails. GitHub Actions runs the same command on Ubuntu with Python 3.12.

The tests do not launch Herdr or ai9s. They cover quoting, labels, the toggle decision, and the two JSON id fields.

## Troubleshooting

**The prefix does nothing.** The key is not bound until the `[[keys.command]]` block is in the config Herdr loaded. Run `herdr server reload-config` and check `herdr plugin action list --plugin aymanzahran.ai9s`.

**Enter resumes inside the sidebar.** The running ai9s is older than 1.0.8, or `AI9S_HERDR_OPEN` is unset. `ai9s version` must report 1.0.8 or newer. Quit that ai9s and toggle the sidebar again so the pane starts the new binary. From the sidebar process, `AI9S_HERDR_OPEN` should be the absolute path of `scripts/open_tab.py`.

**The new tab opens, and the agent does not start.** Read the `ai9s` notification. `herdr plugin log list --plugin aymanzahran.ai9s` shows the toggle command. The Enter hook is a child of ai9s, started by `AI9S_HERDR_OPEN`, so a failure there is the notification rather than a plugin-action log line.

**A project sidebar hides sessions you know are indexed.** The list is limited to the focused pane's directory. Toggle the sidebar from a home-directory pane to see the full index.

**Enter on MastraCode fails.** ai9s plans `mastracode --thread`. The 0.12.1 CLI does not implement that flag. Install a newer MastraCode CLI. The plugin does not substitute `--continue`.

**Amp has no sessions.** ai9s lists Amp and does not download threads. Those stay on ampcode.com. Enter on the Amp harness row starts `amp` when that program is on `PATH`. There is no local Amp session row to resume.

**`herdr plugin install` refuses.** A linked checkout is already registered. `herdr plugin unlink aymanzahran.ai9s`, then install. Unlink leaves the checkout on disk.

**Two sidebars appear in one tab.** The state file lost the pane id (a different `HERDR_PLUGIN_STATE_DIR`, or a deleted file) while the old split was still open. Close the extra split. The next toggle records the new pane id.

## Security

A Herdr plugin runs as you. It is not sandboxed. This one runs `python3`, `sh`, `ai9s`, and the Herdr CLI. Read `herdr-plugin.toml` and `scripts/` before you install it. The install preview lists those commands.

The hook builds one shell string from the ai9s plan and passes that string as a single argument to `herdr pane run`. It rejects control characters before it calls Herdr. It does not start a shell of its own to interpret the resume command. Notifications carry error text, not session contents.

## License

[MIT](LICENSE) © 2026 Ayman Zahran.
