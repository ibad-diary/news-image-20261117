"""make.fun entry: news-image-20261117.

Copies the pre-rendered entry.png (shipped next to this file) to
MAKEFUN_OUTPUT_DIR/entry.png and verifies the output: PNG magic bytes,
size <= 1 MiB, dimensions <= 1024x1024 (parsed from the IHDR chunk).
Standard library only; deterministic: the same input bytes are copied
verbatim on every run.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)

    with open(dst, "rb") as f:
        data = f.read()
    if data[:8] != PNG_MAGIC:
        print("error: not a PNG file", file=sys.stderr)
        return 1
    if len(data) > MAX_BYTES:
        print(f"error: {len(data)} bytes exceeds 1 MiB", file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        print(f"error: {width}x{height} exceeds 1024x1024", file=sys.stderr)
        return 1
    print(f"wrote {dst}: {width}x{height} PNG, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
