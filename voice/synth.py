#!/usr/bin/env python3
"""台本 (script.tsv) を VOICEVOX で一括合成する。

  python3 synth.py              # 未合成の行だけ合成し、all.wav と timeline.tsv を作り直す
  python3 synth.py --force      # 全行を合成し直す
  python3 synth.py --only 22,92 # 指定した行だけ合成し直す
  python3 synth.py --kana       # 合成せず、英字を含む行の読み（カナ）を表示する
  python3 synth.py --kana all   # 合成せず、全行の読みを表示する

読みの置き換えは dict.tsv で行う（VOICEVOX のユーザー辞書は変更しない）。
行ごとの演出（スタイル・抑揚・前の間・動き）は direction.tsv で指定する。
"""
import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.environ.get("VOICEVOX_URL", "http://localhost:50021")

# 話者ごとの設定。id は VOICEVOX のスタイル ID
SPEAKERS = {
    "めたん": {"slug": "metan", "id": 2, "speedScale": 1.0},
    "ずんだもん": {"slug": "zundamon", "id": 3, "speedScale": 1.18},
}
GAP_SEC = 0.35  # all.wav で行と行の間に入れる無音（direction.tsv の gap で上書き）


def load_tsv(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def apply_dict(text, words):
    # 長い表記から先に置き換える（Linux より Arch Linux を優先するため）
    for w in sorted(words, key=lambda w: len(w["surface"]), reverse=True):
        text = text.replace(w["surface"], w["reading"])
    # 日本語と英数字の間の半角スペースは読み上げで間が空くので取り除く
    return re.sub(r"(?<=[^\x00-\x7f]) +| +(?=[^\x00-\x7f])", "", text)


def post(path, params, body=None):
    url = f"{ENGINE}{path}?{urllib.parse.urlencode(params)}"
    data = json.dumps(body).encode() if body is not None else b""
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        return res.read()


def style_ids():
    """話者名 → {スタイル名: ID}"""
    with urllib.request.urlopen(f"{ENGINE}/speakers") as res:
        data = json.load(res)
    names = {"めたん": "四国めたん", "ずんだもん": "ずんだもん"}
    out = {}
    for short, full in names.items():
        sp = next(s for s in data if s["name"] == full)
        out[short] = {st["name"]: st["id"] for st in sp["styles"]}
    return out


def voice_for(r, direction, styles):
    """行の話者設定に、direction.tsv の指定を重ねる。"""
    spk = dict(SPEAKERS[r["speaker"]])
    d = direction.get(r["no"], {})
    if d.get("style"):
        spk["id"] = styles[r["speaker"]][d["style"]]
    if d.get("intonation"):
        spk["intonationScale"] = float(d["intonation"])
    return spk


def make_query(text, spk):
    q = json.loads(post("/audio_query", {"speaker": spk["id"], "text": text}))
    q["speedScale"] = spk["speedScale"]
    if "intonationScale" in spk:
        q["intonationScale"] = spk["intonationScale"]
    return q


def wav_frames(path):
    with wave.open(path, "rb") as w:
        return w.getparams(), w.readframes(w.getnframes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="既存の wav も作り直す")
    ap.add_argument("--only", help="合成する行番号（カンマ区切り）")
    ap.add_argument("--kana", nargs="?", const="ascii", choices=["ascii", "all"],
                    help="合成せず読みを表示する（all で全行、省略時は英字を含む行だけ）")
    args = ap.parse_args()

    rows = load_tsv("script.tsv")
    words = load_tsv("dict.tsv")
    direction = {d["no"]: d for d in load_tsv("direction.tsv")}
    styles = style_ids()
    only = {int(n) for n in args.only.split(",")} if args.only else None
    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)

    if args.kana:
        for r in rows:
            if args.kana == "all" or any(c.isascii() and c.isalpha() for c in r["text"]):
                q = make_query(apply_dict(r["text"], words), voice_for(r, direction, styles))
                print(f"{r['no']:>3} {r['text']}\n    {q['kana']}")
        return

    for r in rows:
        no, spk = int(r["no"]), SPEAKERS[r["speaker"]]
        base = os.path.join(out_dir, f"{no:03d}_{spk['slug']}")
        if only is not None and no not in only:
            continue
        if only is None and not args.force and os.path.exists(base + ".wav"):
            continue
        spk = voice_for(r, direction, styles)
        q = make_query(apply_dict(r["text"], words), spk)
        with open(base + ".wav", "wb") as f:
            f.write(post("/synthesis", {"speaker": spk["id"]}, q))
        # 口パク用に、モーラごとの長さを含むクエリも残す
        with open(base + ".json", "w") as f:
            json.dump(q, f, ensure_ascii=False)
        print(f"{no:03d} {r['speaker']}: {r['text'][:30]}", file=sys.stderr)

    # 全行をつないだ all.wav と、各行の開始・終了時刻 timeline.tsv を作る
    params, chunks, timeline, t = None, [], [], 0.0
    for r in rows:
        no, spk = int(r["no"]), SPEAKERS[r["speaker"]]
        path = os.path.join(out_dir, f"{no:03d}_{spk['slug']}.wav")
        if not os.path.exists(path):
            print(f"未合成: {path}", file=sys.stderr)
            return 1
        p, frames = wav_frames(path)
        params = params or p
        d = direction.get(r["no"], {})
        if chunks:  # 1 行目の前には間を入れない
            gap = float(d["gap"]) if d.get("gap") else GAP_SEC
            chunks.append(b"\0" * int(gap * p.framerate) * p.sampwidth * p.nchannels)
            t += gap
        dur = len(frames) / (p.sampwidth * p.nchannels * p.framerate)
        timeline.append((no, r["speaker"], round(t, 3), round(t + dur, 3), d.get("motion", ""), r["text"]))
        chunks.append(frames)
        t += dur
    with wave.open(os.path.join(out_dir, "all.wav"), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(chunks))
    with open(os.path.join(out_dir, "timeline.tsv"), "w") as f:
        f.write("no\tspeaker\tstart\tend\tmotion\ttext\n")
        for row in timeline:
            f.write("\t".join(map(str, row)) + "\n")
    print(f"all.wav: {t:.1f} 秒 / {len(rows)} 行", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
