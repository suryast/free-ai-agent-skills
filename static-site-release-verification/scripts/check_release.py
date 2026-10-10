#!/usr/bin/env python3
"""Read-only, bounded static release assertions; no deployment or purge actions."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

MAX_BYTES = 4 * 1024 * 1024
MAX_REQUESTS = 32


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Canonicals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag.lower() == 'link' and 'canonical' in (values.get('rel') or '').lower().split():
            self.urls.append(values.get('href'))


def clean_path(value):
    if not isinstance(value, str):
        raise ValueError('URL path must be a string')
    parts = urllib.parse.urlsplit(value)
    decoded = urllib.parse.unquote(parts.path)
    if (parts.scheme or parts.netloc or parts.query or parts.fragment
            or not value.startswith('/') or value.startswith('//')
            or '\\' in decoded or any(c.isspace() or ord(c) < 32 for c in decoded)
            or any(p in {'.', '..'} for p in decoded.split('/'))):
        raise ValueError('URL must be a same-origin clean absolute path')
    return value


def local_file(root, value):
    if not isinstance(value, str) or Path(value).is_absolute():
        raise ValueError('build file must be a relative path')
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError('build file is missing or escapes build directory')
    if target.stat().st_size > MAX_BYTES:
        raise ValueError('build file exceeds byte limit')
    return target.read_bytes()


def html_checks(raw, item):
    text = raw.decode('utf-8')
    parser = Canonicals()
    parser.feed(text)
    if parser.urls != [item['canonical']]:
        raise ValueError('canonical mismatch or duplicate')
    if any(needle not in text for needle in item['needles']):
        raise ValueError('content needle missing')


def verify(manifest, build_dir, base_url, observed_revision):
    base = urllib.parse.urlsplit(base_url)
    if (base.scheme not in {'http', 'https'} or not base.hostname or base.username
            or base.password or base.query or base.fragment or base.path not in {'', '/'}):
        raise ValueError('base URL must be a plain HTTP(S) origin')
    revision = manifest.get('expected_revision')
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError('expected_revision is required')
    pages, assets = manifest.get('pages'), manifest.get('assets')
    if not isinstance(pages, list) or not pages or not isinstance(assets, list):
        raise ValueError('nonempty pages list and assets list required')
    if len(pages) + len(assets) > MAX_REQUESTS:
        raise ValueError('request budget exceeded')
    prepared = []
    paths = set()
    # Validate every local input before making any request.
    for kind, items in [('page', pages), ('asset', assets)]:
        for item in items:
            path = clean_path(item['path'])
            if path in paths:
                raise ValueError('duplicate request path')
            paths.add(path)
            local = local_file(Path(build_dir), item['file'])
            if kind == 'page':
                canonical = item.get('canonical')
                cp = urllib.parse.urlsplit(canonical) if isinstance(canonical, str) else None
                if not cp or cp.scheme not in {'http', 'https'} or not cp.netloc or cp.query or cp.fragment:
                    raise ValueError('canonical must be a clean absolute HTTP(S) URL')
                needles = item.get('needles')
                if not isinstance(needles, list) or not needles or any(not isinstance(n, str) or not n for n in needles):
                    raise ValueError('page requires nonempty string needles')
                html_checks(local, item)
            prepared.append((kind, item, local))
    evidence = {'checked_at': datetime.now(timezone.utc).isoformat(),
                'base_url': base_url, 'expected_revision': revision,
                'observed_revision': observed_revision,
                'revision_match': bool(observed_revision) and observed_revision == revision,
                'checks': []}
    opener = urllib.request.build_opener(NoRedirect())
    for kind, item, local in prepared:
        url = base_url.rstrip('/') + item['path']
        record = {'kind': kind, 'url': url, 'ok': False,
                  'local_sha256': hashlib.sha256(local).hexdigest()}
        try:
            with opener.open(url, timeout=10) as response:
                record['status'] = response.status
                record['cache_headers'] = {h: response.headers[h] for h in
                    ['Age', 'ETag', 'Last-Modified', 'Cache-Control', 'Via'] if h in response.headers}
                raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('response exceeds byte limit')
            if record['status'] != 200:
                raise ValueError('expected HTTP 200')
            record['deployed_sha256'] = hashlib.sha256(raw).hexdigest()
            if kind == 'page':
                html_checks(raw, item)
            elif raw != local:
                raise ValueError('asset byte mismatch')
            record['ok'] = True
        except (urllib.error.URLError, ValueError, UnicodeError, TimeoutError, OSError) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                record['status'] = exc.code
                exc.close()
            # Avoid retaining potentially sensitive server-provided bodies/errors.
            record['error'] = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        evidence['checks'].append(record)
    evidence['ok'] = evidence['revision_match'] and all(x['ok'] for x in evidence['checks'])
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--observed-revision', default='')
    args = parser.parse_args()
    try:
        if args.manifest.stat().st_size > MAX_BYTES:
            raise ValueError('manifest exceeds byte limit')
        result = verify(json.loads(args.manifest.read_text()), args.build_dir,
                        args.base_url, args.observed_revision)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
