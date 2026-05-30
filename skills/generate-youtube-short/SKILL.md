# Generate YouTube Short

Convert any landscape video into a YouTube Short — **9:16 portrait (1080×1920), trimmed to 60 seconds, with AI-generated captions burned in**.

## What this skill does

| Step | What happens |
|------|-------------|
| 1 | Converts landscape → 1080×1920 portrait with blurred background fill |
| 2 | Trims to 60 seconds (YouTube Shorts limit) |
| 3 | Transcribes audio locally with Whisper (no API key needed) |
| 4 | Burns styled captions onto every frame (white Impact font, black stroke) |

## Requirements

```bash
# Install tools
brew install ffmpeg
brew install whisper-cpp
pip3 install Pillow

# Download Whisper model (~142 MB, one-time)
mkdir -p ~/.whisper-models
curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" \
  -o ~/.whisper-models/ggml-base.en.bin

# Install caption script
mkdir -p ~/.claude/scripts
curl -L "https://raw.githubusercontent.com/kaipengyu/generate-youtube-short/main/scripts/burn_captions.py" \
  -o ~/.claude/scripts/burn_captions.py
```

## Usage

```
/generate-short <path-to-video>
```

Example:
```
/generate-short ~/Desktop/my-video.mp4
```

Output is saved as `<input-name>-short-captioned.mp4` in the same directory.

## Steps Claude will run

Given the video path in `$ARGUMENTS`:

1. **Parse the path** — strip quotes, derive output path (`-short-captioned.mp4`).

2. **Convert to 9:16 portrait (blur background, trim to 60s):**
```bash
ffmpeg -i "$INPUT" \
  -t 60 \
  -filter_complex "
    [0:v]split[main][bg];
    [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[blurred];
    [main]scale=1080:-2[fg];
    [blurred][fg]overlay=(W-w)/2:(H-h)/2[outv]
  " \
  -map "[outv]" -map 0:a \
  -c:v libx264 -crf 20 -preset medium \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  /tmp/short-portrait.mp4
```

3. **Extract audio:**
```bash
ffmpeg -i /tmp/short-portrait.mp4 -vn -ar 16000 -ac 1 -f wav /tmp/short-audio.wav
```

4. **Transcribe with Whisper:**
```bash
whisper-cli \
  -m "${WHISPER_MODEL:-$HOME/.whisper-models/ggml-base.en.bin}" \
  -f /tmp/short-audio.wav \
  --output-srt \
  --output-file /tmp/short-captions
```

5. **Burn captions:**
```bash
python3 ~/.claude/scripts/burn_captions.py \
  /tmp/short-portrait.mp4 \
  /tmp/short-captions.srt \
  "$OUTPUT"
```

6. **Clean up:**
```bash
rm -f /tmp/short-portrait.mp4 /tmp/short-audio.wav /tmp/short-captions.srt
```

7. **Confirm** the output file exists and report the path.

## Caption customization

Edit `~/.claude/scripts/burn_captions.py`:

```python
FONT_SIZE = 62           # larger = bigger text
stroke_width=5           # outline thickness
y = int(HEIGHT * 0.80)   # caption vertical position
width=32                 # characters per line
```

## Compatible agents

- Claude Code
