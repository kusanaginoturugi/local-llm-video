#!/usr/bin/env python3
"""コマンドを仮想の端末で動かし、指定した時点の画面を PNG にする（デスクトップに窓を開かない）。

  python3 termshot.py out.png --cols 120 --rows 36 --at 6 -- nvtop
  python3 termshot.py out.png --at 20 --type "こんにちは\\n" -- llama-cli -hf ...

必要なもの: pyte（pip install pyte）、Pillow、Cica フォント。
"""
import argparse
import os
import pty
import select
import signal
import subprocess
import time

import pyte
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/TTF/Cica-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/TTF/Cica-Bold.ttf"
BG = (24, 26, 33)
FG = (220, 223, 230)
# 端末の 16 色（暗い背景向け）
NAMED = {
    "black": (40, 42, 54), "red": (237, 106, 94), "green": (98, 197, 84), "brown": (245, 191, 79),
    "blue": (97, 175, 239), "magenta": (198, 120, 221), "cyan": (86, 182, 194), "white": (220, 223, 230),
    "brightblack": (110, 116, 135), "brightred": (255, 140, 130), "brightgreen": (140, 230, 120),
    "brightbrown": (255, 220, 120), "brightblue": (140, 200, 255), "brightmagenta": (230, 160, 240),
    "brightcyan": (130, 220, 230), "brightwhite": (255, 255, 255),
}


def color(c, default):
    if c == "default":
        return default
    if c in NAMED:
        return NAMED[c]
    if len(c) == 6:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return default


def capture(cmd, cols, rows, at, typed, env):
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)
    pid, fd = pty.fork()
    if pid == 0:
        os.environ.update(env)
        os.environ["TERM"] = "xterm-256color"
        os.environ["NCURSES_NO_UTF8_ACS"] = "1"  # 枠線を罫線の文字で出させる
        os.environ["COLUMNS"], os.environ["LINES"] = str(cols), str(rows)
        os.execvp(cmd[0], cmd)
    import fcntl, struct, termios
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    start, sent = time.time(), False
    while time.time() - start < at:
        if typed and not sent and time.time() - start > 1.0:
            os.write(fd, typed.encode())
            sent = True
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                stream.feed(os.read(fd, 65536))
            except OSError:
                break
    os.kill(pid, signal.SIGTERM)
    return screen


def render(screen, path, size=22, keep_rows=None, replace=()):
    f, fb = ImageFont.truetype(FONT, size), ImageFont.truetype(FONT_BOLD, size)
    cw, ch = round(f.getlength("M")), round(size * 1.25)
    lines = keep_rows or screen.lines
    img = Image.new("RGB", (screen.columns * cw + 32, lines * ch + 32), BG)
    d = ImageDraw.Draw(img)
    for y in range(lines):
        line = screen.buffer[y]
        # 写したくない文字（ユーザー名など）を同じ長さの別の文字に置き換える
        text = "".join(line[x].data or " " for x in range(screen.columns))
        for old, new in replace:
            i = text.find(old)
            while i >= 0:
                for k, chx in enumerate(new.ljust(len(old))[:len(old)]):
                    line[i + k] = line[i + k]._replace(data=chx)
                text = text[:i] + new.ljust(len(old)) + text[i + len(old):]
                i = text.find(old)
        for x in range(screen.columns):
            c = line[x]
            fg, bg = color(c.fg, FG), color(c.bg, BG)
            if c.reverse:
                fg, bg = bg, fg
            px, py = 16 + x * cw, 16 + y * ch
            if bg != BG:
                w = cw * (2 if c.data and ord(c.data[0]) > 0x2E80 else 1)
                d.rectangle((px, py, px + w, py + ch), fill=bg)
            if c.data.strip():
                d.text((px, py + 2), c.data, font=fb if c.bold else f, fill=fg)
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=120)
    ap.add_argument("--rows", type=int, default=34)
    ap.add_argument("--at", type=float, default=5, help="何秒後の画面を撮るか")
    ap.add_argument("--type", default="", help="1 秒後に打ち込む文字（\\n で Enter）")
    ap.add_argument("--env", action="append", default=[], help="KEY=VALUE")
    ap.add_argument("--keep-rows", type=int, help="上から何行だけ残すか")
    ap.add_argument("--replace", action="append", default=[], help="写したくない文字 OLD=NEW")
    import sys
    i = sys.argv.index("--")  # -- より後ろが動かすコマンド
    a, cmd = ap.parse_args(sys.argv[1:i]), sys.argv[i + 1:]
    env = dict(e.split("=", 1) for e in a.env)
    screen = capture(cmd, a.cols, a.rows, a.at, a.type.replace("\\n", "\n"), env)
    render(screen, a.out, keep_rows=a.keep_rows, replace=[r.split("=", 1) for r in a.replace])


if __name__ == "__main__":
    main()
