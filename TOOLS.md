# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Vikunja

- Base URL API: `https://surau-tv-vikunja-irwan.ltjafv.easypanel.host/api/v1`
- API token disimpan lokal di `/root/.openclaw/workspace/.secrets/vikunja.env`; jangan ditampilkan ke chat.
- Auth dari docs: gunakan header `Authorization: Bearer <token>`.
- Secret env harus berupa assignment shell valid (lebih aman pakai kutip tunggal untuk value URL/token).
- Gunakan hanya untuk integrasi Vikunja yang diminta Bang Irwan.

## coret.id

- Agentic API helper installed at `/root/.openclaw/plugin-skills/coret-id/scripts/coret_api.py`.
- Local skill installed at `/root/.openclaw/plugin-skills/coret-id/SKILL.md`.
- API key is stored locally in `/root/.openclaw/workspace/.secrets/coret-id.env`; do not print or share it.
- Test command: `python3 /root/.openclaw/plugin-skills/coret-id/scripts/coret_api.py GET /workspace`.

## GrowthCircle Image Skill

- Local skill installed at `/root/.openclaw/plugin-skills/growthcircle-image/SKILL.md`.
- Helper script: `/root/.openclaw/plugin-skills/growthcircle-image/scripts/growthcircle_image.py`.
- Use when built-in `image_generate` cannot directly use provider `custom-ai-growthcircle-id`.
- Test command: `python3 /root/.openclaw/plugin-skills/growthcircle-image/scripts/growthcircle_image.py --prompt 'Pemandangan sunset dari atas gunung' --size 3:2`.

## WAHA

- Base URL: `https://nanobyte-waha-wpp.ka2h0x.easypanel.host`
- API key is provided by Bang Irwan and should stay private.
- Personal session: `nanobyte_byu` — for Bang Irwan-related/private messaging context.
- Surau TV session: `5455_wpp` — for Surau TV automation and donor communication only.
- Current preference: keep WAHA integration lightweight; priority is checking whether a session is active or not.

## EasyPanel / OpenClaw Deploy Trigger

- Deployment trigger URL is stored locally in `/root/.openclaw/workspace/.secrets/easypanel-deploy.env`; do not print or share it.
- Use only when Bang Irwan explicitly asks to redeploy/restart OpenClaw/Nano, because it can interrupt the active session.

## Surau TV Work Plan API

- Local skill installed at `/root/.openclaw/plugin-skills/surau-workplan/SKILL.md`.
- Helper script: `/root/.openclaw/plugin-skills/surau-workplan/scripts/workplan_api.py`.
- Secret file: `/root/.openclaw/workspace/.secrets/surau-workplan.env` (mode `600`).
- Env key: `SURAU_WORKPLAN_API_KEY`.
- Auth default in helper: header `X-API-Key`; optional fallback mode: query `?token=...`.
- API test status: `GET list` succeeded (`HTTP 200`), total data currently `21`.
- Safe reads: `list`, `detail`, `calendar`.
- Writes: `create`, `update`, `update-status`.
- Destructive actions `delete` and `bulk-delete` should stay confirmation-gated.

## GrowthCircle / Seedance model notes

Disimpan untuk klasifikasi prioritas dan fallback Nano.

### Prioritas mengolah perintah / chat

- Primary: `custom-ai-growthcircle-id/gpt-5.5-free`
- Fallback 1: `custom-ai-growthcircle-id/gpt-5.4-free`
- Fallback 2: `custom-ai-growthcircle-id/claude-opus-4-7-free`
- Fallback 3: `custom-ai-growthcircle-id/claude-opus-4-6-free`
- Fallback 4: `custom-ai-growthcircle-id/claude-sonnet-4-6-free`
- Fallback 5: `custom-ai-growthcircle-id/gemini-3.1-pro-preview-free`
- Fallback 6: `custom-ai-growthcircle-id/claude-haiku-4-5-20251001-free`
- Fallback 7: `custom-ai-growthcircle-id/gpt-5.4-mini-free`
- Fallback 8: `custom-ai-growthcircle-id/gpt-5.3-codex-free`

### Prioritas coding / logika / analisis

- Primary: `custom-ai-growthcircle-id/gpt-5.3-codex-free`
- Fallback 1: `custom-ai-growthcircle-id/gpt-5.5-free`
- Fallback 2: `custom-ai-growthcircle-id/claude-opus-4-7-free`
- Fallback 3: `custom-ai-growthcircle-id/claude-opus-4-6-free`
- Fallback 4: `custom-ai-growthcircle-id/claude-sonnet-4-6-free`

### Prioritas gambar

