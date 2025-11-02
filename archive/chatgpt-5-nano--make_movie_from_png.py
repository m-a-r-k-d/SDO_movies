# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 21:14:34 2025

@author: markd
"""

#!/usr/bin/env python3
"""
************************* UNTESTED CODE ***********************************
It was just copied in from using chatgpt-5-nano which produces quirky code. 
Some cool ideas here though.

Create an MP4 movie from a directory of PNG frames.

Usage:
  python3 src/make_movie_from_frames.py --frames-dir /path/to/frames \
      --output-video /path/to/output.mp4 [--fps 6] [--start 1 --end N] [--delete-frames]

If you want to keep the frames, omit --delete-frames.
"""

import os
import argparse
import subprocess
from shutil import which

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Assemble PNG frames into an MP4 video with FFmpeg."
    )
    parser.add_argument("--frames-dir", required=True,
                        help="Directory containing PNG frames named frame_XXXXX.png")
    parser.add_argument("--output-video", required=True,
                        help="Path to output MP4 video.")
    parser.add_argument("--fps", type=int, default=6,
                        help="Frames per second for the video.")
    parser.add_argument("--start", type=int, default=1,
                        help="Starting frame index (1-based). If you use a pattern, this is used with -start_number.")
    parser.add_argument("--end", type=int, default=None,
                        help="Ending frame index (inclusive). If omitted, use all frames.")
    parser.add_argument("--delete-frames", action="store_true",
                        help="Delete PNG frames after video creation.")
    return parser.parse_args()

def main():
    args = _parse_args()
    frames_dir = args.frames_dir
    out_video = args.output_video
    if which("ffmpeg") is None:
        print("FFmpeg not found on PATH. Please install FFmpeg.", flush=True)
        return 1

    # Build input pattern; assumes frame_00001.png, frame_00002.png, ...
    input_pattern = os.path.join(frames_dir, "frame_%05d.png")

    ffmpeg_cmd = [
        "ffmpeg",
        "-framerate", str(args.fps),
        "-start_number", "1",
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        args.output_video
    ]
    print("Running FFmpeg command:")
    print(" ".join(ffmpeg_cmd))
    rc = subprocess.call(ffmpeg_cmd)
    if rc != 0:
        print("FFmpeg failed to create the video.")
        return rc

    print(f"Video saved to: {out_video}")

    if args.delete_frames:
        for f in os.listdir(frames_dir):
            if f.lower().endswith(".png"):
                os.remove(os.path.join(frames_dir, f))
        print("Intermediate frames deleted.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())