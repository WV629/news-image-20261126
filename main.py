#!/usr/bin/env python3
"""Copy entry.png into the directory the harness grades.

The picture is rendered ahead of time by generate.py; the graded run
has no network and may not have Pillow, so this entrypoint only moves
bytes from beside itself into the output folder.
"""
import os
import shutil
import sys


def place_image():
    """Put entry.png where the harness looks for it, return exit code."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(target_dir, exist_ok=True)
    shutil.copyfile(source, os.path.join(target_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(place_image())
