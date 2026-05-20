FROM node:24-bookworm-slim

ENV NODE_ENV=production \
    OPENCLAW_STATE_DIR=/root/.openclaw

# Basic runtime tools used by OpenClaw helpers and migration/restore commands.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      procps \
      nano \
      git \
      openssh-client \
      python3 \
      curl \
      tar \
      gzip \
    && rm -rf /var/lib/apt/lists/*

# Install OpenClaw CLI/runtime.
RUN npm install -g openclaw@2026.5.7

WORKDIR /root/.openclaw/workspace

# This repository stores the migration backup and workspace files.
COPY . /root/openclaw-nanobyte/

# Restore the full raw backup during image build when present.
# The archive contains .openclaw/ relative to /root.
RUN set -eu; \
    backup="$(ls -1 /root/openclaw-nanobyte/openclaw-full-raw-backup-*.tar.gz 2>/dev/null | sort | tail -n 1 || true)"; \
    if [ -n "$backup" ]; then \
      tar xzf "$backup" -C /root; \
    fi; \
    mkdir -p /root/.openclaw/workspace; \
    cp -a /root/openclaw-nanobyte/. /root/.openclaw/workspace/; \
    rm -rf /root/.openclaw/workspace/.git

EXPOSE 3000 3001

CMD ["openclaw", "gateway", "run", "--bind", "lan", "--port", "3000"]
