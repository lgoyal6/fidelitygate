#!/usr/bin/env python3
"""Build the under-five-minute demo from real CLI and evidence artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True, slots=True)
class Segment:
    key: str
    visual: Literal["slide", "terminal", "report"]
    source: str
    narration: str


@dataclass(frozen=True, slots=True)
class Caption:
    start: float
    end: float
    text: str


SEGMENTS = [
    Segment(
        "problem",
        "slide",
        "1",
        (
            "Agent environment teams usually replay expert trajectories before accepting a "
            "simulation for training or evaluation. That proves an intended route works. It "
            "does not prove a shortcut is unreachable. FidelityGate audits the environment "
            "artifact itself and asks one narrow question: can any reachable action sequence "
            "contradict the approved source policy?"
        ),
    ),
    Segment(
        "execution",
        "terminal",
        "terminal.mp4",
        (
            "Here is the failure in one execution. The replay baseline receives the clean and "
            "mutated refund environments with identical expert traces. It accepts both, for a "
            "balanced accuracy of point five. The falsification agent receives no ground truth. "
            "On the stress mutant it searches by claim progress, finds the unsafe two-action "
            "route in thirty transitions, minimizes it, and replays it three out of three times."
        ),
    ),
    Segment(
        "architecture",
        "slide",
        "2",
        (
            "Every component has a verification job. Exact policy excerpts become typed claims "
            "and are hashed. Benchmark labels are removed before the agent runs. A code-free "
            "workflow interpreter executes inside a credential-minimized worker. The agent "
            "remembers canonical states, checks every transition, and chooses accept only after "
            "complete exploration, reject only after triple replay, and unknown for everything "
            "incomplete."
        ),
    ),
    Segment(
        "results",
        "slide",
        "3",
        (
            "EnvMutationBench contains fourteen clean and fourteen mutated workflows across "
            "authorization, evidence, identity, time, retries, memory, reward, and observability. "
            "Expert replay scores point five because every hidden shortcut survives. FidelityGate "
            "correctly accepts all fourteen clean packages and rejects all fourteen mutants. Four "
            "family-level holdouts also score one point zero. These are synthetic results, not a "
            "production estimate."
        ),
    ),
    Segment(
        "evidence",
        "report",
        "report.png",
        (
            "The output is a review artifact, not a chatbot answer. It includes every case, every "
            "baseline, suite and fixture hashes, the approved source excerpt, the observed "
            "forbidden state, the minimal action sequence, and replay counts. A reviewer can read "
            "the memo first, then reproduce the exact JSON evidence without trusting explanatory "
            "prose."
        ),
    ),
    Segment(
        "stress",
        "slide",
        "4",
        (
            "Claim-directed search is present because an ablation earned it. In a combinatorial "
            "decoy workflow, breadth-first and random search both consume the fixed two hundred "
            "transition budget and miss the mutant. FidelityGate prioritizes states closer to the "
            "forbidden claim and rejects in thirty transitions. The paired clean case remains "
            "unknown, because not finding a bug is not proof of safety."
        ),
    ),
    Segment(
        "failure",
        "slide",
        "5",
        (
            "The most useful result was a failure in the evaluator. The first full run scored zero "
            "point nine two nine because a temporal oracle confused access before expiry with "
            "access after expiry. A second clean fixture allowed actions after its terminal reset. "
            "Both failures are preserved with a one-command reproducer. The lesson is simple: "
            "falsify the benchmark before trusting its score."
        ),
    ),
    Segment(
        "finish",
        "slide",
        "6",
        (
            "From a clean clone, bin verify installs pinned dependencies, runs thirty-two tests at "
            "over ninety-two percent coverage, validates generated benchmark bytes, and reproduces "
            "every committed evidence file. The hot take is that reliable agent evaluation is not "
            "more simulated users. It is the smallest source-backed counterexample that survives "
            "a skeptical replay."
        ),
    ),
]


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def duration(path: Path, *, cwd: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return float(completed.stdout.strip())


def require_tools(names: list[str]) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        raise RuntimeError("missing demo tools: " + ", ".join(missing))


def screenshot_slides(root: Path, build: Path) -> None:
    slide_url = (root / "demo" / "slides.html").as_uri()
    for slide_number in range(1, 7):
        run(
            [
                "playwright",
                "screenshot",
                "--viewport-size=1600,900",
                "--wait-for-timeout=100",
                f"{slide_url}?slide={slide_number}",
                str(build / f"slide-{slide_number}.png"),
            ],
            cwd=root,
        )
    run(
        [
            "playwright",
            "screenshot",
            "--viewport-size=1600,900",
            "--wait-for-timeout=100",
            (root / "artifacts" / "envmutationbench" / "report.html").as_uri(),
            str(build / "report.png"),
        ],
        cwd=root,
    )


def record_terminal(root: Path, build: Path) -> None:
    template = (root / "demo" / "fidelitygate.tape").read_text(encoding="utf-8")
    tape = build / "fidelitygate.tape"
    tape.write_text(template.replace("__REPO_ROOT__", str(root)), encoding="utf-8")
    run(["vhs", str(tape)], cwd=root)


def narration_audio(root: Path, build: Path, segment: Segment) -> tuple[Path, float]:
    output = build / f"{segment.key}.aiff"
    run(
        [
            "say",
            "-v",
            "Samantha",
            "-r",
            "190",
            "-o",
            str(output),
            segment.narration,
        ],
        cwd=root,
    )
    return output, duration(output, cwd=root) + 0.35


def segment_video(
    root: Path,
    build: Path,
    segment: Segment,
    audio: Path,
    segment_duration: float,
) -> Path:
    output = build / f"{segment.key}.mp4"
    if segment.visual == "terminal":
        source = build / segment.source
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(source),
                "-i",
                str(audio),
                "-filter_complex",
                (
                    "[0:v]scale=1600:900:force_original_aspect_ratio=decrease,"
                    "pad=1600:900:(ow-iw)/2:(oh-ih)/2:#090e19,"
                    "tpad=stop_mode=clone:stop_duration=90,format=yuv420p[v]"
                ),
                "-map",
                "[v]",
                "-map",
                "1:a:0",
                "-t",
                f"{segment_duration:.3f}",
                "-r",
                "30",
                "-c:v",
                "libx264",
                "-crf",
                "20",
                "-preset",
                "medium",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-ar",
                "48000",
                "-ac",
                "2",
                str(output),
            ],
            cwd=root,
        )
        return output

    source = build / (
        f"slide-{segment.source}.png" if segment.visual == "slide" else segment.source
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(source),
            "-i",
            str(audio),
            "-t",
            f"{segment_duration:.3f}",
            "-vf",
            (
                "scale=1600:900:force_original_aspect_ratio=decrease,"
                "pad=1600:900:(ow-iw)/2:(oh-ih)/2:#090e19,format=yuv420p"
            ),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-crf",
            "20",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            str(output),
        ],
        cwd=root,
    )
    return output


def timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{millis:03d}"


def caption_chunks(text: str) -> list[str]:
    words = text.split()
    return [" ".join(words[index : index + 9]) for index in range(0, len(words), 9)]


def write_subtitles(
    build: Path, timings: list[tuple[Segment, float, float]]
) -> tuple[Path, list[Caption]]:
    lines: list[str] = []
    captions: list[Caption] = []
    counter = 1
    for segment, start, segment_duration in timings:
        chunks = caption_chunks(segment.narration)
        word_counts = [len(chunk.split()) for chunk in chunks]
        total_words = sum(word_counts)
        cursor = start
        usable_duration = max(0.5, segment_duration - 0.15)
        for chunk, word_count in zip(chunks, word_counts, strict=True):
            chunk_duration = usable_duration * word_count / total_words
            end = cursor + chunk_duration
            lines.extend([str(counter), f"{timestamp(cursor)} --> {timestamp(end)}", chunk, ""])
            captions.append(Caption(start=cursor, end=end, text=chunk))
            counter += 1
            cursor = end
    output = build / "captions.srt"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output, captions


def render_caption_track(
    root: Path, build: Path, captions: list[Caption], total_duration: float
) -> Path:
    frames = build / "caption-frames"
    frames.mkdir(parents=True, exist_ok=True)
    blank = frames / "blank.png"
    Image.new("RGBA", (1600, 130), (0, 0, 0, 0)).save(blank)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 38)

    entries: list[tuple[Path, float]] = []
    cursor = 0.0
    for index, caption in enumerate(captions, start=1):
        if caption.start > cursor + 0.001:
            entries.append((blank, caption.start - cursor))
        image = Image.new("RGBA", (1600, 130), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bounds = draw.textbbox((0, 0), caption.text, font=font)
        text_width = bounds[2] - bounds[0]
        text_height = bounds[3] - bounds[1]
        x = (1600 - text_width) // 2
        y = (130 - text_height) // 2 - 4
        draw.rounded_rectangle(
            (x - 20, y - 13, x + text_width + 20, y + text_height + 17),
            radius=14,
            fill=(9, 14, 25, 215),
        )
        draw.text((x, y), caption.text, font=font, fill=(255, 255, 255, 255))
        path = frames / f"caption-{index:03d}.png"
        image.save(path)
        entries.append((path, caption.end - caption.start))
        cursor = caption.end
    if total_duration > cursor:
        entries.append((blank, total_duration - cursor))

    concat = build / "captions-concat.txt"
    concat_lines: list[str] = []
    for path, frame_duration in entries:
        concat_lines.extend([f"file '{path.as_posix()}'", f"duration {frame_duration:.6f}"])
    concat_lines.append(f"file '{entries[-1][0].as_posix()}'")
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    output = build / "captions.mov"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-vf",
            "fps=30,format=rgba",
            "-t",
            f"{total_duration:.3f}",
            "-c:v",
            "qtrle",
            str(output),
        ],
        cwd=root,
    )
    return output


def assemble(
    root: Path,
    build: Path,
    videos: list[Path],
    caption_track: Path,
    total_duration: float,
) -> Path:
    concat = build / "concat.txt"
    concat.write_text("".join(f"file '{video.as_posix()}'\n" for video in videos), encoding="utf-8")
    assembled = build / "assembled.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(assembled),
        ],
        cwd=root,
    )
    output = root / "demo" / "fidelitygate-demo.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(assembled),
            "-i",
            str(caption_track),
            "-filter_complex",
            "[0:v][1:v]overlay=0:735:shortest=1,format=yuv420p[v]",
            "-map",
            "[v]",
            "-map",
            "0:a:0",
            "-t",
            f"{total_duration:.3f}",
            "-c:v",
            "libx264",
            "-crf",
            "20",
            "-preset",
            "medium",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ],
        cwd=root,
    )
    return output


def verify_video(root: Path, output: Path) -> None:
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    probe = json.loads(completed.stdout)
    video_duration = float(probe["format"]["duration"])
    codec_types = {stream["codec_type"] for stream in probe["streams"]}
    if video_duration >= 300:
        raise RuntimeError(f"demo exceeds five minutes: {video_duration:.2f}s")
    if not {"video", "audio"}.issubset(codec_types):
        raise RuntimeError("demo must contain both video and audio streams")
    run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], cwd=root)
    print(f"Built {output} ({video_duration:.2f}s).")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    build = root / "demo" / "build"
    build.mkdir(parents=True, exist_ok=True)
    require_tools(["ffmpeg", "ffprobe", "playwright", "vhs", "say"])
    screenshot_slides(root, build)
    record_terminal(root, build)

    videos: list[Path] = []
    timings: list[tuple[Segment, float, float]] = []
    cursor = 0.0
    for segment in SEGMENTS:
        audio, segment_duration = narration_audio(root, build, segment)
        videos.append(segment_video(root, build, segment, audio, segment_duration))
        timings.append((segment, cursor, segment_duration))
        cursor += segment_duration
    subtitle_path, captions = write_subtitles(build, timings)
    shutil.copyfile(subtitle_path, root / "demo" / "fidelitygate-demo.srt")
    shutil.copyfile(build / "slide-1.png", root / "demo" / "thumbnail.png")
    caption_track = render_caption_track(root, build, captions, cursor)
    output = assemble(root, build, videos, caption_track, cursor)
    verify_video(root, output)


if __name__ == "__main__":
    main()
