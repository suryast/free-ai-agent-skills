#!/usr/bin/env python3
"""Deterministic six-second packet animation; generated tone is not voiceover."""
from __future__ import annotations

import argparse
import tempfile
import threading
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS, SAMPLE_RATE = 640, 360, 24, 48000
MAX_SECONDS = 30


def validate_brief(brief):
    chapters = brief.get('chapters')
    if not isinstance(chapters, list) or len(chapters) != 3:
        raise ValueError('sample requires exactly three chapters')
    for value in [brief.get('title', ''), *[c.get('label', '') for c in chapters],
                  *[c.get('caption', '') for c in chapters]]:
        if not isinstance(value, str) or not value or not value.isascii() or len(value) > 52 or any(ord(c) < 32 for c in value):
            raise ValueError('text must be printable ASCII, 1-52 characters')
    seconds = [c.get('seconds') for c in chapters]
    if any(type(s) not in {int, float} or not math.isfinite(s) or s < 1 or s > MAX_SECONDS
           or abs(s * FPS - round(s * FPS)) > 1e-6 for s in seconds):
        raise ValueError('chapter duration must be finite, >=1s and frame-aligned')
    total = sum(seconds)
    if total > MAX_SECONDS:
        raise ValueError('runtime cap exceeded')
    return total


def chapter_at(brief, t):
    start = 0
    for index, chapter in enumerate(brief['chapters']):
        if t < start + chapter['seconds']:
            return index, chapter, (t - start) / chapter['seconds']
        start += chapter['seconds']
    return 2, brief['chapters'][-1], 1.0


def frame(brief, t, font=None):
    font = font or ImageFont.load_default(size=20)
    small = ImageFont.load_default(size=16)
    image = Image.new('RGB', (WIDTH, HEIGHT), '#132237')
    draw = ImageDraw.Draw(image)
    index, chapter, fraction = chapter_at(brief, t)
    draw.text((32, 28), brief['title'], font=font, fill='#ffffff')
    centers = [110, 320, 530]
    draw.line((centers[0], 164, centers[-1], 164), fill='#607b9a', width=5)
    for j, x in enumerate(centers):
        draw.rounded_rectangle((x - 48, 119, x + 48, 209), radius=16,
                               fill='#256b78' if index == j else '#293e58')
        draw.text((x, 229), brief['chapters'][j]['label'], font=small,
                  fill='#ffffff', anchor='mm')
    # Each chapter moves the subject independently, even with static captions.
    x = centers[index] - 35 + 70 * fraction
    y = 164 + 18 * math.sin(fraction * math.pi * 2)
    draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill='#ffcc66')
    draw.rectangle((0, 276, WIDTH, HEIGHT), fill='#0b1525')
    draw.text((WIDTH / 2, 302), chapter['caption'], font=small,
              fill='#ffffff', anchor='mm')
    draw.text((WIDTH / 2, 336), 'Synthetic tone demo - not voiceover', font=small,
              fill='#a8bfd5', anchor='mm')
    return image


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}'


def captions(brief):
    start, lines = 0, []
    for i, chapter in enumerate(brief['chapters'], 1):
        end = start + chapter['seconds']
        lines.append(f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{chapter['caption']}\n")
        start = end
    return '\n'.join(lines)


def tone(path, seconds):
    samples = bytearray()
    for i in range(round(seconds * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        envelope = min(1, t / .1, (seconds - t) / .1)
        samples.extend(struct.pack('<h', round(1300 * envelope * math.sin(2 * math.pi * 220 * t))))
    with wave.open(str(path), 'wb') as audio:
        audio.setparams((1, 2, SAMPLE_RATE, 0, 'NONE', 'not compressed'))
        audio.writeframes(samples)


def render(brief, output, narration=None, font_path=None):
    seconds = validate_brief(brief)
    for executable in ['ffmpeg', 'ffprobe']:
        if not shutil.which(executable):
            raise ValueError(f'{executable} must be installed on PATH')
    font = ImageFont.truetype(str(font_path), 20) if font_path else ImageFont.load_default(size=20)
    if narration:
        if (not narration.is_file() or narration.stat().st_size > 64 * 1024 * 1024
                or narration.suffix.lower() not in {'.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac'}):
            raise ValueError('narration must be a local audio file <=64 MiB')
        result = subprocess.run(['ffprobe', '-v', 'error', '-protocol_whitelist', 'file,pipe',
                                 '-show_entries', 'format=duration',
                                 '-of', 'json', str(narration.resolve())],
                                check=True, capture_output=True, timeout=15)
        duration = float(json.loads(result.stdout)['format']['duration'])
        if not math.isfinite(duration) or abs(duration - seconds) > .25:
            raise ValueError('narration duration must match chapter total within 0.25s')
    output.mkdir(parents=True, exist_ok=False)
    audio_path = output / ('narration' + narration.suffix if narration else 'tone.wav')
    if narration:
        shutil.copyfile(narration, audio_path)
    else:
        tone(audio_path, seconds)
    mode = 'local narration' if narration else 'synthetic tone (not voiceover)'
    (output / 'chapters.json').write_text(json.dumps(brief, indent=2) + '\n')
    (output / 'captions.srt').write_text(captions(brief))
    command = ['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS), '-i', 'pipe:0',
               '-protocol_whitelist', 'file,pipe', '-i', str(audio_path),
               '-map', '0:v:0', '-map', '1:a:0',
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
               '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', str(SAMPLE_RATE),
               '-af', 'apad', '-t', str(seconds), '-movflags', '+faststart',
               str(output / 'sample.mp4')]
    # Stream one frame at a time; a watchdog also bounds blocked pipe writes.
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=errors)
        assert process.stdin is not None
        watchdog = threading.Timer(90, process.kill)
        watchdog.start()
        try:
            for i in range(round(seconds * FPS)):
                image = frame(brief, i / FPS, font)
                if narration:
                    draw = ImageDraw.Draw(image)
                    draw.rectangle((0, 320, WIDTH, HEIGHT), fill='#0b1525')
                    draw.text((WIDTH / 2, 336), 'Local narration',
                              font=ImageFont.load_default(size=16),
                              fill='#a8bfd5', anchor='mm')
                process.stdin.write(image.tobytes())
            process.stdin.close()
            if process.wait(timeout=90) != 0:
                raise RuntimeError('FFmpeg encode failed; output is unverified')
        finally:
            watchdog.cancel()
            if process.poll() is None:
                process.kill()
            process.wait()
    (output / 'render.json').write_text(json.dumps({'audio_mode': mode,
        'font': font_path.name if font_path else 'Pillow built-in',
        'seconds': seconds, 'fps': FPS, 'size': [WIDTH, HEIGHT]}, indent=2) + '\n')
    return output / 'sample.mp4'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--brief', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/sample.json')
    parser.add_argument('--narration', type=Path)
    parser.add_argument('--font', type=Path)
    args = parser.parse_args()
    if args.brief.stat().st_size > 16384:
        parser.error('brief exceeds 16 KiB')
    print(render(json.loads(args.brief.read_text()), args.output_dir, args.narration, args.font))


if __name__ == '__main__':
    main()
