#!/usr/bin/env python3
"""合成済みの音声と台本から、口パクつきの解説動画と概要欄の文面を作る。

  python3 render.py              # out/video/video.mp4 と out/video/description.txt（いちばん新しい回）
  EPISODE=ep01 python3 render.py # 回を選ぶ
  python3 render.py --preview 30 # 先頭 30 秒だけ作る（確認用）
  python3 render.py --still 64   # 指定行の 1 コマを out/still_064.png に保存
  python3 render.py --description # 概要欄の文面だけ out/description.txt に書き出す
  python3 render.py --srt         # 字幕ファイルだけ out/subtitles.srt に書き出す
"""
import argparse
import csv
import json
import math
import os
import subprocess
import sys
import tempfile
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import episode  # noqa: E402

SLIDES = episode.module("slides").SLIDES
# 画面の下の空きに出す補足（※）。{行番号: (文, 何行のあいだ出すか)}。番外編から（今の言葉で分かりにくい語の説明）
NOTES = getattr(episode.module("slides"), "NOTES", {})
META = episode.module("meta")  # 概要欄の文面とリンク
VOICE = episode.VOICE_OUT
CHARS = os.path.join(ROOT, "assets", "chars")
SLIDE_DIR = episode.SLIDE_DIR
OUT = episode.VIDEO_OUT

W, H, FPS = 1920, 1080, 30
SIDE = 440                         # 左右のキャラの列の幅（左右で同じ）
SLIDE_BOX = (80, 64, W - 80, 812)   # 画面（スライド）を置く範囲。下の角にはキャラが少しかぶる
SUB_BOX = (SIDE, 828, W - SIDE, 1052)  # 字幕
TSUMUGI_W = 210                     # 第5弾から：字幕の右に、つむぎの立つ場所を空ける
# つむぎは第5弾から本編のレギュラー。番外編（episode.NUMBER が None）も今のシリーズと同じ
TSUMUGI_REGULAR = episode.NUMBER is None or episode.NUMBER >= 5
if TSUMUGI_REGULAR:
    SUB_BOX = (SIDE, 828, W - SIDE - TSUMUGI_W, 1052)
# 第7弾から、めたんとずんだもんは Live2D（公式ショップの坂本アヒル式）で動かす。つむぎは SD 絵のまま。
# direction.tsv の react には、SD 絵の名前の代わりに Live2D の表情・モーションの名前を + でつないで書く（例 exp_sad+mtnFace_sad）
LIVE2D = episode.NUMBER is None or episode.NUMBER >= 7
LIVE2D_PY = os.path.join(ROOT, ".venv-live2d", "bin", "python")
BG = (24, 26, 33)
PANEL = (40, 43, 54)
TEXT = (236, 238, 244)
MUTED = (150, 156, 172)
HL = (255, 214, 102)
COLOR = {"めたん": (234, 96, 160), "ずんだもん": (110, 190, 70),
         "パソコンのめたん": (234, 96, 160), "パソコンのずんだもん": (110, 190, 70),
         "ひまり": (150, 140, 230), "つむぎ": (235, 173, 80), "お囃子": (190, 160, 110)}
SLUG = {"めたん": "metan", "ずんだもん": "zundamon"}
# Live2D で動かすキャラ（第7弾と番外編から）。つむぎも坂本アヒル式の Live2D にした
L2D_SLUG = {**SLUG, "つむぎ": "tsumugi"}
# 音声ファイルの名前。「パソコンの〜」は第3弾のデモで返事をする voice-chat のキャラ（立ち絵は動かさない）
VOICE_SLUG = {**SLUG, "パソコンのめたん": "pc_metan", "パソコンのずんだもん": "pc_zundamon",
              "ひまり": "himari", "つむぎ": "tsumugi", "お囃子": "ohayashi"}
FADE = 0.4  # 章の変わり目で、見出しの前後をフェードでつなぐ秒数
ANNOTATE_ONCE = True  # False にすると、用語が出るたびに毎回読みを添える
BGM = os.path.join(ROOT, "assets", "bgm", "maou_loop_bgm_acoustic51.mp3")  # 魔王魂「アコースティック51」ループ版
BG_IMAGE = os.environ.get("BG_IMAGE", os.path.join(ROOT, "assets", "bg", "rgb_desk.jpg"))  # 背景（ぼかして暗くする）。空なら単色
BG_BLUR = int(os.environ.get("BG_BLUR", 8))   # ぼかしの強さ（ガウスぼかしの半径 px）
BG_DARK = float(os.environ.get("BG_DARK", 0.55))  # 明るさ（0〜1）
# 映像のエンコーダ。NVIDIA の GPU があれば NVENC、なければ VCODEC=x264 で libx264 を使う
VIDEO_CODEC = {
    "nvenc": ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "21", "-b:v", "0"],
    "x264": ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20"],
}[os.environ.get("VCODEC", "nvenc")]
BGM_VOLUME = 0.12
SING_BGM = 0.15  # 歌の行のあいだの BGM の音量（ふだんの何割にするか）
BGM_FILTER = "highpass=f=150,lowpass=f=3500"  # 帯域を絞って声の後ろに下げる（空にすると原音のまま）

JP = "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"
JP_BOLD = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"
MONO = "/usr/share/fonts/PlemolJP/PlemolJPConsole-Regular.ttf"
EMOJI = "/usr/share/fonts/noto/NotoColorEmoji.ttf"  # カラー絵文字（109px のビットマップだけを持つ）
_fonts = {}
_cam_frames = {}
_cam_tmp = None


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size, index=0)
    return _fonts[key]


NO_HEAD = set("、。，．）」』】！？…ー・ぁぃぅぇぉっゃゅょァィゥェォッャュョ")  # 行頭に置かない文字


