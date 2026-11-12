"""OCR の結果を青空文庫の本文と突き合わせて、表記の違いと誤りの候補に分ける。

使い方: python3 compare_aozora.py OCRディレクトリ 青空文庫.txt 出力.tsv [--min-repeat 3]

1935 年の本（旧字・旧かな）と、青空文庫（2004 年の全集、新字・新かな）は表記が違う。
そこで、1 文字ずつ並べたときの置き換えのうち、本の中で何度も出るもの（賣→売、ゐ→い など）を表記の違いとし、
まれな置き換えだけを誤りの候補にする。句読点・括弧・記号は版で付け方が違うので数えない。
候補には、版の違い（言い回しの直し）も混じる。誤り率は、候補を画像で確かめて決める。
"""
import argparse
import collections
import re
import subprocess
import tempfile
from pathlib import Path

SMALL = str.maketrans("ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ", "あいうえおつやゆよわアイウエオツヤユヨワカケ")
LETTER = re.compile(r"[ぁ-ゖァ-ヺー一-鿿々豈-﫿0-9０-９]")


def letters(text):
    """ゝゞを前の字に開き、小書きの仮名を大きくして、字だけを残す。"""
    out = []
    prev = ""
    for ch in text:
        if ch == "々" and out:
            # 「大將々々」のように続くときは、前の 2 字を繰り返す
            if prev == "々":
                out[-1:] = out[-3:-1]
            else:
                out.append(out[-1])
        elif ch in "ゝヽ" and out:
            out.append(out[-1])
        elif ch in "ゞヾ" and out:
            out.append(chr(ord(out[-1]) + 1))
        elif LETTER.match(ch):
            out.append(ch)
        prev = ch
    return "".join(out).translate(SMALL)


def ocr_text(ocr_dir, first, last):
    pages = []
    for path in sorted(Path(ocr_dir).glob("*.txt"))[first - 1:last]:
        lines = []
        for line in path.read_text().splitlines():
            bare = re.sub(r"\s", "", line)
            # 柱（書名）、ノンブル、撮影用のカラーチャートの字は本文ではない
            if re.fullmatch(r"[一寸法師]{3,4}|師法寸一|[0-9０-９\-]*|[\x00-\x7f]*", bare):
                continue
            lines.append(line)
        pages.append((path.stem, letters("".join(lines))))
    return pages


def aozora_text(path):
    text = Path(path).read_text()
    text = text.split("-------------------------------------------------------")[2]
    text = text.split("底本：")[0]
    # 1935 年の本にない「作者の言葉」（冒頭）と、全集の注（末尾）を外す
    text = re.sub(r"［＃ここから６字下げ］.*?［＃ここで字下げ終わり］", "", text, flags=re.S)
    text = re.sub(r"《[^》]*》|［＃[^］]*］|｜", "", text)
    return letters(text)