- Primary target: `custom-ai-growthcircle-id/gpt-image-2-official-free`
- Fallback runtime: `gpt-image-1.5-official-free`, `flux-kontext-pro-free`, `flux-kontext-max-free`, `gpt-4o-image-free`, `gpt-image-2-free`, `flux-2-pro-free`, `doubao-seedream-5-0-lite-free`, `gpt-image-1-official-free`
- Catatan implementasi: tool `image_generate` bawaan belum mengenali provider `custom-ai-growthcircle-id`, jadi sementara gunakan helper lokal `python3 /root/.openclaw/workspace/scripts/growthcircle_image.py --prompt '...'` untuk GrowthCircle direct image generation.
- Catatan endpoint: ukuran ratio seperti `3:2` lebih aman daripada ukuran piksel mentah pada jalur GrowthCircle image tertentu.

### Prioritas video

- Primary: `custom-ai-growthcircle-id/doubao-seedance-4-5-free`
- Fallback: `doubao-seedance-4-0-free`, `doubao-seedance-2.0-free`, `doubao-seedance-2.0-fast-free`, `doubao-seedance-1-5-pro-free`, `doubao-seedance-1-0-pro-quality-free`, `doubao-seedance-1-0-pro-fast-free`
- Face-specific fallback: `doubao-seedance-2.0-face-free`, `doubao-seedance-2.0-fast-face-free`

### Prioritas audio / speech

- Primary target: `custom-ai-growthcircle-id/speech-2.8-hd-free`
- Runtime saat ini: `microsoft` TTS dengan voice `id-ID-GadisNeural` sebagai fallback yang benar-benar jalan.
- Catatan penting: endpoint TTS GrowthCircle mengenali `speech-2.8-hd` (tanpa suffix `-free`) pada jalur `/audio/speech`, tetapi akun saat ini diblok `MODEL_NOT_ALLOWED_FOR_PLAN`.
- Jadi untuk sekarang, speech GrowthCircle dicatat sebagai target/aspirasi; Microsoft tetap jadi jalur kirim audio yang aktif.

### Strategi fallback final Nano

- Chat/perintah umum: `gpt-5.5-free` → `gpt-5.4-free` → `claude-opus-4-7-free` → `claude-opus-4-6-free` → `claude-sonnet-4-6-free` → `gemini-3.1-pro-preview-free` → `claude-haiku-4-5-20251001-free` → `gpt-5.4-mini-free` → `gpt-5.3-codex-free`
- Coding/logika/analisis: `gpt-5.3-codex-free` → `gpt-5.5-free` → `claude-opus-4-7-free` → `claude-opus-4-6-free` → `claude-sonnet-4-6-free`
- Gambar: GrowthCircle direct helper → `gpt-image-1.5-official-free` → `flux-kontext-pro-free` → `flux-kontext-max-free` → `gpt-4o-image-free` → `gpt-image-2-free` → `flux-2-pro-free` → `doubao-seedream-5-0-lite-free` → `gpt-image-1-official-free`
- Video: `doubao-seedance-4-5-free` → `doubao-seedance-4-0-free` → `doubao-seedance-2.0-free` → `doubao-seedance-2.0-fast-free` → `doubao-seedance-1-5-pro-free` → `doubao-seedance-1-0-pro-quality-free` → `doubao-seedance-1-0-pro-fast-free`
- Audio/TTS: target GrowthCircle speech bila plan dibuka → fallback aktif `microsoft` voice `id-ID-GadisNeural` → opsi berikutnya cari provider TTS lain yang lebih natural

### Klasifikasi model

- Chat/perintah: `gpt-5.4-free`, `gpt-5.5-free`, `gpt-5.4-mini-free`, `gpt-5.3-codex-free`, `claude-opus-4-7-free`, `claude-opus-4-6-free`, `claude-sonnet-4-6-free`, `claude-haiku-4-5-20251001-free`, `gemini-3.1-pro-preview-free`, `gemini-3-pro-preview-free`
- Gambar: `doubao-seedream-5-0-lite-free`, `flux-2-pro-free`, `flux-kontext-max-free`, `flux-kontext-pro-free`, `gpt-4o-image-free`, `gpt-image-1-official-free`, `gpt-image-1.5-official-free`, `gpt-image-2-free`, `gpt-image-2-official-free`
- Video: `doubao-seedance-1-0-pro-fast-free`, `doubao-seedance-1-0-pro-quality-free`, `doubao-seedance-1-5-pro-free`, `doubao-seedance-2.0-free`, `doubao-seedance-2.0-face-free`, `doubao-seedance-2.0-fast-free`, `doubao-seedance-2.0-fast-face-free`, `doubao-seedance-4-0-free`, `doubao-seedance-4-5-free`
- Audio/speech: `speech-2.8-hd-free`

## Related

- [Agent workspace](/concepts/agent-workspace)
