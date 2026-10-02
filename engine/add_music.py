"""Add background music to an already-rendered Short, in place, without re-encoding the video.

Usage:
    python -m engine.add_music --video media/videos/x.mp4 [--music generated|library] [--mood auto|calm|...] [--category mountain_lake]
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg

from .music import MOOD_CHOICES, generate_music
from .render import library_tracks


def add_music(video, mode="generated", mood=None, seed=None, music_dir=None, category=None):
    video = Path(video).resolve()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    _, duration = imageio_ffmpeg.count_frames_and_secs(str(video))
    rng = random.Random(seed)
    tmp = Path(tempfile.mkdtemp(prefix="draw-reels_music_"))
    try:
        tracks = library_tracks(music_dir) if mode == "library" else []
        if tracks:
            source = rng.choice(tracks)
            label = source.name
            audio_in = ["-stream_loop", "-1", "-i", str(source)]  # loop short tracks
        else:
            source, label = generate_music(duration, tmp / "music.wav", seed=seed, mood=mood, category=category)
            audio_in = ["-i", str(source)]
        fade_out = min(2.0, duration / 4)
        out = tmp / "out.mp4"
        subprocess.run(
            [ffmpeg, "-v", "error", "-y", "-i", str(video), *audio_in,
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-af", f"afade=t=in:d=0.4,afade=t=out:st={duration - fade_out:.2f}:d={fade_out:.2f}",
             "-t", f"{duration:.3f}", "-movflags", "+faststart", str(out)],
            check=True, capture_output=True,
        )
        os.replace(out, video)
        return label
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    p = argparse.ArgumentParser(description="Add background music to a rendered Short")
    p.add_argument("--video", required=True)
    p.add_argument("--music", choices=["generated", "library"], default="generated")
    p.add_argument("--mood", choices=MOOD_CHOICES, default="auto")
    p.add_argument("--category", help="video style id, used to match the mood")
    p.add_argument("--seed", type=int)
    p.add_argument("--music-dir")
    a = p.parse_args()
    try:
        label = add_music(a.video, a.music, a.mood, a.seed, a.music_dir, a.category)
        print(json.dumps({"event": "done", "music": label}), flush=True)
    except subprocess.CalledProcessError as exc:
        print(json.dumps({"event": "error", "message": exc.stderr.decode(errors="replace").strip()[-300:]}), flush=True)
        return 1
    except Exception as exc:
        print(json.dumps({"event": "error", "message": f"{type(exc).__name__}: {exc}"}), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
