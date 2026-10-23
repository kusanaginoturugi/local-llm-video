#!/usr/bin/env python3
"""台本 (script.tsv) を VOICEVOX で一括合成する。

  python3 synth.py              # 未合成の行だけ合成し、all.wav と timeline.tsv を作り直す
  EPISODE=ep01 python3 synth.py # 回を選ぶ（指定がなければいちばん新しい回）
  python3 synth.py --force      # 全行を合成し直す
  python3 synth.py --only 22,92 # 指定した行だけ合成し直す
  python3 synth.py --kana       # 合成せず、英字を含む行の読み（カナ）を表示する
  python3 synth.py --kana all   # 合成せず、全行の読みを表示する

読みの置き換えは 3 段で行う（VOICEVOX のユーザー辞書は変更しない）。
  1. direction.tsv の yomi 列: その行だけの読み（例: 九割五分=きゅうわりごぶ;黄色=きいろ）
  2. その回の dict.tsv: この動画だけで使う語
  3. voice/dict_common.tsv: シリーズ共通の技術用語
台本・演出・その回の辞書は episodes/epNN/ に置き、出力は episodes/epNN/out/voice/ に書く。
英字の語は単語の区切りでだけ置き換える（ini が Gemini に当たらないように）。
行ごとの演出（スタイル・抑揚・前の間・動き）は direction.tsv で指定する。
辞書ではどうしても区切りやアクセントが直らない行は、direction.tsv の kana 列に読みを AquesTalk 風の
カナ（--kana の表示と同じ記法。' がアクセント、/ が区切り、_ が無声化）で書くと、その行だけ置き換える。
"""
import argparse
import array
import csv
import math
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import episode  # noqa: E402
ENGINE = os.environ.get("VOICEVOX_URL", "http://localhost:50021")

# 話者ごとの設定。id は VOICEVOX のスタイル ID、pan は左右の位置（-1 左 〜 0 中央 〜 1 右）
SPEAKERS = {
    "めたん": {"slug": "metan", "id": 2, "speedScale": 1.0, "pan": -0.35},
    "ずんだもん": {"slug": "zundamon", "id": 3, "speedScale": 1.18, "pan": 0.35},
    # 第3弾のデモで返事をする voice-chat のキャラ。解説役とは別人なので中央から鳴らし、速さは voice-chat の設定に合わせる
    "パソコンのずんだもん": {"slug": "pc_zundamon", "id": 3, "speedScale": 1.15, "pan": 0.0, "base": "ずんだもん"},
    "パソコンのめたん": {"slug": "pc_metan", "id": 2, "speedScale": 1.0, "pan": 0.0, "base": "めたん"},
    # 第3弾のデモで voice-chat に話しかける役（冥鳴ひまり）。解説の 2 人と聞き分けやすいよう別の声にし、中央から鳴らす
    "ひまり": {"slug": "himari", "id": 14, "speedScale": 1.0, "pan": 0.0, "sing_id": 3014},
}
GAP_SEC = 0.35  # all.wav で行と行の間に入れる無音（direction.tsv の gap で上書き）


def load_tsv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def replace_words(text, words):
    """表記 → 読みの置き換え。長い表記から先に当てる（Linux より Arch Linux を優先）。"""
    for surface, reading in sorted(words, key=lambda w: len(w[0]), reverse=True):
        if surface.isascii():
            # 英字の語の途中には当てない（CUDA0 のように数字が続くのは当てる）
            text = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(surface)}(?![A-Za-z_])", reading, text)
        else:
            text = text.replace(surface, reading)
    return text


def line_words(yomi):
    """direction.tsv の yomi 列（表記=読み;表記=読み）を分解する。"""
    return [tuple(p.split("=", 1)) for p in (yomi or "").split(";") if "=" in p]


def apply_dict(text, yomi, episode_words, common):
    for words in (line_words(yomi), episode_words, common):
        text = replace_words(text, words)
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
        spk["id"] = styles[spk.get("base", r["speaker"])][d["style"]]
    if d.get("intonation"):
        spk["intonationScale"] = float(d["intonation"])
    return spk


SING_QUERY_SPEAKER = 6000  # 楽譜から歌い方（音の高さと長さ）を作る歌い手（波音リツ）。声はその行の話者で出す
FADE_SEC = 5.0  # 歌の行は、終わりをこの秒数かけてフェードアウトする（楽譜の JSON の fade で変えられる）


