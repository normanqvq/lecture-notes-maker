#!/usr/bin/env python3
"""Download the Noto Sans CJK SC fonts that notes.css embeds for CJK text.

    python assets/get_fonts.py

Works the same on Windows, macOS and Linux (standard library only). The files
land in assets/fonts/ next to this script and are git-ignored (about 33 MB).
"""

import sys
import urllib.request
from pathlib import Path

BASE = ("https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/"
        "SimplifiedChinese/")
FILES = ["NotoSansCJKsc-Regular.otf", "NotoSansCJKsc-Bold.otf"]


def main():
    dest = Path(__file__).resolve().parent / "fonts"
    dest.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = dest / name
        if target.exists() and target.stat().st_size > 1_000_000:
            print(f"already present: {target}")
            continue
        print(f"downloading {name} ...")
        try:
            with urllib.request.urlopen(BASE + name) as r, open(target, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
        except Exception as e:  # network / proxy / TLS problems
            target.unlink(missing_ok=True)
            sys.exit(f"get_fonts: failed to download {name}: {e}\n"
                     f"  Fetch it manually from {BASE}{name} and put it in {dest}")
        print(f"  -> {target} ({target.stat().st_size // 1024} KB)")
    print("done")


if __name__ == "__main__":
    main()