def diff(a, b):
    """GNU diff で 1 字 1 行にして並べる（長い文でも速い）。"""
    with tempfile.TemporaryDirectory() as tmp:
        fa, fb = Path(tmp, "a"), Path(tmp, "b")
        fa.write_text("\n".join(a) + "\n")
        fb.write_text("\n".join(b) + "\n")
        out = subprocess.run(["diff", str(fa), str(fb)], capture_output=True, text=True).stdout
    hunks = []
    for m in re.finditer(r"^(\d+)(?:,(\d+))?([acd])(\d+)(?:,(\d+))?$", out, re.M):
        a1, a2, op, b1, b2 = m.groups()
        a1, b1 = int(a1), int(b1)
        a2, b2 = int(a2 or a1), int(b2 or b1)
        if op == "a":
            # 「a1 の後ろに挿入」なので、0 始まりの位置は a1、置き換える範囲は空
            hunks.append((a1, a1, "", b[b1 - 1:b2]))
        elif op == "d":
            hunks.append((a1 - 1, a2, a[a1 - 1:a2], ""))
        else:
            hunks.append((a1 - 1, a2, a[a1 - 1:a2], b[b1 - 1:b2]))
    return [(start, end, old, new) for start, end, old, new in hunks]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ocr_dir")
    parser.add_argument("aozora")
    parser.add_argument("output")
    parser.add_argument("--min-repeat", type=int, default=3)
    parser.add_argument("--pages", default="1-9999", help="OCR のページの範囲（例 6-114）")
    args = parser.parse_args()

    first, last = map(int, args.pages.split("-"))
    pages = ocr_text(args.ocr_dir, first, last)
    page_of = []
    for stem, text in pages:
        page_of.extend([stem] * len(text))
    ocr = "".join(text for _, text in pages)
    ref = aozora_text(args.aozora)
    hunks = diff(ocr, ref)

    # 置き換えの出てくる回数。同じ長さの置き換えは 1 字ずつの組でも数える
    pair_count = collections.Counter((old, new) for _, _, old, new in hunks)
    char_count = collections.Counter()
    for _, _, old, new in hunks:
        if old and len(old) == len(new):
            char_count.update(zip(old, new))

    def orthographic(start, old, new):
        # くの字点（〳〵）は字として数えないので、青空文庫で繰り返しを書いた分が挿入として出る
        if not old and ocr[max(0, start - len(new)):start] == new:
            return True
        if pair_count[(old, new)] >= args.min_repeat:
            return True
        return bool(old) and len(old) == len(new) and all(
            char_count[p] >= args.min_repeat for p in zip(old, new))

    # 長い塊（どちらかが 200 字以上）は、範囲の外（扉・ほかの作品）か、列やページごとの抜け。数えずに表示する
    big = [h for h in hunks if len(h[2]) >= 200 or len(h[3]) >= 200]
    rows, ortho, cand_chars = [], 0, 0
    ortho_pairs = collections.Counter()
    ortho_rows = []
    for start, end, old, new in hunks:
        if len(old) >= 200 or len(new) >= 200:
            continue
        if orthographic(start, old, new):
            ortho += max(len(old), len(new))
            ortho_pairs[(old, new)] += 1
            ortho_rows.append((page_of[min(start, len(page_of) - 1)], ocr[max(0, start - 6):start], old, new, ocr[end:end + 6]))
            continue
        cand_chars += max(len(old), len(new))
        page = page_of[min(start, len(page_of) - 1)]
        rows.append((page, ocr[max(0, start - 6):start], old, new, ocr[end:end + 6]))
    with open(args.output, "w") as f:
        f.write("page\tbefore\tocr\taozora\tafter\n")
        for row in rows:
            f.write("\t".join(row) + "\n")
    body = len(ocr) - sum(len(h[2]) for h in big)
    for start, end, old, new in big:
        print(f"長い塊（数えない）: {page_of[min(start, len(page_of) - 1)]} OCR {len(old)} 字／青空文庫 {len(new)} 字"
              f" OCR「{old[:20]}」青空文庫「{new[:20]}」")
    print(f"OCR の字数: {len(ocr)}（長い塊を除いた本文 {body} 字）")
    print(f"青空文庫の字数: {len(ref)}")
    print(f"表記の違いとみなした字: {ortho}")
    with open(Path(args.output).with_suffix(".ortho.tsv"), "w") as f:
        f.write("count\tocr\taozora\n")
        for (old, new), count in ortho_pairs.most_common():
            f.write(f"{count}\t{old}\t{new}\n")
    with open(Path(args.output).with_suffix(".ortho-rows.tsv"), "w") as f:
        f.write("page\tbefore\tocr\taozora\tafter\n")
        for row in ortho_rows:
            f.write("\t".join(row) + "\n")
    print(f"誤りの候補: {len(rows)} か所、{cand_chars} 字（本文 1 万字あたり {cand_chars / body * 10000:.0f} 字）")


if __name__ == "__main__":
    main()
