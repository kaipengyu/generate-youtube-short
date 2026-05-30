# /generate-short

Convert any landscape video into a YouTube Short (9:16, ≤60s) with AI-generated captions burned in.

## Usage

```
/generate-short <path-to-video>
```

Example:
```
/generate-short ~/Desktop/my-video.mp4
```

Output is saved as `<input-name>-short-captioned.mp4` in the same directory as the input.

---

## Steps to run when this command is invoked

Given the video path in `$ARGUMENTS`:

1. **Parse the path** — strip quotes. Derive output path by replacing the extension with `-short-captioned.mp4`.

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

3. **Extract audio for Whisper:**

```bash
ffmpeg -i /tmp/short-portrait.mp4 -vn -ar 16000 -ac 1 -f wav /tmp/short-audio.wav
```

4. **Transcribe with whisper-cli:**

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

7. **Confirm** the output file exists and report the path to the user.

---

## Requirements

| Tool | Install |
|------|---------|
| `ffmpeg` | `brew install ffmpeg` |
| `whisper-cli` | `brew install whisper-cpp` |
| Whisper model | `curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" -o ~/.whisper-models/ggml-base.en.bin` |
| `Pillow` | `pip3 install Pillow` |
| `burn_captions.py` | Place at `~/.claude/scripts/burn_captions.py` |
