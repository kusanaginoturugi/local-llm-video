#!/usr/bin/env python3
"""YouTube のサムネイル（1280x720）を作る。その回の out/video/thumbnail.png に保存する。

文言と色はその回の meta.py の THUMBNAIL で決める。

  THUMBNAIL = {
      "number": 3,                       # 第何弾か（左上の札に「#3」と出る）
      "color": (164, 222, 70),           # 背景の色（回ごとに変えて、一覧で見分けられるようにする）
      "title": "ずんだもんと",            # 1 行目
      "title2": "声で会話",               # 2 行目（いちばん大きく）
      "pill": ("返事まで", "0.2秒"),      # 下の黒い札（小さい言葉、黄色で大きく見せる言葉）
      "metan": "met_s214",               # 左下に置くめたんの SD 絵
      "zundamon": "zunmon_3022",         # 右下に置くずんだもんの SD 絵
  }

作りは「一色の背景に、大きな黒い文字と、黒い札が 1 つ」。小さい文字は一覧の大きさ（320x180）では読めないので入れない。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import episode  # noqa: E402

META = episode.module("meta")
THUMB = META.THUMBNAIL
OUT = os.path.join(episode.VIDEO_OUT, "thumbnail.png")
SD = os.path.join(ROOT, "assets", "official", "sd")
BLACK = "/usr/share/fonts/noto-cjk/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"
W, H = 1280, 720
INK = (17, 17, 17)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
CATCH = "ちょっといいゲーミング PC でできる"  # シリーズのキャッチフレーズ。毎回同じ位置・同じ形で右上に置く


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def fit(text, size, max_width):
    """横幅に収まるまで文字を小さくする。"""
    while font(BLACK, size).getlength(text) > max_width:
        size -= 4
    return font(BLACK, size)


def sd(name, height):
    im = Image.open(os.path.join(SD, name + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def badges(d):
    """左上にシリーズ名と回数、右上にキャッチフレーズ。どちらも黒い角丸の札に白い文字。"""
    d.rounded_rectangle((24, 22, 470, 74), 26, fill=INK)
    d.text((48, 48), "ローカル LLM で遊ぼう", font=font(BOLD, 30), fill=WHITE, anchor="lm")
    d.text((440, 48), f"#{THUMB['number']}", font=font(BLACK, 30), fill=WHITE, anchor="rm")
    f = font(BLACK, 26)
    w = f.getlength(CATCH)
    d.rounded_rectangle((W - 24 - w - 48, 22, W - 24, 74), 26, fill=INK)
    d.text((W - 24 - w / 2 - 24, 48), CATCH, font=f, fill=WHITE, anchor="mm")


def pill(img, small, big):
    """下の真ん中に、黒い角丸の札。小さい言葉は白、大きく見せる言葉は黄色。札の下に影を落とす。"""
    f1, f2 = font(BLACK, 44), font(BLACK, 92)
    gap = f1.getlength(" ")
    w = f1.getlength(small) + gap + f2.getlength(big)
    box = (W / 2 - w / 2 - 40, 500, W / 2 + w / 2 + 40, 640)
    shade = Image.new("RGBA", (W, H))
    ImageDraw.Draw(shade).rounded_rectangle(box, 30, fill=(0, 0, 0, 110))
    img.alpha_composite(shade.filter(ImageFilter.GaussianBlur(14)), (0, 10))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 30, fill=INK)
    d.text((box[0] + 40, 586), small, font=f1, fill=WHITE, anchor="ls")
    d.text((box[0] + 40 + f1.getlength(small) + gap, 600), big, font=f2, fill=YELLOW, anchor="ls")


def main():
    img = Image.new("RGBA", (W, H), tuple(THUMB["color"]) + (255,))
    d = ImageDraw.Draw(img)
    badges(d)
    # 見出し（2 行）。左右のキャラにかからない幅に収める
    d.text((W // 2, 185), THUMB["title"], font=fit(THUMB["title"], 116, 1000), fill=INK, anchor="mm")
    d.text((W // 2, 345), THUMB["title2"], font=fit(THUMB["title2"], 200, 1060), fill=INK, anchor="mm")
    pill(img, *THUMB["pill"])
    # キャラクター: 左下にめたん、右下にずんだもん
    metan = sd(THUMB["metan"], 300)
    zun = sd(THUMB["zundamon"], 290)
    img.alpha_composite(metan, (10, H - metan.height + 80))
    img.alpha_composite(zun, (W - zun.width - 20, H - zun.height + 20))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.convert("RGB").save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
