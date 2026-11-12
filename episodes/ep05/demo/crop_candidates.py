"""誤りの候補から無作為に選び、原本の画像のその位置を切り出して 1 枚に並べる（人が画像で判定するため）。

使い方: python3 crop_candidates.py 候補.tsv OCRディレクトリ 画像ディレクトリ 出力.png [--count 40] [--seed 1]
候補.tsv は compare_aozora.py の出力。選んだ候補は 出力.tsv に番号つきで書く。
"""
import argparse
import csv
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from compare_aozora import letters

FONT = "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"


def locate(row, ocr_dir):
    """候補の前後の字から行を探し、行の中の位置（0〜1）と行の枠を返す。"""
    data = json.loads((Path(ocr_dir) / f"{row['page']}.json").read_text())
    keys = [row["before"][-3:] + row["ocr"] + row["after"][:3], row["before"][-3:] + row["ocr"],
            row["ocr"] + row["after"][:3], row["before"][-4:], row["after"][:4]]
    for key in keys:
        if not key:
            continue
        for line in (l for block in data["contents"] for l in (block if isinstance(block, list) else [block])):
            text = letters(line["text"])
            at = text.find(key)
            if at < 0:
                continue
            offset = at + (len(row["before"][-3:]) if key.startswith(row["before"][-3:]) and row["before"] else 0)
            if key == row["after"][:4]:
                offset = at
            return line["boundingBox"], (offset + 0.5) / max(1, len(text)), line["isVertical"] == "true"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates")
    parser.add_argument("ocr_dir")
    parser.add_argument("image_dir")
    parser.add_argument("output")
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    with open(args.candidates, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    sample = random.Random(args.seed).sample(rows, min(args.count, len(rows)))
    font = ImageFont.truetype(FONT, 22)
    tiles = []
    for no, row in enumerate(sample, 1):
        tile = Image.new("RGB", (260, 520), "white")
        draw = ImageDraw.Draw(tile)
        found = locate(row, args.ocr_dir)
        if found:
            box, frac, vertical = found
            xs, ys = [p[0] for p in box], [p[1] for p in box]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            page = Image.open(Path(args.image_dir) / f"{int(row['page'].rsplit('_', 1)[1]):03d}.jpg")
            width = x1 - x0
            if vertical:
                cy = y0 + (y1 - y0) * frac
                crop = page.crop((x0 - width, cy - width * 4, x1 + width, cy + width * 4))
            else:
                cx = x0 + (x1 - x0) * frac
                crop = page.crop((cx - width * 4, y0 - width, cx + width * 4, y1 + width))
            crop.thumbnail((250, 420))
            tile.paste(crop, ((260 - crop.width) // 2, 95))
        else:
            draw.text((10, 200), "位置が見つからない", fill="red", font=font)
        draw.text((6, 2), f"#{no} {row['page'][-3:]}", fill="black", font=font)
        draw.text((6, 32), f"OCR「{row['ocr'] or '（なし）'}」", fill="blue", font=font)
        draw.text((6, 62), f"青空「{row['aozora'] or '（なし）'}」", fill="darkgreen", font=font)
        tiles.append(tile)
    cols = 10
    sheet = Image.new("RGB", (260 * cols, 520 * ((len(tiles) + cols - 1) // cols)), "gray")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % cols) * 260, (i // cols) * 520))
    sheet.save(args.output)
    with open(Path(args.output).with_suffix(".tsv"), "w") as f:
        f.write("no\tpage\tbefore\tocr\taozora\tafter\tverdict\n")
        for no, row in enumerate(sample, 1):
            f.write(f"{no}\t{row['page']}\t{row['before']}\t{row['ocr']}\t{row['aozora']}\t{row['after']}\t\n")


if __name__ == "__main__":
    main()
