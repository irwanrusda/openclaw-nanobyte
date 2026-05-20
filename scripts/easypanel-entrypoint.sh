#!/bin/sh
set -eu

STATE_DIR="${OPENCLAW_STATE_DIR:-/root/.openclaw}"
WORKSPACE_DIR="${STATE_DIR}/workspace"
CONFIG_FILE="${STATE_DIR}/openclaw.json"

mkdir -p "$STATE_DIR" "$WORKSPACE_DIR"

# EasyPanel mounts volumes at runtime. If /root/.openclaw is an empty persistent
# volume, files restored during image build are hidden, so seed the workspace here.
if [ -d /root/openclaw-nanobyte ]; then
  cp -an /root/openclaw-nanobyte/. "$WORKSPACE_DIR"/ 2>/dev/null || true
  rm -rf "$WORKSPACE_DIR/.git"
fi

# Optional secret injection for redeploys. Put the revoked/reissued Telegram token
# in EasyPanel as OPENCLAW_TELEGRAM_TOKEN; do not commit it to GitHub.
if [ -n "${OPENCLAW_TELEGRAM_TOKEN:-}" ] && [ -f "$CONFIG_FILE" ]; then
  node <<'NODE'
const fs = require('fs');

const configFile = process.env.CONFIG_FILE || '/root/.openclaw/openclaw.json';
const token = process.env.OPENCLAW_TELEGRAM_TOKEN;

if (!token) process.exit(0);

const cfg = JSON.parse(fs.readFileSync(configFile, 'utf8'));
let changed = false;

function isTelegramPath(path) {
  return path.some((part) => String(part).toLowerCase().includes('telegram'));
}

function looksLikeBotToken(value) {
  return typeof value === 'string' && /^\d{6,}:[A-Za-z0-9_-]{20,}$/.test(value);
}

function walk(value, path = []) {
  if (!value || typeof value !== 'object') return;
  for (const key of Object.keys(value)) {
    const nextPath = path.concat(key);
    const lowerKey = String(key).toLowerCase();
    if (
      typeof value[key] === 'string' &&
      isTelegramPath(nextPath) &&
      (lowerKey.includes('token') || looksLikeBotToken(value[key]))
    ) {
      if (value[key] !== token) {
        value[key] = token;
        changed = true;
      }
      continue;
    }
    walk(value[key], nextPath);
  }
}

walk(cfg);

if (changed) {
  const backup = `${configFile}.bak-entrypoint`;
  fs.copyFileSync(configFile, backup);
  fs.writeFileSync(configFile, JSON.stringify(cfg, null, 2));
  console.log(`[entrypoint] updated Telegram token in ${configFile}; backup=${backup}`);
} else {
  console.log('[entrypoint] OPENCLAW_TELEGRAM_TOKEN provided, but no Telegram token field was changed');
}
NODE
fi

exec "$@"
