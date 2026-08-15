#!/usr/bin/env python3
"""Preprocess a lecture recording into material the skill can actually read.

A video is two things a model cannot touch directly: moving pictures and
sound. This script flattens both into files it can:

    frames/          one PNG per distinct slide state, named by timestamp
    frames/extra/    near-duplicate frames that were folded away (build-up
                     steps, spotlight moves) - kept in case a trace needs them
    sheets/          contact sheets of the kept frames, for cheap triage
    transcript.srt   whisper output, timestamped
    index.md         the alignment: for each kept frame, what was said
                     while it was on screen

Requires ffmpeg/ffprobe and whisper-cli on PATH (brew install ffmpeg
whisper-cpp), plus a ggml model file.

Usage:
    python3 extract_video.py lecture.mp4
    python3 extract_video.py slides.mp4 --audio-from camera.mp4
        (Panopto often stores the screen capture and the camera/audio as
         two separate streams - download both, point --audio-from at the
         one with sound)
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_MODEL = Path.home() / ".local/share/whisper-cpp/ggml-large-v3-turbo.bin"

# Mean absolute pixel difference (0-255) on a 16x16 grayscale thumbnail,
# below which two consecutive frames count as "the same slide state".
# Double-triggers from fade transitions land near 0; a new bullet line on a
# slide lands around 2-5; an actual slide change lands well above 10.
DEDUP_THRESHOLD = 6.0


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=False, **kw)


def die(msg):
    sys.exit(f"extract_video: {msg}")


def check_tools():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"{tool} not found - brew install ffmpeg")
    if not shutil.which("whisper-cli"):
        die("whisper-cli not found - brew install whisper-cpp")


def probe_duration(video):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(video)]).stdout
    return float(out.strip())


def has_audio(video):
    out = run(["ffprobe", "-v", "error", "-select_streams", "a",
               "-show_entries", "stream=index", "-of", "csv=p=0", str(video)]).stdout
    return bool(out.strip())


def extract_audio(video, wav):
    print(f"[1/5] extracting audio from {video.name} ...")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video),
         "-vn", "-ar", "16000", "-ac", "1", str(wav)])


def transcribe(wav, outdir, model, lang):
    print(f"[2/5] transcribing with whisper ({model.name}) - this is the slow part ...")
    prefix = outdir / "transcript"
    run(["whisper-cli", "-m", str(model), "-f", str(wav),
         "-l", lang, "-osrt", "-of", str(prefix), "--no-prints"])
    srt = prefix.with_suffix(".srt")
    if not srt.exists() or srt.stat().st_size == 0:
        die("whisper produced no transcript")
    return srt


def extract_raw_frames(video, rawdir, scene_threshold):
    """Scene-detect frames; returns [(path, seconds), ...] in time order."""
    print(f"[3/5] scene-detecting frames (threshold {scene_threshold}) ...")
    rawdir.mkdir(parents=True)
    log = rawdir / "showinfo.log"
    with open(log, "wb") as f:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "info", "-i", str(video),
             "-vf", f"select='eq(n,0)+gt(scene,{scene_threshold})',showinfo",
             "-fps_mode", "vfr", str(rawdir / "%05d.png")],
            check=True, stdout=subprocess.DEVNULL, stderr=f)
    times = [float(m) for m in
             re.findall(rb"pts_time:([0-9.]+)", log.read_bytes())]
    frames = sorted(rawdir.glob("*.png"))
    if len(frames) != len(times):
        die(f"frame/timestamp mismatch: {len(frames)} frames, {len(times)} timestamps")
    return list(zip(frames, times))


def thumbnail_bytes(png):
    """16x16 grayscale raw bytes - enough to tell slide states apart."""
    out = run(["ffmpeg", "-v", "error", "-i", str(png),
               "-vf", "scale=16:16,format=gray", "-f", "rawvideo", "-"]).stdout
    if len(out) != 256:
        die(f"unexpected thumbnail size for {png}")
    return out


def mean_abs_diff(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def dedup_frames(raw, framedir):
    """Group runs of near-identical consecutive frames, keep the last of
    each run (the completed build-up state), move the rest to extra/."""
    print(f"[4/5] deduplicating {len(raw)} raw frames ...")
    framedir.mkdir(parents=True)
    extradir = framedir / "extra"
    extradir.mkdir()

    thumbs = [thumbnail_bytes(p) for p, _ in raw]
    groups = []  # each group: list of (path, t)
    for i, item in enumerate(raw):
        if i > 0 and mean_abs_diff(thumbs[i - 1], thumbs[i]) < DEDUP_THRESHOLD:
            groups[-1].append(item)
        else:
            groups.append([item])

    kept = []
    for group in groups:
        path, t = group[-1]  # last frame = completed state
        mm, ss = int(t) // 60, int(t) % 60
        name = f"{len(kept):03d}_t{mm:02d}m{ss:02d}s.png"
        shutil.copy(path, framedir / name)
        earlier = [gt for _, gt in group[:-1]]
        kept.append((name, t, earlier))
        for j, (epath, et) in enumerate(group[:-1]):
            emm, ess = int(et) // 60, int(et) % 60
            shutil.copy(epath, extradir / f"{len(kept)-1:03d}_{j:02d}_t{emm:02d}m{ess:02d}s.png")
    return kept


def contact_sheets(framedir, sheetdir):
    frames = sorted(p for p in framedir.glob("*.png"))
    if not frames:
        return 0
    sheetdir.mkdir(parents=True)
    # feed an explicit concat list so glob quirks can't reorder anything
    listfile = sheetdir / "_frames.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\nduration 1\n" for p in frames))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(listfile), "-vf", "scale=320:-1,tile=4x6",
         "-fps_mode", "passthrough", str(sheetdir / "sheet_%02d.png")])
    listfile.unlink()
    return len(list(sheetdir.glob("sheet_*.png")))


def parse_srt(srt):
    """Returns [(start_seconds, text), ...]."""
    segs = []
    for block in srt.read_text().split("\n\n"):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->", block)
        if not m:
            continue
        h, mi, s, ms = (int(g) for g in m.groups())
        start = h * 3600 + mi * 60 + s + ms / 1000
        text = " ".join(line.strip() for line in block.splitlines()
                        if line.strip() and "-->" not in line
                        and not line.strip().isdigit())
        if text:
            segs.append((start, text))
    return segs


def fmt_t(t):
    return f"{int(t) // 60:02d}:{int(t) % 60:02d}"


def write_index(outdir, video, duration, kept, segs, n_sheets):
    print("[5/5] writing index.md ...")
    lines = [
        "# Video source index",
        "",
        f"- source: `{video.name}`",
        f"- duration: {fmt_t(duration)}",
        f"- kept frames: {len(kept)} (near-duplicates in `frames/extra/`)",
        f"- contact sheets: {n_sheets} in `sheets/` - triage there first, "
        "then open individual frames",
        f"- transcript: `transcript.srt` ({len(segs)} segments)",
        "",
        "Each section below is one kept frame and everything said while it",
        "was on screen. Frame filenames carry their timestamp.",
        "",
    ]
    bounds = [t for _, t, _ in kept] + [duration]
    for i, (name, t, earlier) in enumerate(kept):
        lines.append(f"## frame {name}  ({fmt_t(t)})")
        if earlier:
            lines.append(f"- {len(earlier)} earlier build-up state(s) at "
                         + ", ".join(fmt_t(e) for e in earlier)
                         + " (see `frames/extra/`)")
        spoken = [f"- [{fmt_t(s)}] {text}" for s, text in segs
                  if bounds[i] <= s < bounds[i + 1]]
        lines.extend(spoken if spoken else ["- (nothing spoken)"])
        lines.append("")
    (outdir / "index.md").write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video", type=Path, help="video whose picture shows the slides")
    ap.add_argument("--audio-from", type=Path, default=None,
                    help="separate video carrying the audio track (dual-stream recordings)")
    ap.add_argument("--outdir", type=Path, default=None,
                    help="output directory (default: <video>_extracted next to the video)")
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--scene", type=float, default=0.08,
                    help="ffmpeg scene-change threshold (default 0.08)")
    args = ap.parse_args()

    check_tools()
    if not args.video.exists():
        die(f"no such file: {args.video}")
    if not args.model.exists():
        die(f"whisper model not found at {args.model}\n"
            f"  mkdir -p {args.model.parent} && curl -L -o {args.model} \\\n"
            "  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin")

    audio_src = args.audio_from or args.video
    if not has_audio(audio_src):
        die(f"{audio_src.name} has no audio track"
            + ("" if args.audio_from else " - pass --audio-from <file with sound>"))

    outdir = args.outdir or args.video.parent / (args.video.stem + "_extracted")
    if outdir.exists():
        die(f"{outdir} already exists - remove it or pick another --outdir")
    outdir.mkdir(parents=True)

    duration = probe_duration(args.video)
    wav = outdir / "_audio.wav"
    rawdir = outdir / "_raw_frames"
    try:
        extract_audio(audio_src, wav)
        srt = transcribe(wav, outdir, args.model, args.lang)
        raw = extract_raw_frames(args.video, rawdir, args.scene)
        kept = dedup_frames(raw, outdir / "frames")
        n_sheets = contact_sheets(outdir / "frames", outdir / "sheets")
        write_index(outdir, args.video, duration, kept, parse_srt(srt), n_sheets)
    finally:
        wav.unlink(missing_ok=True)  # 80+ MB of pure intermediate, always drop
        shutil.rmtree(rawdir, ignore_errors=True)

    print(f"\ndone: {outdir}")
    print(f"  {len(kept)} frames kept from {len(raw)} detected, "
          f"{n_sheets} contact sheets, transcript + index.md")


if __name__ == "__main__":
    main()
