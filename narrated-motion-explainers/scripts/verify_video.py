#!/usr/bin/env python3
"""Probe/decode the finished video and verify motion outside caption regions."""
import argparse
import io
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageChops
from render import FPS, HEIGHT, WIDTH, validate_brief


def verify(output):
    video = (output / 'sample.mp4').resolve()
    brief = json.loads((output / 'chapters.json').read_text())
    expected = validate_brief(brief)
    metadata = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams',
        '-show_format', '-of', 'json', str(video)], check=True,
        capture_output=True, timeout=15).stdout)
    streams = metadata['streams']
    visual = next(s for s in streams if s['codec_type'] == 'video')
    audio = next(s for s in streams if s['codec_type'] == 'audio')
    duration = float(metadata['format']['duration'])
    if (visual['codec_name'] != 'h264' or visual['pix_fmt'] != 'yuv420p'
            or (visual['width'], visual['height']) != (WIDTH, HEIGHT)
            or visual['avg_frame_rate'] != f'{FPS}/1' or audio['codec_name'] != 'aac'
            or int(audio['sample_rate']) != 48000 or abs(duration - expected) > .1):
        raise ValueError('video contract mismatch')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video),
                    '-f', 'null', '-'], check=True, capture_output=True, timeout=90)
    pairs, start = [], 0
    for index, chapter in enumerate(brief['chapters']):
        images = []
        for part, fraction in enumerate([.25, .75]):
            time = start + chapter['seconds'] * fraction
            result = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(time), '-i', str(video),
                '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', 'pipe:1'],
                check=True, capture_output=True, timeout=15)
            image = Image.open(io.BytesIO(result.stdout)).convert('RGB')
            image.save(output / f'inspect-{index + 1}-{part + 1}.png')
            images.append(image.crop((45, 105, 595, 214)))
        changed = ImageChops.difference(*images).getbbox()
        if changed is None:
            raise ValueError(f'chapter {index + 1} has no decoded subject motion')
        pairs.append({'chapter': index + 1, 'subject_motion': True})
        start += chapter['seconds']
    evidence = {'ok': True, 'duration': duration, 'video_codec': visual['codec_name'],
                'pixel_format': visual['pix_fmt'], 'size': [WIDTH, HEIGHT],
                'fps': FPS, 'audio_codec': audio['codec_name'],
                'audio_sample_rate': int(audio['sample_rate']),
                'full_decode': True, 'motion_checks': pairs}
    (output / 'verification.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', type=Path)
    print(json.dumps(verify(parser.parse_args().output_dir), indent=2))


if __name__ == '__main__':
    main()
