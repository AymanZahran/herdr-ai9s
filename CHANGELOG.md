# Changelog

## 0.1.2 - 2026-10-14

- Pressing the prefix key again closes the sidebar in this tab, or focuses it when another pane is focused. A successful open is remembered. An ai9s pane already in the tab is reused.

## 0.1.1 - 2026-10-14

- The sidebar splits the focused pane. Herdr rejects a workspace id on a split, which is the `target_pane_id` error from 0.1.0.

## 0.1.0 - 2026-10-14

- Sidebar in the current Herdr tab, toggled with a prefix key you bind (suggested `prefix+i`).
- Enter on a session or a harness opens that program in a new tab of the current workspace. The sidebar stays in the previous tab.
- Enter on a directory, branch, or model still pins that row inside ai9s.
- `y` on a session plans the ai9s auto-approve resume and starts it in the new tab.
- Requires Herdr 0.8.0 or newer and ai9s 1.0.8 or newer. macOS and Linux.
