#!/usr/bin/env python3
"""音名と長さを並べたテキストから、VOICEVOX の歌の楽譜（JSON）を作る。

  python3 voice/score.py episodes/ep03/jupiter.txt   # → episodes/ep03/jupiter.json

テキストの書き方:

  tempo 117      4 分音符を 1 分に何回打つか（既定 120）
  gain 0.75      音量（既定 1.0）
  fade 0.5       終わりを絞る秒数（既定 5）
  shift 2        全体を半音いくつ上げるか（下げるならマイナス、既定 0）
  # から行末まではコメント

  E4:8 G4:8 A4:4 A4:8 C5:8 B4:8. G4:16 | ぱそこんのなかで

1 行が 1 フレーズ。フレーズの前には短い休符が入る（長い楽譜を一度に渡すと VOICEVOX が失敗するので、
synth.py は休符でフレーズに分けて歌わせる）。

- 音名: C D E F G A B に # か b を付けてもよく、続けてオクターブ（真ん中のドが C4）。休符は r
- 長さ: 4 が 4 分音符、8 が 8 分音符、2 が 2 分音符、1 が全音符。後ろに . で付点。
  4+8 のように + でつなぐと、タイでつないだ長さになる
- | の右が歌詞。1 音に 1 モーラ（「しゃ」「きょ」のような小さい字はひとまとまり）を、休符を飛ばして順に割り当てる。
  歌詞が足りない音は、ひとつ前の歌詞をもう一度歌う（鼻歌なら「ら」を 1 つ書けば全部「ら」になる）
"""
import json
import os
import re
import sys

FPS = 93.75  # VOICEVOX の歌の 1 秒あたりのフレーム数
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SMALL = set("ゃゅょぁぃぅぇぉャュョァィゥェォ")


def morae(text):
    """歌詞を 1 モーラずつに分ける。小さい「ゃ」などは前の字とまとめる。"""
    out = []
    for ch in text.replace(" ", ""):
        if ch in SMALL and out:
            out[-1] += ch
        else:
            out.append(ch)
    return out


def key_of(name):
    """音名（例 F#4、Bb3）→ MIDI の番号。休符（r）は None。"""
    if name.lower() == "r":
        return None
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    if not m:
        raise SystemExit(f"音名が読めません: {name}")
    n, acc, octave = m.groups()
    return 12 * (int(octave) + 1) + NOTE[n] + {"#": 1, "b": -1, "": 0}[acc]


def beats(length):
    """長さ（例 8.、4+8）→ 4 分音符いくつ分か。"""
    total = 0.0
    for part in length.split("+"):
        dots = part.count(".")
        base = 4 / float(part.rstrip("."))
        total += base * (2 - 0.5 ** dots)
    return total


def convert(text):
    tempo, opts, notes = 120.0, {}, []
    for raw in text.splitlines():
        # コメントは行頭の #、または空白のあとの「# 」から（F#4 の # とまぎれないように）
        if raw.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s#\s.*$", "", raw).strip()
        if not line:
            continue
        word = line.split()[0]
        if word in ("tempo", "gain", "fade", "shift"):
            value = float(line.split()[1])
            if word == "tempo":
                tempo = value
            else:
                opts[word] = value
            continue
        tones, _, lyric = line.partition("|")
        words = morae(lyric.strip())
        notes.append({"key": None, "frame_length": 12, "lyric": ""})  # フレーズの区切り
        last = "ら"
        for token in tones.split():
            name, _, length = token.partition(":")
            key = key_of(name)
            frames = round(beats(length or "4") * 60 / tempo * FPS)
            if key is None:
                notes.append({"key": None, "frame_length": frames, "lyric": ""})
                continue
            if words:
                last = words.pop(0)
            notes.append({"key": key + int(opts.get("shift", 0)), "frame_length": frames, "lyric": last})
        if words:
            print(f"歌詞が余りました（音が足りない）: {''.join(words)}", file=sys.stderr)
    notes.append({"key": None, "frame_length": 30, "lyric": ""})
    score = {k: v for k, v in opts.items() if k in ("gain", "fade")}
    score["notes"] = notes
    return score


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    with open(src) as f:
        score = convert(f.read())
    dst = os.path.splitext(src)[0] + ".json"
    with open(dst, "w") as f:
        json.dump(score, f, ensure_ascii=False, indent=1)
    sec = sum(n["frame_length"] for n in score["notes"]) / FPS
    print(f"{dst}（{len(score['notes'])} 音、{sec:.1f} 秒）")


if __name__ == "__main__":
    main()
