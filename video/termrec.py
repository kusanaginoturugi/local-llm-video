#!/usr/bin/env python3
"""コマンドを仮想の端末で動かして、出た文字と時刻を記録し、あとで動画にする（デスクトップに窓を開かない）。

  python3 termrec.py record rec.jsonl --show '$ ocr.py …' -- python3 ocr.py …
  python3 termrec.py render rec.jsonl out.mp4 --speed 4 --fps 30

record は、画面に出た文字をそのまま時刻つきで残す（最初に --show の行を、打ち込んだコマンドとして出す）。
render は、記録を時刻どおりに仮想の端末へ流し直して、1 コマずつ絵にする。--speed で早送りできる。
最後の画面は --hold 秒そのまま残す。必要なもの: pyte、Pillow、ffmpeg、PlemolJP Console フォント（AUR の ttf-plemoljp-bin）。
"""
import argparse
import base64
import json
import os
import pty
import select
import subprocess
import sys
import time

import pyte

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from termshot import render as draw  # noqa: E402


def record(path, cmd, cols, rows, show, cwd):
    pid, fd = pty.fork()
    if pid == 0:
        if cwd:
            os.chdir(cwd)
        os.environ["TERM"] = "xterm-256color"
        os.environ["COLUMNS"], os.environ["LINES"] = str(cols), str(rows)
        os.environ["PYTHONUNBUFFERED"] = "1"
        os.execvp(cmd[0], cmd)
    import fcntl
    import struct
    import termios
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    start = time.time()
    with open(path, "w") as out:
        # 記録をリポジトリに入れても困らないよう、ホームディレクトリは ~ に置き換えて残す
        home = os.path.expanduser("~")
        shown = [c.replace(home, "~") for c in cmd]
        out.write(json.dumps({"cols": cols, "rows": rows, "cmd": shown}, ensure_ascii=False) + "\n")
        if show:
            out.write(json.dumps([0.0, base64.b64encode(f"{show}\r\n".encode()).decode()]) + "\n")
        while True:
            r, _, _ = select.select([fd], [], [], 0.5)
            if not r:
                if os.waitpid(pid, os.WNOHANG)[0]:
                    break
                continue
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            out.write(json.dumps([round(time.time() - start, 3), base64.b64encode(data).decode()]) + "\n")
        out.write(json.dumps([round(time.time() - start, 3), ""]) + "\n")
    os.waitpid(pid, 0)
    print(f"{path}: {time.time() - start:.1f} 秒")


def render(path, out, speed, fps, hold, size, start_at, until):
    with open(path) as f:
        head = json.loads(f.readline())
        events = [json.loads(line) for line in f]
    screen = pyte.Screen(head["cols"], head["rows"])
    stream = pyte.ByteStream(screen)
    end = min(events[-1][0], until) if until else events[-1][0]
    first = draw(screen, None, size=size)
    w, h = first.size
    w, h = w + w % 2, h + h % 2
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                           "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    i, frame, last = 0, 0, None
    total = int((end - start_at) / speed * fps) + int(hold * fps)
    while frame <= total:
        t = start_at + min(frame / fps * speed, end - start_at)
        changed = False
        while i < len(events) and events[i][0] <= t:
            if events[i][1]:
                stream.feed(base64.b64decode(events[i][1]))
                changed = True
            i += 1
        if changed or last is None:
            img = draw(screen, None, size=size)
            if img.size != (w, h):
                pad = img.__class__.new("RGB", (w, h), img.getpixel((0, 0)))
                pad.paste(img, (0, 0))
                img = pad
            last = img.tobytes()
        ff.stdin.write(last)
        frame += 1
    ff.stdin.close()
    ff.wait()
    print(f"{out}: 記録 {end - start_at:.1f} 秒を {speed} 倍速で {total / fps:.1f} 秒")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("record")
    r.add_argument("rec")
    r.add_argument("--cols", type=int, default=100)
    r.add_argument("--rows", type=int, default=24)
    r.add_argument("--show", default="", help="最初に出す行（打ち込んだコマンドとして見せる）")
    r.add_argument("--cwd")
    v = sub.add_parser("render")
    v.add_argument("rec")
    v.add_argument("out")
    v.add_argument("--speed", type=float, default=1.0)
    v.add_argument("--fps", type=int, default=30)
    v.add_argument("--hold", type=float, default=2.0)
    v.add_argument("--size", type=int, default=22)
    v.add_argument("--start", type=float, default=0.0, help="記録の何秒目から")
    v.add_argument("--until", type=float, help="記録の何秒目まで")
    if sys.argv[1:2] == ["record"]:
        i = sys.argv.index("--")
        a, cmd = ap.parse_args(sys.argv[1:i]), sys.argv[i + 1:]
        record(a.rec, cmd, a.cols, a.rows, a.show, a.cwd)
    else:
        a = ap.parse_args()
        render(a.rec, a.out, a.speed, a.fps, a.hold, a.size, a.start, a.until)


if __name__ == "__main__":
    main()
