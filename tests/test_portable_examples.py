"""Portable examples: loopback-only HTTP, synthetic consent, optional real video."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load('release_checker', 'static-site-release-verification/scripts/check_release.py')
consent = load('consent_example', 'approval-blocked-maintenance-loops/scripts/decide.py')
try:
    import PIL
    motion = load('motion_renderer', 'narrated-motion-explainers/scripts/render.py')
except ImportError:
    motion = None


class PublicInventoryTests(unittest.TestCase):
    def test_readme_count_and_package_links(self):
        import re
        from scripts.validate_skills import resource_errors
        packages = list(ROOT.glob('*/SKILL.md'))
        readme = ROOT / 'README.md'
        text = readme.read_text()
        declared = re.search(r'\*\*(\d+) complete skill packages\*\*', text)
        assert declared is not None
        self.assertEqual(int(declared.group(1)), len(packages))
        catalog = text.split('## Skills\n', 1)[1].split('\n---', 1)[0]
        self.assertEqual(sum(line.startswith('|') for line in catalog.splitlines()) - 2, len(packages))
        self.assertEqual(resource_errors(readme, ROOT), [])


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.html = b'<link rel="canonical" href="https://example.com/"><h1>Release ready</h1>'
        self.css = b'body {color: navy}'
        (self.root / 'index.html').write_bytes(self.html)
        (self.root / 'app.css').write_bytes(self.css)
        self.manifest = json.loads((ROOT / 'static-site-release-verification/assets/example.json').read_text())
        self.responses = {'/': (200, self.html), '/app.css': (200, self.css)}
        responses = self.responses
        self.requests = []
        requests = self.requests

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                status, body = responses.get(self.path, (404, b''))
                self.send_response(status)
                self.send_header('Age', '12')
                if status == 302:
                    self.send_header('Location', '/redirected')
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def verify(self, observed='synthetic-release-1'):
        return release.verify(self.manifest, self.root, self.base, observed)

    def test_clean_urls_and_parity(self):
        result = self.verify()
        self.assertTrue(result['ok'])
        self.assertEqual(self.requests, ['/', '/app.css'])
        self.assertEqual(result['checks'][0]['cache_headers']['Age'], '12')

    def test_fresh_html_stale_asset(self):
        self.responses['/app.css'] = (200, b'old css')
        result = self.verify()
        self.assertFalse(result['ok'])
        self.assertTrue(result['checks'][0]['ok'])
        self.assertEqual(result['checks'][1]['error'], 'asset byte mismatch')

    def test_revision_missing_or_mismatched(self):
        for value in ['', 'old-release']:
            self.assertFalse(self.verify(value)['ok'])

    def test_missing_needle_and_duplicate_canonical(self):
        for body in [self.html.replace(b'Release ready', b'Old release'),
                     self.html + b'<link rel="canonical" href="https://example.com/">']:
            self.responses['/'] = (200, body)
            self.assertFalse(self.verify()['ok'])

    def test_redirect_not_followed(self):
        self.responses['/'] = (302, b'')
        self.assertFalse(self.verify()['ok'])
        self.assertNotIn('/redirected', self.requests)

    def test_http_error(self):
        self.responses['/app.css'] = (404, b'missing')
        self.assertFalse(self.verify()['ok'])

    def test_response_byte_cap(self):
        self.responses['/app.css'] = (200, b'a' * (release.MAX_BYTES + 1))
        self.assertFalse(self.verify()['ok'])

    def test_input_rejected_before_network(self):
        for path in ['/app.css?v=1', '//evil.example/asset', '/%2e%2e/private', '/a\\b']:
            self.manifest['assets'][0]['path'] = path
            with self.assertRaises(ValueError):
                self.verify()
        self.assertEqual(self.requests, [])

    def test_local_escape_and_budget(self):
        self.manifest['assets'][0]['file'] = '../outside'
        with self.assertRaises(ValueError):
            self.verify()
        self.manifest['assets'] = self.manifest['assets'] * 33
        with self.assertRaises(ValueError):
            self.verify()
        self.assertEqual(self.requests, [])

    def test_checker_cli(self):
        manifest = self.root / 'release.json'
        manifest.write_text(json.dumps(self.manifest))
        result = subprocess.run([sys.executable,
            str(ROOT / 'static-site-release-verification/scripts/check_release.py'),
            '--manifest', str(manifest), '--build-dir', str(self.root),
            '--base-url', self.base, '--observed-revision', 'synthetic-release-1'],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['ok'])


class ConsentTests(unittest.TestCase):
    def setUp(self):
        self.checkpoint = json.loads((ROOT / 'approval-blocked-maintenance-loops/assets/checkpoint.json').read_text())

    def test_automatic_wakeups_never_renew_consent(self):
        for state in ['denied', 'expired', 'awaiting_approval', 'ready', 'transient_failure']:
            self.checkpoint['state'] = state
            for _ in range(4):
                self.assertEqual(consent.decide(self.checkpoint)[0], 'hold')

    def test_explicit_scoped_attempt(self):
        for state in ['denied', 'expired', 'ready']:
            self.checkpoint['state'] = state
            self.assertEqual(consent.decide(self.checkpoint, scope_approved=True,
                prerequisites_current=True)[0], 'attempt')
        self.checkpoint['state'] = 'awaiting_approval'
        self.assertEqual(consent.decide(self.checkpoint, scope_approved=True,
            prerequisites_current=True)[0], 'hold')

    def test_stale_prerequisites_and_exhausted_budget(self):
        self.assertEqual(consent.decide(self.checkpoint, scope_approved=True)[0], 'hold')
        self.checkpoint['retry_count'] = 1
        self.assertEqual(consent.decide(self.checkpoint, scope_approved=True,
            prerequisites_current=True)[0], 'hold')

    def test_unknown_requires_reconciliation_not_redispatch(self):
        self.checkpoint['state'] = 'unknown'
        self.assertEqual(consent.decide(self.checkpoint, scope_approved=True,
            prerequisites_current=True)[0], 'hold')
        self.assertEqual(consent.decide(self.checkpoint, readback_authorized=True)[0], 'reconcile')
        self.assertEqual(consent.decide(self.checkpoint, readback_authorized=True,
            readback_matches=True)[0], 'done')

    def test_transient_requires_no_side_effect_evidence(self):
        self.checkpoint['state'] = 'transient_failure'
        flags = dict(scope_approved=True, prerequisites_current=True)
        self.assertEqual(consent.decide(self.checkpoint, **flags)[0], 'hold')
        self.checkpoint['no_side_effect_evidence'] = True
        self.assertEqual(consent.decide(self.checkpoint, **flags)[0], 'attempt')

    def test_execution_and_completion_require_readback(self):
        self.checkpoint['state'] = 'executed'
        self.assertEqual(consent.decide(self.checkpoint, readback_authorized=True)[0], 'verify')
        self.checkpoint['state'] = 'completed'
        self.assertEqual(consent.decide(self.checkpoint)[0], 'hold')
        self.assertEqual(consent.decide(self.checkpoint, readback_matches=True)[0], 'done')

    def test_invalid_state_and_unbounded_counters(self):
        for state, count, budget in [('invented', 0, 1), ('ready', 0, 4), ('ready', True, 1)]:
            self.checkpoint.update(state=state, retry_count=count, retry_budget=budget)
            with self.assertRaises(ValueError):
                consent.decide(self.checkpoint)

    def test_example_cli_has_no_side_effect(self):
        checkpoint = ROOT / 'approval-blocked-maintenance-loops/assets/checkpoint.json'
        before = checkpoint.read_bytes()
        result = subprocess.run([sys.executable,
            str(ROOT / 'approval-blocked-maintenance-loops/scripts/decide.py'), str(checkpoint)],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'hold: expired approval')
        self.assertEqual(checkpoint.read_bytes(), before)


@unittest.skipIf(motion is None, 'install motion package requirements for Pillow tests')
class MotionTests(unittest.TestCase):
    def setUp(self):
        assert motion is not None
        self.brief = json.loads((ROOT / 'narrated-motion-explainers/assets/sample.json').read_text())

    def test_brief_runtime_cap_and_caption_bounds(self):
        self.assertEqual(motion.validate_brief(self.brief), 6)
        for value in [0, 31, float('nan'), 1.01]:
            broken = copy.deepcopy(self.brief)
            broken['chapters'][0]['seconds'] = value
            with self.assertRaises(ValueError):
                motion.validate_brief(broken)
        self.brief['chapters'][0]['caption'] = 'x' * 53
        with self.assertRaises(ValueError):
            motion.validate_brief(self.brief)

    def test_deterministic_frames_and_subject_motion(self):
        self.assertEqual(motion.frame(self.brief, .5).tobytes(), motion.frame(self.brief, .5).tobytes())
        self.assertNotEqual(motion.frame(self.brief, .5).crop((45, 105, 595, 214)).tobytes(),
                            motion.frame(self.brief, 1.5).crop((45, 105, 595, 214)).tobytes())
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(motion.frame(self.brief, 0))
        for chapter in self.brief['chapters']:
            self.assertLess(draw.textlength(chapter['caption'], font=ImageFont.load_default(size=16)), 576)

    def test_caption_timeline(self):
        text = motion.captions(self.brief)
        self.assertIn('00:00:00,000 --> 00:00:02,000', text)
        self.assertIn('00:00:04,000 --> 00:00:06,000', text)
        self.assertEqual(text.count('-->'), 3)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg/ffprobe required')
    def test_real_render_decode_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'sample'
            video = motion.render(self.brief, output)
            self.assertGreater(video.stat().st_size, 0)
            result = subprocess.run([sys.executable,
                str(ROOT / 'narrated-motion-explainers/scripts/verify_video.py'), str(output)],
                capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)
            evidence = json.loads(result.stdout)
            self.assertTrue(evidence['full_decode'])
            self.assertEqual(len(evidence['motion_checks']), 3)
            with self.assertRaises(FileExistsError):
                motion.render(self.brief, output)
            # Optional narration branch uses synthetic WAV as an audio-input fixture,
            # not as evidence that real spoken narration was supplied.
            narration_output = Path(temp) / 'audio-input'
            motion.render(self.brief, narration_output, output / 'tone.wav')
            self.assertTrue((narration_output / 'narration.wav').is_file())
            short = Path(temp) / 'short.wav'
            motion.tone(short, 1)
            with self.assertRaises(ValueError):
                motion.render(self.brief, Path(temp) / 'mismatch', short)


if __name__ == '__main__':
    unittest.main()
