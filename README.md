# generate-short-skill

A Claude Code slash command (`/generate-short`) that converts any landscape video into a YouTube Short — **9:16 portrait, ≤60 seconds, with AI-generated captions burned in**.

## What it does

| Step | Details |
|------|---------|
| 1 | Converts landscape → **1080×1920** portrait with blurred background fill |
| 2 | Trims to **60 seconds** (YouTube Shorts limit) |
| 3 | Transcribes audio with **Whisper** (runs locally, no API key needed) |
| 4 | Burns **styled captions** onto every frame (white Impact font, black stroke) |

## Install

### 1. Install dependencies

```bash
# ffmpeg
brew install ffmpeg

# Whisper C++ port
brew install whisper-cpp

# Python caption renderer
pip3 install Pillow
```

### 2. Download Whisper model (~142 MB, one-time)

```bash
mkdir -p ~/.whisper-models
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" \
  -o ~/.whisper-models/ggml-base.en.bin
```

### 3. Install the skill

```bash
# Claude Code slash command
mkdir -p ~/.claude/commands
curl -L "https://raw.githubusercontent.com/kaipengyu/generate-short-skill/main/.claude/commands/generate-short.md" \
  -o ~/.claude/commands/generate-short.md

# Python caption script
mkdir -p ~/.claude/scripts
curl -L "https://raw.githubusercontent.com/kaipengyu/generate-short-skill/main/scripts/burn_captions.py" \
  -o ~/.claude/scripts/burn_captions.py
```

Or clone the repo and use it as a Claude Code project (the command will be auto-detected):

```bash
git clone https://github.com/YOUR_USERNAME/generate-short-skill
cd generate-short-skill
# Open in Claude Code — /generate-short is now available
```

## Usage

In Claude Code, type:

```
/generate-short ~/Desktop/my-video.mp4
```

Claude will run the full pipeline and tell you where the output file is saved.

## Caption customization

Edit `scripts/burn_captions.py`:

```python
FONT_SIZE = 62           # larger = bigger text
stroke_width=5           # outline thickness
y = int(HEIGHT * 0.80)   # 0.0 = top, 1.0 = bottom
width=32                 # characters per line
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `~/.whisper-models/ggml-base.en.bin` | Path to Whisper model |
| `WHISPER_CLI` | `/opt/homebrew/bin/whisper-cli` | Path to whisper-cli binary |

## Requirements

- macOS (tested on Apple Silicon M4)
- Python 3.8+
- ffmpeg 7+
- whisper-cpp 1.8+

## License

MIT