def wrap(text, f, width):
    """英単語は途中で切らず、句読点や閉じかっこは行頭に来ないように折り返す。"""
    import re
    tokens = re.findall(r"[A-Za-z0-9_.,:/+\-%]+|.", text)
    lines, cur = [], ""
    for tok in tokens:
        if cur and f.getlength(cur + tok) > width and tok not in NO_HEAD:
            lines.append(cur.rstrip())
            cur = tok.lstrip()
        else:
            cur += tok
    return lines + [cur] if cur else lines


EMOJI_RE = None


def draw_text_emoji(img, xy, text, f, fill):
    """絵文字だけ Noto Color Emoji で描く（ふつうのフォントだと豆腐になる）。"""
    import re
    global EMOJI_RE
    EMOJI_RE = EMOJI_RE or re.compile(r"([\U0001F000-\U0001FFFF\u2600-\u27BF\u2B00-\u2BFF]\ufe0f?)")
    d = ImageDraw.Draw(img)
    x, y = xy
    for part in EMOJI_RE.split(text):
        if not part:
            continue
        if EMOJI_RE.fullmatch(part):
            g = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((0, 0), part, font=font(EMOJI, 109), embedded_color=True)
            g = g.crop(g.getbbox() or (0, 0, 1, 1))
            sz = int(f.size * 0.95)
            g = g.resize((sz, int(g.height * sz / max(g.width, 1))), Image.LANCZOS)
            img.paste(g, (int(x), int(y + f.size * 0.2)), g)
            x += sz + 4
        else:
            d.text((x, y), part, font=f, fill=fill)
            x += f.getlength(part)


def fit_font(lines, path, start, width, mono=False):
    size = start
    while size > 16 and max(font(path, size).getlength(l) for l in lines) > width:
        size -= 2
    return font(path, size)


def screencam_frames(relative_path):
    """実録のページ部分を一時 JPEG に展開して、動画のフレームに合わせる。"""
    global _cam_tmp
    if relative_path not in _cam_frames:
        if _cam_tmp is None:
            _cam_tmp = tempfile.TemporaryDirectory(prefix="local-llm-screencam-")
        folder = os.path.join(_cam_tmp.name, str(len(_cam_frames)))
        os.makedirs(folder)
        # 第4弾のブラウザ録画はページ部分だけを切り出す。第5弾からは録画をそのまま使い、縦横比を保って枠に収める
        if episode.NAME == "ep04":
            crop = "crop=1600:755:0:0," if relative_path.endswith("-tab.mkv") else "crop=1600:755:0:145,"
        else:
            crop = ""
        subprocess.run([
            "ffmpeg", "-loglevel", "error", "-y", "-i", episode.path(relative_path),
            "-vf", f"{crop}fps=10", "-q:v", "3",
            os.path.join(folder, "%04d.jpg"),
        ], check=True)
        files = sorted(os.path.join(folder, name) for name in os.listdir(folder))
        if not files:
            raise RuntimeError(f"スクリーンカムからフレームを読めません: {relative_path}")
        _cam_frames[relative_path] = files
    return _cam_frames[relative_path]


