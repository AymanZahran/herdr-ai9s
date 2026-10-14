# Security

herdr-ai9s runs as your user inside Herdr. It is ordinary Python and a shell script. Herdr does not sandbox plugins.

Before you install it, read `herdr-plugin.toml` and the files under `scripts/`. `herdr plugin install` shows those commands in its preview. Prefer `--ref v0.1.0` when you want this reviewed revision instead of whatever the default branch points at later.

The plugin talks to Herdr through `HERDR_BIN_PATH` and to ai9s through `ai9s resume --json`. The resume command is quoted as one shell string for `herdr pane run`. Names and arguments that contain a control character or DEL are rejected first. Notifications contain the error text, capped at 300 characters, and do not include session titles or prompts.

Report a vulnerability through [GitHub private vulnerability reporting](https://github.com/AymanZahran/herdr-ai9s/security) on this repository. Please do not open a public issue for an unpublished security report.
