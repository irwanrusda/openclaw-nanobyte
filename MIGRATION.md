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

Before starting the new gateway, stop any old OpenClaw gateway/container that uses the same chat provider tokens.
Telegram long polling only allows one active poller per bot token; running the old and new servers at the same time will cause `409: Conflict: terminated by other getUpdates request`.

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

## Telegram `getUpdates` conflict

If logs show this error:

```text
409: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
```

The gateway is already running, but Telegram messages will not work because another process is polling the same bot token. Fix it by keeping only one Telegram poller active:

```bash
# On the old server/container
pkill -f "openclaw gateway" || true
```

If the old gateway runs under Docker/EasyPanel, stop or scale down the old app/container there. After that, restart the new OpenClaw gateway/container.
