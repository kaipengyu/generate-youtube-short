#!/usr/bin/env python3
"""
burn_captions.py — burn SRT captions into a video using Pillow

Usage: python3 burn_captions.py <input_video> <srt_file> <output_video>
"""
import sys
import subprocess
import re
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont

if len(sys.argv) != 4:
    print("Usage: burn_captions.py <input_video> <srt_file> <output_video>")
    sys.exit(1)

INPUT  = sys.argv[1]
SRT    = sys.argv[2]
OUTPUT = sys.argv[3]
WIDTH, HEIGHT = 1080, 1920
FPS    = 30
FONT_SIZE = 62


def ts_to_sec(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path):
    captions = []
    with open(path) as f:
        content = f.read()
    for block in content.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)", lines[1])
        if not m:
            continue
        start = ts_to_sec(m.group(1))
        end   = min(ts_to_sec(m.group(2)), 60.0)
        text  = " ".join(lines[2:]).strip().lstrip()
        if text and start < 60.0:
            captions.append((start, end, text))
    return captions


def get_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_caption(draw, text, font):
    wrapped = textwrap.fill(text, width=32)
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (WIDTH - text_w) // 2
    y = int(HEIGHT * 0.80) - text_h // 2
    draw.multiline_text(
        (x, y), wrapped, font=font,
        fill=(255, 255, 255),
        stroke_width=5, stroke_fill=(0, 0, 0),
        align="center",
    )


def main():
    captions = parse_srt(SRT)
    font = get_font(FONT_SIZE)

    decode = subprocess.Popen(
        ["ffmpeg", "-i", INPUT, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    encode = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
            "-i", "pipe:0",
            "-i", INPUT,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-c:a", "copy", "-shortest",
            OUTPUT,
        ],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )

    frame_size = WIDTH * HEIGHT * 3
    frame_num  = 0

    while True:
        raw = decode.stdout.read(frame_size)
        if len(raw) < frame_size:
            break

        t = frame_num / FPS
        frame_num += 1

        caption = next((text for start, end, text in captions if start <= t < end), None)

        img = Image.frombytes("RGB", (WIDTH, HEIGHT), raw)
        if caption:
            draw_caption(ImageDraw.Draw(img), caption, font)

        encode.stdin.write(img.tobytes())

        if frame_num % 150 == 0:
            print(f"  {t:.1f}s / 60s processed...", flush=True)

    encode.stdin.close()
    encode.wait()
    decode.wait()
    print(f"Done! {frame_num} frames -> {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()
