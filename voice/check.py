#!/usr/bin/env python3
"""合成した声を whisper-server で文字起こしし、台本とずれている行を一覧にする。

耳が VOICEVOX の読み方に慣れてしまうと、「Qwen 3」が「クエン酸」に聞こえるような
読み間違いに気づきにくい。初めて聞く人の代わりに Whisper に聞かせて、台本と比べる。

  python3 voice/check.py            # 似ている度合いが低い行から 20 行を表示
  python3 voice/check.py --all      # 全行を表示
  python3 voice/check.py --only 33  # 指定した行だけ

whisper-server（既定 http://127.0.0.1:8082/inference、WHISPER_URL で変える）と ffmpeg が必要。
英単語をカタカナで書き取るなど、読み間違いでなくてもずれは出るので、上から耳で確かめる。
"""
import argparse
import csv
import difflib
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import episode  # noqa: E402

WHISPER = os.environ.get("WHISPER_URL", "http://127.0.0.1:8082/inference")


def normalize(text):
    """空白・句読点・記号を除き、全角英数を半角にそろえて比べやすくする。"""
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\s、。，．,.!?！？「」『』（）()…・:：;；\"'“”‘’〜~\-_/]", "", text)


def transcribe(wav):
    """16kHz モノラルに変換して whisper-server に送る。"""
    with tempfile.TemporaryDirectory() as tmp:
        mono = os.path.join(tmp, "in.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ar", "16000", "-ac", "1", mono], check=True)
        boundary = uuid.uuid4().hex
        with open(mono, "rb") as f:
            audio = f.read()
        parts = []
        for name, value in (("language", "ja"), ("response_format", "text"), ("temperature", "0")):
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"in.wav\"\r\n"
                     "Content-Type: audio/wav\r\n\r\n".encode() + audio + b"\r\n")
        body = b"".join(parts) + f"--{boundary}--\r\n".encode()
        req = urllib.request.Request(WHISPER, data=body, method="POST",
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=120) as res:
            return res.read().decode().strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="全行を表示する")
    ap.add_argument("--top", type=int, default=20, help="表示する行数（既定 20）")
    ap.add_argument("--only", help="調べる行番号（カンマ区切り）")
    args = ap.parse_args()
    only = {int(n) for n in args.only.split(",")} if args.only else None

    with open(os.path.join(episode.VOICE_OUT, "timeline.tsv"), newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    slug = {"めたん": "metan", "ずんだもん": "zundamon", "パソコンのめたん": "pc_metan", "パソコンのずんだもん": "pc_zundamon", "ひまり": "himari"}
    results = []
    for r in rows:
        no = int(r["no"])
        if only is not None and no not in only:
            continue
        heard = transcribe(os.path.join(episode.VOICE_OUT, f"{no:03d}_{slug[r['speaker']]}.wav"))
        ratio = difflib.SequenceMatcher(None, normalize(r["text"]), normalize(heard)).ratio()
        results.append((ratio, no, r["text"], heard))
        print(f"\r{len(results)} 行", end="", file=sys.stderr)
    print(file=sys.stderr)

    results.sort()
    shown = results if (args.all or only) else results[:args.top]
    for ratio, no, text, heard in shown:
        print(f"{no:>3}  {ratio:.2f}\n     台本: {text}\n     聞こえ: {heard}")


if __name__ == "__main__":
    main()
