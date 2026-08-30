# Demo video

`fidelitygate-demo.mp4` is a 2:54 submission video generated entirely from verified repository artifacts: real CLI execution, the committed evidence report, scripted narration, and burned captions. `fidelitygate-demo.srt` is the standalone caption file and `thumbnail.png` is the judge-facing cover image.

Rebuild on macOS with:

```bash
uv run python scripts/build_demo_video.py
```

Requirements beyond the project dependencies: `vhs`, Playwright Chromium, `ffmpeg`, `ffprobe`, and macOS `say` with the Samantha voice.

The build verifies that the final file is below five minutes, contains H.264 video plus AAC audio, and decodes fully. The committed render is 1600×900 at 30 fps, 174.5 seconds long, and approximately 7 MB. Six sampled frames were visually inspected after the full decode check.
