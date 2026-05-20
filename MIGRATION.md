# OpenClaw Nanobyte migration notes

This repository contains the safe, user-editable Nanobyte/OpenClaw workspace files for migration.

## Included

- Persona/context: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `TOOLS.md`, `HEARTBEAT.md`
- Daily memory notes: `memory/*.md`
- Local helper scripts under `scripts/`

## Excluded intentionally

The following are intentionally not committed because they can contain secrets, private chats, auth/session state, tokens, databases, logs, or generated media:

- `.secrets/`
- `.openclaw/`
- `.venv*/`
- `memory/.dreams/`
- `tmp/`
- `*.env`, `*.sqlite`, `*.db`, `*.jsonl`, `*.log`
- generated images/audio/video

## Restore on a new server

```bash
mkdir -p /root/.openclaw
git clone https://github.com/irwanrusda/openclaw-nanobyte /root/.openclaw/workspace
```

Then transfer secrets/runtime state directly server-to-server, not via GitHub, for example:

```bash
rsync -avz /root/.openclaw/workspace/.secrets/ root@NEW_SERVER:/root/.openclaw/workspace/.secrets/
chmod -R go-rwx /root/.openclaw/workspace/.secrets
```

If full OpenClaw runtime state is required, copy it directly with `rsync` after stopping the old service/container. Do not expose the same Telegram/WhatsApp tokens from two running servers at the same time.
