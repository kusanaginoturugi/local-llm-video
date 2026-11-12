"""紙の色と汚れを抜いて、白い紙に黒い字だけにする（制作者の自炊用の手順と同じ背景補正）。

使い方: python3 clean.py [--threshold 25 --gain 2 --white 225] 入力.jpg... 出力ディレクトリ
ページをぼかして紙の明るさを推定し、そこより暗い差分だけを字として残す。
既定値は制作者の自炊用。墨の薄い本には --threshold 8 --gain 3 --white 235 も試した。
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def clean(image, threshold=25, gain=2, white=225):
    gray = image.convert("L")
    background = gray.filter(ImageFilter.GaussianBlur(radius=35))
    difference = np.asarray(background, dtype=np.int16) - np.asarray(gray, dtype=np.int16)
    strength = np.clip((difference - threshold) * gain, 0, 255).astype(np.uint8)
    cleaned = 255 - strength
    cleaned[cleaned > white] = 255
    return Image.fromarray(cleaned, "L")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=int, default=25)
    parser.add_argument("--gain", type=int, default=2)
    parser.add_argument("--white", type=int, default=225)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    *sources, out = args.paths
    Path(out).mkdir(parents=True, exist_ok=True)
    for source in sources:
        clean(Image.open(source), args.threshold, args.gain, args.white).save(Path(out) / Path(source).name, quality=90)


if __name__ == "__main__":
    main()