def sing_line(base, spk, score_name):
    """direction.tsv の sing 列に書いた楽譜（その回のフォルダの JSON）を、話者の声で歌わせる。

    VOICEVOX の歌は 2 段階: /sing_frame_audio_query で楽譜から歌い方を作り、/frame_synthesis で声にする。
    長い楽譜を一度に渡すと推論に失敗するので、楽譜の休符（key が null）で区切ってフレーズごとに歌わせ、つなぐ。
    口パクは付けないので、口パク用のクエリは空にしておく。
    """
    with open(episode.path(score_name)) as f:
        score_file = json.load(f)
    notes = score_file["notes"]
    phrases, cur = [], []
    for n in notes:
        if n["key"] is None and cur:
            phrases.append(cur)
            cur = []
        cur.append(n)
    if any(n["key"] is not None for n in cur):
        phrases.append(cur)
    params, frames = None, bytearray()
    rest = {"key": None, "frame_length": 10, "lyric": ""}
    for ph in phrases:
        score = {"notes": ([] if ph[0]["key"] is None else [rest]) + ph + [rest]}
        q = json.loads(post("/sing_frame_audio_query", {"speaker": SING_QUERY_SPEAKER}, score))
        with open(base + ".wav", "wb") as f:
            f.write(post("/frame_synthesis", {"speaker": spk["sing_id"]}, q))
        with wave.open(base + ".wav") as w:
            params = params or w.getparams()
            frames += w.readframes(w.getnframes())
    n, fade = len(frames) // 2, int(score_file.get("fade", FADE_SEC) * params.framerate)  # 楽譜の fade で上書きできる
    for i in range(max(0, n - fade), n):  # 終わりを直線で絞る（16bit モノラル）
        v = int.from_bytes(frames[i * 2:i * 2 + 2], "little", signed=True)
        frames[i * 2:i * 2 + 2] = int(v * (n - i) / fade).to_bytes(2, "little", signed=True)
    with wave.open(base + ".wav", "wb") as w:
        w.setparams(params)
        w.writeframes(bytes(frames))
    with open(base + ".json", "w") as f:
        json.dump({"accent_phrases": [], "speedScale": 1.0, "prePhonemeLength": 0.0}, f)


def make_query(text, spk, kana=None):
    q = json.loads(post("/audio_query", {"speaker": spk["id"], "text": text}))
    if kana:
        # direction.tsv の kana 列（AquesTalk 風の記法）で、読みと区切りとアクセントを丸ごと置き換える
        q["accent_phrases"] = json.loads(post("/accent_phrases", {"speaker": spk["id"], "text": kana, "is_kana": "true"}))
        q["kana"] = kana
    q["speedScale"] = spk["speedScale"]
    if "intonationScale" in spk:
        q["intonationScale"] = spk["intonationScale"]
    return q


def pan_stereo(frames, pan):
    """16bit モノラルを、左右の音量の合計が変わらない配分（定パワーパン）でステレオにする。"""
    angle = (pan + 1) * math.pi / 4
    gl, gr = math.cos(angle) * math.sqrt(2), math.sin(angle) * math.sqrt(2)
    mono = array.array("h", frames)
    out = array.array("h", bytes(len(frames) * 2))
    out[0::2] = array.array("h", (max(-32768, min(32767, int(v * gl))) for v in mono))
    out[1::2] = array.array("h", (max(-32768, min(32767, int(v * gr))) for v in mono))
    return out.tobytes()


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

    rows = load_tsv(episode.path("script.tsv"))
    words = [(w["surface"], w["reading"]) for w in load_tsv(episode.path("dict.tsv"))]
    common = [(w["surface"], w["reading"]) for w in load_tsv(os.path.join(HERE, "dict_common.tsv"))]
    direction = {d["no"]: d for d in load_tsv(episode.path("direction.tsv"))}
    styles = style_ids()
    only = {int(n) for n in args.only.split(",")} if args.only else None
    out_dir = episode.VOICE_OUT
    os.makedirs(out_dir, exist_ok=True)

    if args.kana:
        for r in rows:
            if args.kana == "all" or any(c.isascii() and c.isalpha() for c in r["text"]):
                q = make_query(apply_dict(r["text"], direction.get(r["no"], {}).get("yomi"), words, common),
                               voice_for(r, direction, styles), direction.get(r["no"], {}).get("kana"))
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
        if direction.get(r["no"], {}).get("sing"):
            sing_line(base, spk, direction[r["no"]]["sing"])
            print(f"{no:03d} {r['speaker']}: （歌）{direction[r['no']]['sing']}", file=sys.stderr)
            continue
        q = make_query(apply_dict(r["text"], direction.get(r["no"], {}).get("yomi"), words, common), spk,
                       direction.get(r["no"], {}).get("kana"))
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
            chunks.append(b"\0" * int(gap * p.framerate) * p.sampwidth * 2)
            t += gap
        dur = len(frames) / (p.sampwidth * p.nchannels * p.framerate)
        timeline.append((no, r["speaker"], round(t, 3), round(t + dur, 3), d.get("motion", ""), r["text"]))
        chunks.append(pan_stereo(frames, spk["pan"]))  # 立ち位置に合わせて左右に振る
        t += dur
    with wave.open(os.path.join(out_dir, "all.wav"), "wb") as w:
        w.setparams(params._replace(nchannels=2))
        w.writeframes(b"".join(chunks))
    with open(os.path.join(out_dir, "timeline.tsv"), "w") as f:
        f.write("no\tspeaker\tstart\tend\tmotion\ttext\n")
        for row in timeline:
            f.write("\t".join(map(str, row)) + "\n")
    print(f"all.wav: {t:.1f} 秒 / {len(rows)} 行", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
