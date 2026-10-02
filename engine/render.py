"""Render one drawing Short to .mp4.

Usage:
    python -m engine.render --category mountain_lake --out media/videos/x.mp4

Progress is reported on stdout as JSON lines so the Node server can stream it:
    {"event": "progress", "stage": "render", "progress": 0.42}
    {"event": "done", "video": "...", "thumbnail": "...", ...}
"""

import argparse
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from moviepy import AudioFileClip, VideoClip, afx

from .art import PALETTES, Palette
from .frame import Compositor
from .music import MOOD_CHOICES, generate_music
from .scenes import SCENES

ROOT = Path(__file__).resolve().parent.parent
AUDIO_TYPES = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
QUOTES = json.loads((Path(__file__).parent / "quotes.json").read_text(encoding="utf-8"))


def emit(**payload):
    print(json.dumps(payload), flush=True)


def render(args):
    seed = args.seed if args.seed is not None else random.randrange(1 << 30)
    rng = random.Random(seed)
    palette = Palette(args.palette or rng.choice(list(PALETTES)))
    hook = None if args.no_hook else (args.hook or rng.choice(QUOTES))  # short quote shown on the video
    # The drawing fills the main time; the hold at the end shows the finished picture.
    duration = args.draw_seconds + args.hold_seconds
    scene = SCENES[args.category](random.Random(seed), palette, duration, hold=args.hold_seconds)
    comp = Compositor((args.width, args.height), palette.background, glow=args.glow,
                      hook_text=hook, watermark=args.watermark)
    total = max(1, round(duration * args.fps))

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    thumb = out.with_suffix(".jpg")
    comp.frame(scene, min(duration, getattr(scene, "thumb_at", duration * 0.45))).save(thumb, quality=90)

    cache = Path(tempfile.mkdtemp(prefix="drawreels_"))
    state = {"t": None, "img": None, "done": 0}

    def frame_at(t):
        i = min(int(t * args.fps + 1e-6), total - 1)
        if i != state["t"]:
            state["t"], state["img"] = i, np.asarray(comp.frame(scene, i / args.fps))
            state["done"] = max(state["done"], i + 1)
            if i % 15 == 0 or i == total - 1:
                emit(event="progress", stage="render", progress=round(state["done"] / total, 3))
        return state["img"]

    track = None
    try:
        clip = VideoClip(frame_at, duration=total / args.fps)
        audio_path, music_label = pick_music(args, rng, seed, clip.duration, cache)
        if audio_path:
            track = fit_track(AudioFileClip(str(audio_path)), clip.duration)
            clip = clip.with_audio(track)
        clip.write_videofile(
            str(out), fps=args.fps, codec="libx264", audio_codec="aac", audio_bitrate="192k", preset="medium",
            ffmpeg_params=["-crf", str(args.crf), "-movflags", "+faststart"], logger=None,
        )
        clip.close()
        emit(event="progress", stage="encode", progress=1.0)
        emit(event="done", video=str(out), thumbnail=str(thumb), seed=seed,
             palette=palette.name, hook=hook, duration=round(clip.duration, 2), music=music_label)
    finally:
        if track is not None:
            track.close()  # release the file handle so the temp folder can be removed on Windows
        shutil.rmtree(cache, ignore_errors=True)


def fit_track(track, duration):
    """Loop a short library track or trim a long one to the video, with gentle fades."""
    if track.duration < duration:
        track = track.with_effects([afx.AudioLoop(duration=duration)])
    else:
        track = track.subclipped(0, duration)
    return track.with_effects([afx.AudioFadeIn(0.4), afx.AudioFadeOut(min(2.0, duration / 4))])


def library_tracks(folder=None):
    folder = Path(folder) if folder else ROOT / "media" / "music"
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.glob("*") if p.suffix.lower() in AUDIO_TYPES)


def pick_music(args, rng, seed, duration, cache):
    """Returns (audio path or None, label). Library mode falls back to generated when empty."""
    if args.music == "off":
        return None, None
    if args.music == "library":
        tracks = library_tracks(args.music_dir)
        if tracks:
            choice = rng.choice(tracks)
            return choice, choice.name
    path, label = generate_music(duration, cache / "music.wav", seed=seed, mood=args.mood,
                                 hold=args.hold_seconds, category=args.category)
    return path, label


def main():
    p = argparse.ArgumentParser(description="Render a drawing Short")
    p.add_argument("--category", required=True, choices=sorted(SCENES))
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int)
    p.add_argument("--palette", choices=sorted(PALETTES))
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--draw-seconds", type=float, default=20, help="length of the main drawing or animation")
    p.add_argument("--hold-seconds", type=float, default=3, help="extra time showing the finished picture")
    p.add_argument("--glow", type=float, default=0.55)
    p.add_argument("--crf", type=int, default=18)
    p.add_argument("--hook", help="quote text to show (default: random from quotes.json)")
    p.add_argument("--watermark", help="banner text burned into the video (free trial Shorts)")
    p.add_argument("--music-dir", help="folder with the user's own music (library mode)")
    p.add_argument("--no-hook", action="store_true")
    p.add_argument("--music", choices=["generated", "library", "off"], default="generated")
    p.add_argument("--mood", choices=MOOD_CHOICES, default="auto",
                   help="generated music mood (default: auto, matched to the style)")
    p.add_argument("--no-music", action="store_true", help="same as --music off")
    args = p.parse_args()
    if args.no_music:
        args.music = "off"
    try:
        render(args)
    except Exception as exc:  # report to the server instead of dying silently
        emit(event="error", message=f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    sys.exit(main())
