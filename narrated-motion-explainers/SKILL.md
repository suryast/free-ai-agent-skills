---
name: narrated-motion-explainers
description: Produces short captioned motion explainers by streaming Pillow frames into FFmpeg and verifying the finished MP4. Use when asked for an animated explainer, narrated process video, or reproducible lightweight motion graphics without browser or scene-engine dependencies.
license: MIT
compatibility: Python 3.11+, Pillow (pinned package requirements), FFmpeg and ffprobe on PATH with libx264 and AAC support. Works without network or TTS credentials. Shell setup examples use POSIX; Windows uses the virtualenv Scripts directory.
---

# Narrated motion explainers

## Deliver a video, not merely a renderer

1. Establish audience, one message, runtime cap, aspect ratio, and narration rights. Write a fresh brief and short chapter script; retain source notes for factual claims without copying full source pages.
2. For narration, obtain an authorized local recording or optional TTS output. Measure audio with ffprobe before setting chapter durations. Do not invent speech timing from word counts. Keep any external TTS provider optional; never bundle credentials. Match captions to actual speech, restoring punctuation only after token alignment and clamping overlapping cues.
3. Render a short preview first. Use deterministic scene state at time `t`, RGB Pillow frames, and FFmpeg rawvideo input. Animate the explanatory subject, not only the background or caption strip. Use legible captions, bounded text, and licensed fonts; avoid distributing font binaries without permission.
4. Encode H.264/yuv420p plus AAC at an explicit 48 kHz sample rate. Bound output duration and processing time. Preserve chapter JSON, captions, renderer and audio beside the MP4 so visual rerenders do not require network access.
5. Probe the actual output's duration, dimensions, frame rate, codecs and audio. Decode the entire MP4. Extract paired interior frames per chapter and check subject motion separately from captions. Inspect decoded frames for clipping, layout and synchronization; a passed Python run is not video verification.
6. Deliver the real verified MP4 plus source/caption assets, brief, source/rights notes and measured results. If narration is unavailable, label the output a tone/silent motion demo, not a narrated video. Do not ship a virtualenv, credentials or copyrighted source snapshots.

## Runnable offline sample

The fresh sample explains a three-stage packet route in six seconds. Its generated quiet synthetic tone is **not voiceover**. [render.py](scripts/render.py) produces an MP4, WAV (tone mode), chapter copy and SRT. [verify_video.py](scripts/verify_video.py) probes and fully decodes it, checks per-chapter subject motion, and saves decoded inspection PNGs. Dependencies are in [requirements.txt](requirements.txt); the brief is [sample.json](assets/sample.json).

Run from the repository root (or adjust paths to the installed whole package):

```bash
python3 -m venv .motion-venv
.motion-venv/bin/python -m pip install -r narrated-motion-explainers/requirements.txt
# Install FFmpeg/ffprobe separately using your platform's supported package manager.
.motion-venv/bin/python narrated-motion-explainers/scripts/render.py --output-dir motion-output
.motion-venv/bin/python narrated-motion-explainers/scripts/verify_video.py motion-output
```

The output directory must not already exist, preventing accidental overwrite. The renderer limits chapter duration to 30 seconds total and checks that timings land on 24 fps boundaries; encode/decode subprocesses have bounded timeouts. This is a small fixed 640×360 sample, not a general video editor. Captions are ASCII and length-limited; translate with proper font/glyph and line-layout checks instead of removing those limits blindly.

For your own spoken narration, edit the sample chapter timings/text and pass `--brief brief.json --narration recording.wav`. The renderer measures the recording and rejects a duration mismatch exceeding 0.25 seconds, then copies it into the output. It accepts a local WAV/MP3/OGG/FLAC/M4A/AAC file up to 64 MiB and disables network input protocols. It does not create or align speech automatically. Listen to the final video and verify caption timing manually; structural checks cannot prove semantic narration alignment.

Pillow's built-in font is the default; no external font files are bundled. To use a system font, pass `--font /path/to/licensed-font.ttf`, verify its license, and keep the path out of public deliverables. Output records only the font basename. The default sample is independently runnable with Python/Pillow/FFmpeg; runtime-specific agent tools are not required.
