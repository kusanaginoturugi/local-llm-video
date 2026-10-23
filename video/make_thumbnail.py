#!/usr/bin/env python3
"""YouTube のサムネイル（1280x720）を作る。その回の out/video/thumbnail.png に保存する。

文言と SD 絵はその回の meta.py の THUMBNAIL で決める。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import episode  # noqa: E402

META = episode.module("meta")
THUMB = getattr(META, "THUMBNAIL", {})
OUT = os.path.join(episode.VIDEO_OUT, "thumbnail.png")
BG_IMAGE = os.path.join(ROOT, "assets", "bg", "rgb_desk.jpg")
SD = os.path.join(ROOT, "assets", "official", "sd")
BLACK = "/usr/share/fonts/noto-cjk/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"
W, H = 1280, 720
YELLOW = (255, 214, 64)
GREEN = (120, 220, 80)
PINK = (255, 110, 180)


def font(path, size):
    return ImageFont.truetype(path, size, index=0)


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    return im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))


def sd(name, height):
    im = Image.open(os.path.join(SD, name + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * height / im.height), height), Image.LANCZOS)


def outlined(d, xy, text, f, fill, stroke, width, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, stroke_width=width, stroke_fill=stroke, anchor=anchor)


CATCH = "ちょっといいゲーミング PC でできる"  # シリーズのキャッチフレーズ。毎回同じ位置・同じ形で右上に置く


def catch_badge(img):
    """右上にキャッチフレーズの札を置く（左上のシリーズ名の札と対になる）。"""
    d = ImageDraw.Draw(img)
    f = font(BLACK, 28)
    w = f.getlength(CATCH)
    x1 = W - 24
    d.rounded_rectangle((x1 - w - 44, 20, x1, 76), 14, fill=YELLOW, outline=(20, 20, 30), width=3)
    d.text((x1 - w / 2 - 22, 48), CATCH, font=f, fill=(20, 20, 30), anchor="mm")


def main():
    # その回の meta.py に thumbnail() があれば、その回専用の描き方を使う
    if hasattr(META, "thumbnail"):
        img = META.thumbnail({"W": W, "H": H, "font": font, "sd": sd, "cover": cover, "outlined": outlined,
                              "BG_IMAGE": BG_IMAGE, "BLACK": BLACK, "BOLD": BOLD})
        catch_badge(img)
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        img.convert("RGB").save(OUT)
        print(OUT)
        return
    # 背景: 動画と同じ写真を、少しだけぼかして暗くする
    bg = cover(Image.open(BG_IMAGE).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(4))
    bg = ImageEnhance.Brightness(bg).enhance(0.6).convert("RGBA")
    # 文字の下を少し暗くして読みやすくする
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((0, 150, W, 560), fill=(0, 0, 0, 120))
    bg.alpha_composite(shade)

    # キャラクター: 左にめたん、右にずんだもん（どちらも喜んでいる表情）
    metan = sd(THUMB["metan"], 470)
    zun = sd(THUMB["zundamon"], 520)
    bg.alpha_composite(metan, (-30, H - metan.height + 40))
    bg.alpha_composite(zun, (W - zun.width + 20, H - zun.height + 30))

    d = ImageDraw.Draw(bg)
    # 上のシリーズ名と回数
    outlined(d, (W // 2, 70), "ローカル LLM で遊ぼう", font(BOLD, 54), (255, 255, 255), (20, 20, 30), 6)
    d.rounded_rectangle((W // 2 - 90, 112, W // 2 + 90, 160), 12, fill=PINK)
    d.text((W // 2, 136), THUMB["badge"], font=font(BLACK, 34), fill=(255, 255, 255), anchor="mm")
    # メインのタイトル（2 行）
    outlined(d, (W // 2, 270), THUMB["title"], font(BLACK, 128), YELLOW, (20, 20, 30), 12)
    outlined(d, (W // 2, 420), THUMB["title2"], font(BLACK, 100), (255, 255, 255), (20, 20, 30), 12)
    # 下の補足
    outlined(d, (W // 2, 525), THUMB["sub"], font(BOLD, 40), GREEN, (20, 20, 30), 6)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bg.convert("RGB").save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
