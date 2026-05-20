#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_PATH = Path('/root/.openclaw/openclaw.json')
DEFAULT_PROVIDER_ID = 'custom-ai-growthcircle-id'
DEFAULT_MODELS = [
    'gpt-image-2-official-free',
    'gpt-image-1.5-official-free',
    'gpt-image-2-free',
    'gpt-4o-image-free',
    'flux-kontext-pro-free',
    'flux-kontext-max-free',
    'flux-2-pro-free',
    'doubao-seedream-5-0-lite-free',
    'gpt-image-1-official-free',
]


def load_provider(provider_id: str):
    cfg = json.loads(CONFIG_PATH.read_text())
    providers = cfg.get('models', {}).get('providers', {})
    provider = providers.get(provider_id)
    if not provider:
        raise SystemExit(f'Provider not found: {provider_id}')
    base_url = provider.get('baseUrl', '').rstrip('/')
    api_key = provider.get('apiKey')
    if not base_url or not api_key:
        raise SystemExit(f'Provider {provider_id} missing baseUrl/apiKey')
    return base_url, api_key


def request_json(method: str, url: str, api_key: str, body=None, timeout=120):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'OpenClaw-Nano/1.0',
        'Accept': 'application/json',
    }
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8', 'replace')
        return json.loads(raw)


def submit_generation(base_url: str, api_key: str, model: str, prompt: str, size: str):
    url = base_url + '/images/generations'
    payload = {
        'model': model,
        'prompt': prompt,
        'size': size,
    }
    return request_json('POST', url, api_key, body=payload, timeout=180)


def poll_task(base_url: str, api_key: str, task_id: str, poll_seconds: int, max_wait_seconds: int):
    started = time.time()
    paths = [
        f'/images/generations/{task_id}',
        f'/tasks/{task_id}',
    ]
    last = None
    while time.time() - started <= max_wait_seconds:
        for path in paths:
            try:
                data = request_json('GET', base_url + path, api_key, timeout=60)
                last = data
                task = data.get('data') or {}
                status = task.get('status')
                if status == 'completed':
                    return data
                if status in ('failed', 'error', 'cancelled'):
                    return data
            except urllib.error.HTTPError:
                pass
        time.sleep(poll_seconds)
    return last


def extract_asset_url(result_data: dict):
    data = result_data.get('data') or {}
    result = data.get('result') or {}
    images = result.get('images') or []
    if not images:
        return None
    first = images[0] or {}
    urls = first.get('url') or []
    if not urls:
        return None
    asset_path = urls[0]
    if asset_path.startswith('http://') or asset_path.startswith('https://'):
        return asset_path
    # GrowthCircle serves these from growthcircle.id, not ai.growthcircle.id.
    return 'https://growthcircle.id' + asset_path


def download_binary(url: str, api_key: str, output_path: Path):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'OpenClaw-Nano/1.0',
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=180) as resp:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(resp.read())


def sanitize_name(text: str, fallback: str = 'growthcircle-image') -> str:
    cleaned = ''.join(ch.lower() if ch.isalnum() else '-' for ch in text).strip('-')
    cleaned = '-'.join(part for part in cleaned.split('-') if part)
    return (cleaned[:80] or fallback)


def main():
    ap = argparse.ArgumentParser(description='Generate image via GrowthCircle image endpoint with fallback + polling.')
    ap.add_argument('--prompt', required=True)
    ap.add_argument('--size', default='3:2', help='Usually ratio strings work best on GrowthCircle, e.g. 1:1, 3:2, 16:9')
    ap.add_argument('--output', default='')
    ap.add_argument('--provider-id', default=DEFAULT_PROVIDER_ID)
    ap.add_argument('--model', action='append', dest='models', default=[])
    ap.add_argument('--poll-seconds', type=int, default=5)
    ap.add_argument('--max-wait-seconds', type=int, default=240)
    args = ap.parse_args()

    base_url, api_key = load_provider(args.provider_id)
    models = args.models or DEFAULT_MODELS
    out = Path(args.output) if args.output else Path('/root/.openclaw/workspace/tmp') / f"{sanitize_name(args.prompt)}.png"

    attempts = []
    for model in models:
        attempt = {'model': model}
        try:
            submitted = submit_generation(base_url, api_key, model, args.prompt, args.size)
            attempt['submit'] = submitted
            items = submitted.get('data') or []
            item = items[0] if isinstance(items, list) and items else {}
            if item.get('b64_json'):
                import base64
                out.write_bytes(base64.b64decode(item['b64_json']))
                print(json.dumps({'ok': True, 'model': model, 'output': str(out), 'mode': 'inline'}, ensure_ascii=False))
                return
            task_id = item.get('task_id')
            if not task_id:
                attempt['error'] = 'missing_task_id'
                attempts.append(attempt)
                continue
            polled = poll_task(base_url, api_key, task_id, args.poll_seconds, args.max_wait_seconds)
            attempt['poll'] = polled
            task = (polled or {}).get('data') or {}
            status = task.get('status')
            if status == 'completed':
                asset_url = extract_asset_url(polled)
                if not asset_url:
                    attempt['error'] = 'completed_without_asset_url'
                    attempts.append(attempt)
                    continue
                download_binary(asset_url, api_key, out)
                print(json.dumps({
                    'ok': True,
                    'model': model,
                    'taskId': task_id,
                    'assetUrl': asset_url,
                    'output': str(out),
                    'attemptsTried': [a['model'] for a in attempts] + [model],
                }, ensure_ascii=False))
                return
            attempt['error'] = status or 'unknown_status'
            attempts.append(attempt)
        except urllib.error.HTTPError as e:
            try:
                err = e.read().decode('utf-8', 'replace')
            except Exception:
                err = str(e)
            attempt['httpError'] = {'code': e.code, 'body': err[:1200]}
            attempts.append(attempt)
        except Exception as e:
            attempt['exception'] = f'{type(e).__name__}: {e}'
            attempts.append(attempt)

    print(json.dumps({'ok': False, 'attempts': attempts}, ensure_ascii=False, indent=2))
    sys.exit(1)


if __name__ == '__main__':
    main()
