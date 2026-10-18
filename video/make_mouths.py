"""公式イラストから口パク用の差分（閉じ口・半開き・開き口）を作る。"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "official")
OUT = os.path.join(ROOT, "assets", "chars")
os.makedirs(OUT, exist_ok=True)


def open_mouth(im, cx, cy, w, h):
    """口の中（暗い赤）と舌（ピンク）を楕円で描く。"""
    im = im.copy()
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
              fill=(150, 50, 60, 255), outline=(110, 40, 45, 255), width=max(2, w // 18))
    tw, th = w * 0.55, h * 0.45
    d.ellipse([cx - tw / 2, cy + h / 2 - th - h * 0.08, cx + tw / 2, cy + h / 2 - h * 0.08],
              fill=(230, 120, 130, 255))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.2)))
    return im


def close_mouth(im, box, line):
    """口のあたりを周りの肌色で塗りつぶし、閉じ口の線を描く。"""
    im = im.copy()
    x0, y0, x1, y1 = box
    # 塗る色は口の少し下の肌から取る
    skin = im.crop((x0, y1 + 10, x1, y1 + 40)).convert("RGB").resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    im.paste(Image.new("RGBA", im.size, skin + (255,)), (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.line(line, fill=(170, 80, 80, 255), width=9, joint="curve")
    return im


BUST = 0.42      # 全身のうち、頭の上からこの割合までをバストショットにする
BUST_H = 560     # 動画内での高さ（px）
BUST_W = 420     # 動画内での幅（px）。顔を中心に切り出す


def save(im, name, bbox, face_x, bust=BUST):
    x0, y0, x1, y1 = bbox
    h = int((y1 - y0) * bust)
    w = h * BUST_W // BUST_H
    left = face_x - w // 2
    im = im.crop((left, y0, left + w, y0 + h))
    im = im.resize((BUST_W, BUST_H), Image.LANCZOS)
    im.save(os.path.join(OUT, name))


CHAR_H = 580  # 動画内での SD 絵の高さ（px）。render.py と合わせる


def save_sd(im, name):
    im = im.crop(im.getbbox())
    im = im.resize((round(im.width * CHAR_H / im.height), CHAR_H), Image.LANCZOS)
    im.save(os.path.join(OUT, name))


SD = os.path.join(SRC, "sd")

# めたん（SD・met_s209）: 元の絵は閉じ口。半開きと開き口を描き足す
met = Image.open(os.path.join(SD, "met_s209.png")).convert("RGBA")
save_sd(met, "metan_0.png")
save_sd(open_mouth(met, 3102, 3745, 150, 70), "metan_1.png")
save_sd(open_mouth(met, 3102, 3760, 180, 130), "metan_2.png")

# ずんだもん（SD・zunmon_3002）: 元の絵は開き口。閉じ口と半開きを作る
zun = Image.open(os.path.join(SD, "zunmon_3002.png")).convert("RGBA")
closed = close_mouth(zun, (3205, 3975, 3590, 4185), [(3290, 4070), (3395, 4105), (3500, 4070)])
save_sd(closed, "zundamon_0.png")
save_sd(open_mouth(closed, 3395, 4080, 220, 110), "zundamon_1.png")
save_sd(zun, "zundamon_2.png")

# 確認用に口元を並べた画像
row = []
for n, (fx, fy) in (("metan", (0.52, 0.41)), ("zundamon", (0.50, 0.53))):
    for i in range(3):
        im = Image.open(os.path.join(OUT, f"{n}_{i}.png"))
        w, h = im.size
        cx, cy = int(w * fx), int(h * fy)
        row.append(im.crop((cx - 80, cy - 60, cx + 80, cy + 60)).resize((240, 180), Image.LANCZOS))
sheet = Image.new("RGBA", (240 * 6, 180), (200, 200, 200, 255))
for i, c in enumerate(row):
    sheet.alpha_composite(c, (240 * i, 0))
sheet.save(os.path.join(OUT, "check_mouths.png"))
