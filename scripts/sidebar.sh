#!/bin/sh
# Herdr runs this inside the sidebar pane. Enter in ai9s starts open_tab.py.
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
if [ -x "$HOME/.local/bin/ai9s" ]; then
  PATH="$HOME/.local/bin:$PATH"
  export PATH
fi
export AI9S_HERDR_OPEN="$root/scripts/open_tab.py"
export AI9S_HERDR_SIDEBAR=1
exec ai9s