@lru_cache(maxsize=5)
def screencam_frame(path):
    with Image.open(path) as source:
        im = source.convert("RGB")
    if episode.NAME == "ep04":
        return im.resize((1585, 748), Image.Resampling.LANCZOS)
    im.thumbnail((1585, 748), Image.Resampling.LANCZOS)
    box = Image.new("RGB", (1585, 748), im.getpixel((0, 0)))
    box.paste(im, ((1585 - im.width) // 2, (748 - im.height) // 2))
    return box


# ---------- 画面（スライド） ----------

def draw_slide(img, spec, section, elapsed=0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = SLIDE_BOX
    if section:
        d.text((x0, 20), section, font=font(JP_BOLD, 30), fill=MUTED)
    kind = spec[0]
    if kind == "image":
        im = Image.open(os.path.join(SLIDE_DIR, spec[1])).convert("RGB")
        r = min((x1 - x0) / im.width, (y1 - y0) / im.height)
        im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        img.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2))
    elif kind == "screencam":
        _, path, label, speed, source_start = spec
        frames = screencam_frames(path)
        index = min(int(max(0, source_start + elapsed * speed) * 10), len(frames) - 1)
        frame = screencam_frame(frames[index]).resize((1458, 688), Image.Resampling.LANCZOS)
        img.paste(frame, (x0 + (x1 - x0 - frame.width) // 2, y0 + 60))
        # ラベルは録画の外。翻訳の進捗表示や本文を隠さない。
        d.rounded_rectangle((x0 + 20, y0 + 4, x1 - 20, y0 + 54), 12, fill=(16, 17, 22))
        d.text((x0 + 45, y0 + 13), label, font=font(JP_BOLD, 27), fill=TEXT)
    elif kind == "title":
        _, main, sub = spec
        f = fit_font([main], JP_BOLD, 96, x1 - x0)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 40), main, font=f, fill=TEXT, anchor="ms")
        fs = font(JP, 36)
        for i, l in enumerate(wrap(sub, fs, x1 - x0)):
            d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 40 + i * 52), l, font=fs, fill=MUTED, anchor="ms")
    elif kind == "big":
        f = fit_font([spec[1]], JP_BOLD, 72, x1 - x0 - 80)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), spec[1], font=f, fill=TEXT, anchor="mm")
    elif kind == "todo":
        d.rounded_rectangle(SLIDE_BOX, 24, outline=MUTED, width=4)
        f = font(JP_BOLD, 34)
        d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 50), "収録した画面をここに入れる", font=f, fill=MUTED, anchor="mm")
        for i, l in enumerate(wrap(spec[1], font(JP, 40), x1 - x0 - 120)):
            d.text(((x0 + x1) / 2, (y0 + y1) / 2 + 20 + i * 58), l, font=font(JP, 40), fill=TEXT, anchor="mm")
    elif kind == "bullets":
        _, head, items = spec
        d.text((x0 + 40, y0 + 40), head, font=font(JP_BOLD, 56), fill=TEXT)
        y = y0 + 150
        f = font(JP, 44)
        for it in items:
            d.ellipse((x0 + 50, y + 18, x0 + 66, y + 34), fill=HL)
            for l in wrap(it, f, x1 - x0 - 140):
                d.text((x0 + 90, y), l, font=f, fill=TEXT)
                y += 62
            y += 18
    elif kind in ("term", "code"):
        if kind == "term":
            _, lines, hl = spec
            head = "ターミナル"
        else:
            _, head, lines, hl = spec
        d.rounded_rectangle(SLIDE_BOX, 18, fill=(16, 17, 22))
        d.rounded_rectangle((x0, y0, x1, y0 + 56), 18, fill=PANEL)
        d.rectangle((x0, y0 + 36, x1, y0 + 56), fill=PANEL)
        for i, c in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
            d.ellipse((x0 + 24 + i * 30, y0 + 18, x0 + 44 + i * 30, y0 + 38), fill=c)
        d.text((x0 + 130, y0 + 28), head, font=font(JP, 26), fill=MUTED, anchor="lm")
        f = fit_font([l or " " for l in lines], MONO, 40, x1 - x0 - 80)
        # 行数が多いときは高さにも収まる大きさまで下げる
        while len(lines) * f.size * 1.45 > (y1 - y0) - 110 and f.size > 16:
            f = font(MONO, f.size - 2)
        lh = int(f.size * 1.45)
        y = y0 + 90
        for i, l in enumerate(lines):
            if i in hl:
                d.rectangle((x0 + 20, y - 6, x1 - 20, y + lh - 10), fill=(70, 62, 30))
            color = (130, 220, 130) if l.startswith("$") else (HL if i in hl else TEXT)
            d.text((x0 + 40, y), l, font=f, fill=color)
            y += lh
    elif kind == "chat":
        # 会話の吹き出し。あなたは右、キャラは左。新しい発言が下に来て、入りきらない古い発言は上から消える
        _, head, msgs, hl = spec
        d.rounded_rectangle(SLIDE_BOX, 18, fill=(16, 17, 22))
        d.rounded_rectangle((x0, y0, x1, y0 + 56), 18, fill=PANEL)
        d.rectangle((x0, y0 + 36, x1, y0 + 56), fill=PANEL)
        d.text((x0 + 30, y0 + 28), head, font=font(JP, 26), fill=MUTED, anchor="lm")
        f, fn = font(JP, 36), font(JP_BOLD, 26)
        bw = (x1 - x0) * 0.72
        blocks = []
        for i, (who, text) in enumerate(msgs):
            lines = [l for para in text.split("\n") for l in (wrap(para, f, bw - 60) or [""])]
            blocks.append((i, who, lines, 40 + len(lines) * 52 + 30))
        y = y1 - 30
        for i, who, lines, h in reversed(blocks):
            if y - h < y0 + 80:
                # いちばん新しい発言が長すぎるときは、入るところまで出して「…」で切る
                if i != blocks[-1][0]:
                    break
                keep = max(1, int((y - (y0 + 80) - 70) // 52))
                lines = lines[:keep - 1] + [lines[keep - 1].rstrip() + "…"]
                h = 40 + len(lines) * 52 + 30
            me = who.startswith("あなた")
            bx0 = x1 - 40 - bw if me else x0 + 40
            fill = (40, 70, 110) if me else ((70, 62, 30) if i in hl else (40, 44, 56))
            d.rounded_rectangle((bx0, y - h, bx0 + bw, y - 10), 22, fill=fill,
                                outline=HL if i in hl else None, width=3)
            d.text((bx0 + 30, y - h + 14), who, font=fn, fill=MUTED)
            for j, l in enumerate(lines):
                draw_text_emoji(img, (bx0 + 30, y - h + 52 + j * 52), l, f, TEXT)
            y -= h + 14
    elif kind == "flow":
        # 横に並べた箱を矢印でつなぐ流れ図。箱は (名前, 説明の行…)。hl の箱を強調し、notes を下に並べる
        _, head, boxes, hl, notes = spec
        d.text((x0 + 40, y0 + 30), head, font=font(JP_BOLD, 48), fill=TEXT)
        n, gap = len(boxes), 70
        bw = (x1 - x0 - 80 - gap * (n - 1)) / n
        by0, by1 = y0 + 130, y0 + 130 + (300 if notes else 420)
        fn, fl = font(JP_BOLD, 36), font(JP, 28)
        for i, (name, *desc) in enumerate(boxes):
            bx = x0 + 40 + i * (bw + gap)
            on = i in hl
            d.rounded_rectangle((bx, by0, bx + bw, by1), 18, fill=(70, 62, 30) if on else (32, 35, 44),
                                outline=HL if on else MUTED, width=4 if on else 2)
            cf = fn
            while cf.getlength(name) > bw - 30 and cf.size > 20:
                cf = font(JP_BOLD, cf.size - 2)
            d.text((bx + bw / 2, by0 + 60), name, font=cf, fill=HL if on else TEXT, anchor="mm")
            for j, l in enumerate(desc):
                lf = fl
                while lf.getlength(l) > bw - 30 and lf.size > 18:
                    lf = font(JP, lf.size - 2)
                d.text((bx + bw / 2, by0 + 130 + j * 46), l, font=lf, fill=TEXT if j == 0 else MUTED, anchor="mm")
            if i < n - 1:
                ax, ay = bx + bw + 10, (by0 + by1) / 2
                d.line((ax, ay, ax + gap - 20, ay), fill=MUTED, width=5)
                d.polygon([(ax + gap - 20, ay - 14), (ax + gap - 4, ay), (ax + gap - 20, ay + 14)], fill=MUTED)
        y = by1 + 50
        for label, text, strong in notes:
            d.text((x0 + 60, y), label, font=font(JP_BOLD, 30), fill=HL if strong else MUTED)
            tf = font(JP_BOLD if strong else JP, 34)
            while tf.getlength(text) > x1 - x0 - 340 and tf.size > 18:
                tf = font(JP_BOLD if strong else JP, tf.size - 2)
            d.text((x0 + 280, y - 2), text, font=tf, fill=TEXT)
            y += 70
    elif kind == "table":
        _, head, header, rows, hl = spec
        d.text((x0 + 40, y0 + 40), head, font=font(JP_BOLD, 52), fill=TEXT)
        f, fb = font(JP, 36), font(JP_BOLD, 36)
        cols = len(header)
        widths = [max(fb.getlength(header[c]), *(f.getlength(r[c]) for r in rows)) + 60 for c in range(cols)]
        scale = min(1.0, (x1 - x0 - 80) / sum(widths))
        widths = [w * scale for w in widths]
        y = y0 + 150
        rh = min(80, int((y1 - y0 - 250) / (len(rows) + 1)))  # 行が多い表は詰めて、下の角のキャラにかぶらないようにする
        if rh < 80:
            f, fb = font(JP, int(36 * rh / 80) + 4), font(JP_BOLD, int(36 * rh / 80) + 4)
        tx = x0 + (x1 - x0 - sum(widths)) / 2  # 表は画面の中央に置く
        for ri, row in enumerate([header] + rows):
            x = tx
            fill = PANEL if ri == 0 else ((70, 62, 30) if ri - 1 in hl else (32, 35, 44))
            d.rectangle((x, y, x + sum(widths), y + rh - 6), fill=fill)
            for c, cell in enumerate(row):
                cf = fb if ri == 0 else f
                while cf.getlength(cell) > widths[c] - 30 and cf.size > 18:
                    cf = font(JP_BOLD if ri == 0 else JP, cf.size - 2)
                d.text((x + 24, y + rh / 2 - 3), cell, font=cf,
                       fill=HL if ri - 1 in hl else TEXT, anchor="lm")
                x += widths[c]
            y += rh


def load_annotations():
    """dict_common.tsv とその回の dict.tsv で annotate=yes の用語 → 読み。"""
    out = {}
    for name in (os.path.join(ROOT, "voice", "dict_common.tsv"), episode.path("dict.tsv")):
        with open(name, newline="") as f:
            out.update({r["surface"]: r["reading"] for r in csv.DictReader(f, delimiter="\t")
                        if r.get("annotate") == "yes"})
    return out


def annotate(lines):
    """用語が動画の中で最初に出てきた行だけ、字幕に「VRAM（ブイラム）」と読みを添える。"""
    terms = sorted(load_annotations().items(), key=lambda kv: -len(kv[0]))
    seen = set()
    for ln in lines:
        text, i, out = ln["text"], 0, ""
        while i < len(text):
            for term, reading in terms:
                if text.startswith(term, i):
                    out += term + ("" if (ANNOTATE_ONCE and term in seen) else f"（{reading}）")
                    seen.add(term)
                    i += len(term)
                    break
            else:
                out += text[i]
                i += 1
        ln["subtitle"] = out


def draw_subtitle(img, speaker, text):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = SUB_BOX
    d.rounded_rectangle(SUB_BOX, 20, fill=(12, 13, 17))
    d.rounded_rectangle((x0, y0, x0 + 12, y1), 6, fill=COLOR[speaker])
    d.text((x0 + 40, y0 + 18), speaker, font=font(JP_BOLD, 30), fill=COLOR[speaker])
    # 2 行に収まらなければ文字を小さくする（字幕枠の高さは 3 行分まで）
    for size in (42, 34, 28):
        f = font(JP_BOLD, size)
        lines = wrap(text, f, x1 - x0 - 80)
        if len(lines) <= (2 if size == 42 else 3):
            break
    for i, l in enumerate(lines[:4]):
        d.text((x0 + 40, y0 + 62 + i * int(f.size * 1.3)), l, font=f, fill=TEXT)


# ---------- 口パク ----------

OPEN_WIDE = set("ao")
OPEN_HALF = set("iueN")


def mouth_track(query, start):
    """audio_query のモーラの長さから、(開始秒, 終了秒, 口の開き 0-2) の列を作る。"""
    sp = query.get("speedScale", 1.0)
    t = start + query.get("prePhonemeLength", 0.1) / sp
    track = []
    for ap in query["accent_phrases"]:
        moras = ap["moras"] + ([ap["pause_mora"]] if ap.get("pause_mora") else [])
        for m in moras:
            c = (m.get("consonant_length") or 0) / sp
            v = (m.get("vowel_length") or 0) / sp
            vowel = m.get("vowel", "pau")
            if c:
                track.append((t, t + c, 0 if m.get("consonant") in ("m", "b", "p") else 1))
                t += c
            level = 2 if vowel in OPEN_WIDE else 1 if vowel in OPEN_HALF else 0
            track.append((t, t + v, level))
            t += v
    return track


def is_sd_react(react):
    """react が SD 絵の名前か。Live2D の回でも、オチの場面だけ SD 絵に切り替えられる（漫画で急に絵が崩れるように）。"""
    return bool(react) and "+" not in react and os.path.exists(os.path.join(SD_DIR, react + ".png"))


def check_live2d_react(no, speaker, react):
    """Live2D の回の react が、SD 絵か、モデルにある表情・モーションの名前か確かめる。"""
    if is_sd_react(react):
        return
    import live2d_frames
    exps, motions = live2d_frames.model_vocab(L2D_SLUG[speaker])
    names = react.split("+")
    bad = [n for n in names if n not in exps | motions]
    if not bad and (sum(n in exps for n in names) > 1 or sum(n in motions for n in names) > 1):
        raise SystemExit(f"{no} 行（{speaker}）の react {react}：表情とモーションは 1 つずつまでです")
    if bad:
        raise SystemExit(f"{no} 行（{speaker}）の react {'+'.join(bad)} は Live2D モデルにありません。\n"
                         f"表情: {' '.join(sorted(exps))}\nモーション: {' '.join(sorted(motions))}\n"
                         f"SD 絵（{SD_DIR}）の名前なら、その行だけ SD 絵になります")


class Live2DStream:
    """video/live2d_frames.py を立ち上げ、めたんとずんだもんの絵を 1 コマずつ受け取る。"""

    def __init__(self, lines, start, count):
        if not os.path.exists(LIVE2D_PY):
            raise SystemExit("第7弾からは Live2D を使います。README の「Live2D」の手順で .venv-live2d を作ってください")
        plan = {"fps": FPS, "start": start, "count": count, "lines": [
            {"slug": L2D_SLUG[l["speaker"]], "start": l["start"], "end": l["end"],
             "wav": os.path.join(VOICE, f"{l['no']:03d}_{L2D_SLUG[l['speaker']]}.wav"),
             "react": l["react"].split("+") if l["react"] and not is_sd_react(l["react"]) else []}
            for l in lines if l["speaker"] in L2D_SLUG]}
        self.plan = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(plan, self.plan)
        self.plan.close()
        self.proc = subprocess.Popen([LIVE2D_PY, os.path.join(ROOT, "video", "live2d_frames.py"), self.plan.name],
                                     stdout=subprocess.PIPE)
        sizes = json.loads(self.proc.stdout.readline())
        self.sizes = [(name, tuple(sizes[slug])) for name, slug in L2D_SLUG.items()]

    def next(self):
        frame = {}
        for name, (w, h) in self.sizes:
            buf = self.proc.stdout.read(w * h * 4)
            if len(buf) != w * h * 4:
                raise SystemExit("Live2D の絵が途中で切れました（live2d_frames.py のエラーを見てください）")
            frame[name] = Image.frombytes("RGBA", (w, h), buf)
        return frame

    def close(self):
        self.proc.stdout.close()
        self.proc.wait()
        os.unlink(self.plan.name)


def dimmed(im):
    """しゃべっていないキャラを暗くする。"""
    dark = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dark.paste((0, 0, 0, 90), (0, 0), im)
    out = im.copy()
    out.alpha_composite(dark)
    return out


def load_chars():
    chars = {}
    for name, slug in ({} if LIVE2D else SLUG).items():
        frames = [bust(Image.open(os.path.join(CHARS, f"{slug}_{i}.png")).convert("RGBA"), slug) for i in range(3)]
        dim = []
        for fr in frames:
            dark = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            dark.paste((0, 0, 0, 90), (0, 0), fr)
            f2 = fr.copy()
            f2.alpha_composite(dark)
            dim.append(f2)
        chars[name] = (frames, dim)
    if episode.NAME == "ep04" or TSUMUGI_REGULAR:
        # 第4弾は乱入用に大きく、中央でタイトルに重ねる。第5弾は本編にいるので小さく、字幕の箱の上に立たせる
        for mood in ("angry", "happy"):
            source = os.path.join(ROOT, "assets", "official", f"tsumugi-sd-{mood}.png")
            portrait = Image.open(source).convert("RGBA")
            portrait = portrait.crop(portrait.getbbox())
            height = 600 if episode.NAME == "ep04" else 240
            im = portrait.resize((round(portrait.width * height / portrait.height), height), Image.LANCZOS)
            chars[f"つむぎ-{mood}"] = im
            dark = Image.new("RGBA", im.size, (0, 0, 0, 0))
            dark.paste((0, 0, 0, 90), (0, 0), im)
            dimmed = im.copy()
            dimmed.alpha_composite(dark)
            chars[f"つむぎ-{mood}-dim"] = dimmed
    return chars


def char_pos(name, im):
    """左右の列の中央に、足元をそろえて置く。"""
    x = (SIDE - im.width) // 2
    return (x if name == "めたん" else W - SIDE + x, H - im.height)  # 胸で画面の下端に切れる


def motion_offset(kind, dt):
    """行の頭から dt 秒後の、キャラの位置のずれ (dx, dy)。"""
    if kind == "jump" and dt < 0.4:
        return 0, -int(28 * math.sin(math.pi * dt / 0.4))
    if kind == "shake" and dt < 0.5:
        return int(10 * math.sin(dt * 70) * (1 - dt / 0.5)), 0
    return 0, 0


# ---------- 本体 ----------

def load_lines():
    with open(os.path.join(VOICE, "timeline.tsv"), newline="") as f:
        tl = list(csv.DictReader(f, delimiter="\t"))
    with open(episode.path("screens.tsv"), newline="") as f:
        sections = {r["no"]: r["section"] for r in csv.DictReader(f, delimiter="\t")}
    with open(episode.path("direction.tsv"), newline="") as f:
        direction = {r["no"]: r for r in csv.DictReader(f, delimiter="\t")}
    reacts = {no: d.get("react", "") for no, d in direction.items()}
    lines, spec, slide_start = [], SLIDES[1], 0.0
    mood = "happy"  # 第5弾のつむぎの表情。つむぎの行の react（angry / happy）で変わり、次に変わるまで続く
    for r in tl:
        no = int(r["no"])
        if no in SLIDES:
            spec = SLIDES[no]
            slide_start = float(r["start"])
        with open(os.path.join(VOICE, f"{no:03d}_{VOICE_SLUG[r['speaker']]}.json")) as f:
            q = json.load(f)
        if r["speaker"] == "つむぎ" and reacts.get(r["no"]) in ("angry", "happy"):
            mood = reacts[r["no"]]
        if LIVE2D and r["speaker"] in L2D_SLUG and reacts.get(r["no"]):
            check_live2d_react(no, r["speaker"], reacts[r["no"]])
        lines.append({
            "no": no, "speaker": r["speaker"], "text": r["text"],
            "start": float(r["start"]), "end": float(r["end"]),
            "section": sections.get(r["no"], ""), "spec": spec, "slide_start": slide_start,
            "notes": [text for s, (text, n) in sorted(NOTES.items()) if s <= no < s + n],
            "motion": r.get("motion", ""),
            "react": reacts.get(r["no"], ""),
            "tsumugi": mood,
            # 歌の行と、番外編のお囃子の行（sound 列）は、BGM を絞る
            "sing": bool(direction.get(r["no"], {}).get("sing") or direction.get(r["no"], {}).get("sound")),
            "track": mouth_track(q, float(r["start"])),
        })
    annotate(lines)
    return lines


_background = None


def background():
    """背景の 1 枚を作る。画像があれば画面いっぱいに切り出し、ぼかして暗くする。"""
    global _background
    if _background is None:
        if BG_IMAGE:
            from PIL import ImageFilter, ImageEnhance
            im = Image.open(BG_IMAGE).convert("RGB")
            r = max(W / im.width, H / im.height)
            im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
            im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
            im = im.filter(ImageFilter.GaussianBlur(BG_BLUR))
            im = ImageEnhance.Brightness(im).enhance(BG_DARK)
            # 画面と字幕の下に半透明の板を敷いて、文字を読みやすくする
            panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(panel)
            x0, y0, x1, y1 = SLIDE_BOX
            d.rounded_rectangle((x0 - 20, y0 - 50, x1 + 20, y1 + 16), 28, fill=BG + (150,))
            im = im.convert("RGBA")
            im.alpha_composite(panel)
            _background = im.convert("RGB")
        else:
            _background = Image.new("RGB", (W, H), BG)
    return _background


def media_seconds(path):
    """音や動画のファイルの長さ（秒）。"""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def base_frame(line, t=None):
    img = background().copy()
    draw_slide(img, line["spec"], line["section"], 0 if t is None else t - line["slide_start"])
    draw_notes(img, line.get("notes", []))
    draw_subtitle(img, line["speaker"], line["subtitle"])
    return img


def draw_notes(img, notes):
    """補足（※）を、画面の下のほう、左右のキャラのあいだに小さく出す。新しいものほど下。"""
    if not notes:
        return
    d = ImageDraw.Draw(img)
    f = font(JP, 28)
    x0, x1 = SIDE + 20, W - SIDE - 20
    rows = [l for n in notes for l in wrap(n, f, x1 - x0)]
    y = SLIDE_BOX[3] - 24 - 40 * len(rows)
    for i, l in enumerate(rows):
        d.text((x0, y + 40 * i), l, font=f, fill=(206, 210, 222))


def section_card(section):
    """セクションの変わり目に出す見出し。"""
    img = background().copy()
    d = ImageDraw.Draw(img)
    num, _, title = section.partition(". ")
    cx, cy = W / 2, (SLIDE_BOX[1] + SLIDE_BOX[3]) / 2
    d.text((cx, cy - 70), f"Part {num}", font=font(JP_BOLD, 40), fill=HL, anchor="mm")
    f = fit_font([title], JP_BOLD, 72, SLIDE_BOX[2] - SLIDE_BOX[0])
    d.text((cx, cy + 20), title, font=f, fill=TEXT, anchor="mm")
    d.line((cx - 120, cy + 90, cx + 120, cy + 90), fill=HL, width=4)
    return img


def speaker_state(line, t):
    """話している側の見た目を決める値（口の開き、位置のずれ、拡大率）。同じなら同じ絵になる。"""
    dt = t - line["start"]
    level = 0
    for s0, e0, lv in line["track"]:
        if s0 <= t < e0:
            level = lv
            break
    dx, dy, scale = 0, 0, 1.0
    if line.get("react"):
        # リアクションの行は、出るときに弾ませ（0.85 → 1.1 → 1.0）、声に合わせて少し跳ねさせる。
        # SD 絵は口パクがないのでその代わり。Live2D でも表情が変わるのに合わせて弾ませる
        dy = -4 * level
        if dt < 0.12:
            scale = 0.85 + 0.25 * dt / 0.12   # 0.85 → 1.1
        elif dt < 0.24:
            scale = 1.1 - 0.1 * (dt - 0.12) / 0.12
    elif LIVE2D:
        dy = -3 * level   # Live2D はふだんの行も、声に合わせて少し跳ねさせる
    mx, my = motion_offset(line["motion"], dt)
    return level, dx + mx, dy + my, round(scale, 3)


def frame_at(base, line, t, chars, talking=True, state=None, l2d=None):
    img = base.copy()
    for name in ("めたん", "ずんだもん"):
        if l2d:
            # Live2D：表情と口は live2d_frames.py が動かしている。ここでは位置のずれと暗くするだけ
            im = l2d[name]
            dx = dy = 0
            if talking and name == line["speaker"]:
                _, dx, dy, scale = state or speaker_state(line, t)
                if is_sd_react(line["react"]):
                    im = sd_image(line["react"])
                if scale != 1.0:
                    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
            elif talking:
                im = dimmed(im)
            x, y = char_pos(name, im)
            img.paste(im, (x + dx, y + dy), im)
            continue
        frames, dim = chars[name]
        dx, dy, scale = 0, 0, 1.0
        if talking and name == line["speaker"]:
            level, dx, dy, scale = state or speaker_state(line, t)
            im = sd_image(line["react"]) if line.get("react") else frames[level]
        else:
            im = frames[0] if not talking else dim[0]
        if scale != 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
        x, y = char_pos(name, im)
        img.paste(im, (x + dx, y + dy), im)
    # 第4弾のつむぎは二人の間へ割り込み、タイトルを隠す。
    # 79行は締めの直後に出すので、次の章の見出しで予告しない。
    if episode.NAME == "ep04" and (3 <= line["no"] <= 8 or 79 <= line["no"] <= 83):
        angry = line["no"] in (3, 4, 5, 6, 7, 79, 80, 81, 82)
        im = chars["つむぎ-angry" if angry else "つむぎ-happy"]
        dy = motion_offset(line["motion"], t - line["start"])[1] if line["speaker"] == "つむぎ" else 0
        img.paste(im, ((W - im.width) // 2, 805 - im.height + dy), im)
    # 第5弾からのつむぎは最初から本編にいる。字幕の右の空き（ずんだもんの隣）に立ち、しゃべっていないときは二人と同じく暗くする
    if TSUMUGI_REGULAR and l2d:
        # 第7弾と番外編から：つむぎも Live2D。表情と口は live2d_frames.py が動かす。しゃべるときは 2 人と同じく弾む
        im = l2d["つむぎ"]
        dy = 0
        if talking and line["speaker"] == "つむぎ":
            _, _, dy, scale = state or speaker_state(line, t)
            if scale != 1.0:
                im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
        elif talking:
            im = dimmed(im)
        img.paste(im, (SUB_BOX[2] + (TSUMUGI_W - im.width) // 2, H - im.height + dy), im)  # 2 人と同じく画面の下で切れる
    elif TSUMUGI_REGULAR:
        speaking = talking and line["speaker"] == "つむぎ"
        im = chars[f"つむぎ-{line['tsumugi']}" + ("" if speaking or not talking else "-dim")]
        dy = motion_offset(line["motion"], t - line["start"])[1] if speaking else 0
        if LIVE2D:
            # 第7弾から：2 人が Live2D で動くので、つむぎの SD 絵も止まって見えないようにする。
            # いつもゆっくり上下（呼吸、3.2 秒で 1 往復）し、しゃべるときは 2 人と同じく弾んで跳ねる
            if speaking:
                _, _, dy, scale = state or speaker_state(line, t)
                if scale != 1.0:
                    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BILINEAR)
            dy += round(3 * math.sin(2 * math.pi * t / 3.2))
        img.paste(im, (SUB_BOX[2] + (TSUMUGI_W - im.width) // 2, H - 8 - im.height + dy), im)
    return img


SD_DIR = os.path.join(ROOT, "assets", "official", "sd")
BUST_H = 387       # 画面でのバストショットの高さ（px）
# キャラごとの大きさの倍率。めたんは髪が大きく顔も大きく見えるので、ずんだもんと顔の大きさをそろえる
CHAR_SCALE = {"met": 0.75, "zun": 1.0}
# SD 絵ごとの切り出す下端（絵の上からの割合）。あごの少し下、胸のあたりで切る。
# ポーズで顔の高さが違うので絵ごとに決める（しゃがんだ絵は顔が下にあるので大きめ）
BUST_BOTTOM = {
    "metan": 0.58, "met_s214": 0.62, "met_s215": 0.72, "met_s218": 0.66, "met_s221": 0.63, "met_s222": 0.63,
    "zundamon": 0.66, "zunmon_3009": 0.82, "zunmon_3013": 0.75, "zunmon_3015": 0.7, "zunmon_3016": 0.76,
    "zunmon_3017": 0.80, "zunmon_3019": 0.74, "zunmon_3020": 0.78, "zunmon_3021": 0.68, "zunmon_3022": 0.76,
    "zunmon_3030": 0.9,
}
# 表情違いの絵ごとの拡大率。絵によって顔の大きさが違うので、ふだんの絵（metan）と顔の幅がそろうようにする。
# 横にはみ出す分は切る（見切れてよい）
FACE_SCALE = {"met_s214": 0.85, "met_s215": 1.29, "met_s218": 0.9, "met_s221": 0.85, "met_s222": 0.9}
_sd = {}


def bust(im, key):
    """SD 絵の頭から胸までを切り出し、高さを BUST_H にそろえる。横にはみ出す分は中央で切る。"""
    im = im.crop(im.getbbox())
    im = im.crop((0, 0, im.width, round(im.height * BUST_BOTTOM.get(key, 0.62))))
    h = round(BUST_H * CHAR_SCALE[key[:3]])
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    if key in FACE_SCALE:
        f = FACE_SCALE[key]
        im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    max_w = SIDE - 16
    if im.width > max_w:
        left = (im.width - max_w) // 2
        im = im.crop((left, 0, left + max_w, im.height))
    return im


def sd_image(name):
    """リアクション用の SD 絵（バストショット）。"""
    if name not in _sd:
        _sd[name] = bust(Image.open(os.path.join(SD_DIR, name + ".png")).convert("RGBA"), name)
    return _sd[name]


def write_description(lines):
    chapters, seen, prev = [], set(), None
    for ln in lines:
        sec = ln["section"]
        if sec and sec not in seen:
            seen.add(sec)
            # セクションの見出しが出る瞬間（前の行が終わったところ）をチャプターの頭にする
            t = 0 if not chapters else int(prev["end"] + 0.2)
            title = sec.split(". ", 1)[-1]
            chapters.append(f"{t // 60}:{t % 60:02d} {title}")
        prev = ln
    text = META.description(chapters)
    with open(os.path.join(OUT, "description.txt"), "w") as f:
        f.write(text + "\n")
    return text


def write_srt(lines):
    """YouTube にアップロードする字幕ファイル（SRT）を書き出す。"""
    def ts(t):
        ms = round(t * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    path = os.path.join(OUT, "subtitles.srt")
    with open(path, "w") as f:
        for i, ln in enumerate(lines, 1):
            f.write(f"{i}\n{ts(ln['start'])} --> {ts(ln['end'])}\n{ln['speaker']}：{ln['text']}\n\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=float, help="先頭から指定秒だけ作る")
    ap.add_argument("--start", type=float, default=0.0, help="--preview と一緒に：この秒から作る（例 --start 1000 --preview 41 で最後だけ）")
    ap.add_argument("--still", type=int, help="指定行の 1 コマを PNG で保存")
    ap.add_argument("--description", action="store_true", help="概要欄の文面だけ書き出す")
    ap.add_argument("--srt", action="store_true", help="字幕ファイル（SRT）だけ書き出す")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    lines = load_lines()
    chars = load_chars()

    if args.srt:
        print(write_srt(lines))
        return

    if args.description:
        print(write_description(lines))
        return

    if args.still:
        ln = next(l for l in lines if l["no"] == args.still)
        t = ln["start"] + (ln["end"] - ln["start"]) / 3
        l2d = None
        if LIVE2D:
            stream = Live2DStream(lines, round(t * FPS), 1)
            l2d = stream.next()
            stream.close()
        frame_at(base_frame(ln, t), ln, t, chars, l2d=l2d).save(os.path.join(OUT, f"still_{args.still:03d}.png"))
        return

    print(write_description(lines))
    audio = os.path.join(VOICE, "all.wav")
    total = lines[-1]["end"] + 1.0
    start = args.start if args.preview else 0.0  # 途中から作るのはプレビューだけ
    if args.preview:
        total = min(total, start + args.preview)
    n_frames = math.ceil(total * FPS)
    first = round(start * FPS)
    name = "preview.mp4" if args.preview else "video.mp4"
    # BGM はセリフの間だけ音量を下げる（sidechaincompress）。最初と最後はフェード
    # 歌の行（direction.tsv の sing 列）のあいだは、1 秒かけて BGM を 15% まで絞り、歌のあとに戻す
    # 途中から作るときは、音を start 秒から読むので、時刻は start を引いた値で書く
    sing_duck = "*".join(f"(1-{1 - SING_BGM:.2f}*clip((t-{l['start'] - 1 - start:.2f}),0,1)*clip(({l['end'] + 1 - start:.2f}-t),0,1))"
                         for l in lines if l["sing"]) or "1"
    afilter = (
        "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit[voice][key];"
        f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,{BGM_FILTER + ',' if BGM_FILTER else ''}volume={BGM_VOLUME},volume='{sing_duck}':eval=frame,"
        f"afade=t=in:d=2,afade=t=out:st={max(0, total - start - 4):.2f}:d=4[bgm];"
        "[bgm][key]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=700[duck];"
        "[voice][duck]amix=inputs=2:normalize=0:duration=longest[a]"
    )
    cmd = ["ffmpeg", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-ss", f"{start:.3f}", "-i", audio, "-stream_loop", "-1", "-ss", f"{start % media_seconds(BGM):.3f}", "-i", BGM,
           "-filter_complex", afilter, "-map", "0:v", "-map", "[a]", "-t", f"{total - start:.3f}",
           *VIDEO_CODEC, "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", os.path.join(OUT, name)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    stream = Live2DStream(lines, first, n_frames - first) if LIVE2D else None

    li, base, card, card_for = 0, None, None, None
    prev_key, prev_bytes = None, None
    for i in range(first, n_frames):
        t = i / FPS
        l2d = stream.next() if stream else None
        # 次の行の開始時刻を過ぎたら行を進める（行間の無音は前の行の画面のまま）
        while li + 1 < len(lines) and t >= lines[li + 1]["start"]:
            li += 1
            base = None
        if base is None or lines[li]["spec"][0] == "screencam":
            base = base_frame(lines[li], t)
        nxt = lines[li + 1] if li + 1 < len(lines) else None
        # 次の行で新しいセクションが始まり、間が 1 秒以上あるなら、間のあいだ見出しを出す
        if (nxt and nxt["section"] != lines[li]["section"] and t >= lines[li]["end"] + 0.2
                and nxt["start"] - lines[li]["end"] >= 1.0):
            if card_for != nxt["section"]:
                card, card_for = section_card(nxt["section"]), nxt["section"]
                next_base = base_frame(nxt)
            # 前の章の画面 → 見出し → 次の章の画面を、FADE 秒ずつフェードでつなぐ
            c0, c1 = lines[li]["end"] + 0.2, nxt["start"]
            if t < c0 + FADE:
                a = round((t - c0) / FADE, 2)
                bg = Image.blend(base, card, a)
            elif t > c1 - FADE:
                a = round((c1 - t) / FADE, 2)
                bg = Image.blend(next_base, card, max(0.0, a))
            else:
                a, bg = 1.0, card
            key = ("card", card_for, a, t > c1 - FADE, i if stream else 0)
            if key != prev_key:
                prev_bytes = frame_at(bg, lines[li], t, chars, talking=False, l2d=l2d).tobytes()
        else:
            state = speaker_state(lines[li], t)
            # Live2D の回は、呼吸やまばたきで毎コマ絵が変わるので使い回さない
            key = (li, state, i if lines[li]["spec"][0] == "screencam" or stream else 0)
            # 口の開き・位置・拡大率が前のコマと同じなら、組み立て直さずに使い回す
            if key != prev_key:
                prev_bytes = frame_at(base, lines[li], t, chars, state=state, l2d=l2d).tobytes()
        prev_key = key
        ff.stdin.write(prev_bytes)
        if i % (FPS * 30) == 0:
            print(f"{t:6.0f} / {total:.0f} 秒", file=sys.stderr)
    ff.stdin.close()
    if stream:
        stream.close()
    ff.wait()
    print(os.path.join(OUT, name), file=sys.stderr)


if __name__ == "__main__":
    main()
