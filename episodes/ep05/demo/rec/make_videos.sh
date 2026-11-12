#!/bin/sh
# 第5弾の実録を動画にする。
#   bunko-{cuda,cpu}.jsonl：video/termrec.py record で取った ocr.py の実行の記録（自炊本 356 ページ）
#   firefox-search.mkv：record_firefox.sh で撮った Firefox の検索
# 出力：bunko-cpu-vs-gpu-x5.mp4（左右に並べて 5 倍速）、firefox-search-cut.mp4（先頭 12.5 秒）
set -eu
cd "$(dirname "$0")"
PY=../.venv/bin/python
TERMREC=../../../../video/termrec.py
F=/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc
$PY $TERMREC render bunko-cuda.jsonl bunko-cuda-x5.mp4 --speed 5 --hold 20
$PY $TERMREC render bunko-cpu.jsonl bunko-cpu-x5.mp4 --speed 5 --until 165 --hold 0
# zsh で書くときは ${F} と書く（$F:textfile の :t が修飾子になる）
ffmpeg -loglevel error -y -i bunko-cpu-x5.mp4 -i bunko-cuda-x5.mp4 -filter_complex \
  "[0:v]pad=iw:ih+70:0:70:color=0x181a21,drawtext=fontfile=${F}:textfile=label-cpu.txt:fontcolor=white:fontsize=34:x=20:y=16[a];\
[1:v]pad=iw:ih+70:0:70:color=0x181a21,drawtext=fontfile=${F}:textfile=label-gpu.txt:fontcolor=0x8ce678:fontsize=34:x=20:y=16[b];\
[a][b]hstack=inputs=2:shortest=1,pad=iw+20:ih:10:0:color=0x0e0f13,drawtext=fontfile=${F}:textfile=label-speed.txt:fontcolor=0xffdc78:fontsize=34:x=w-tw-30:y=16" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p bunko-cpu-vs-gpu-x5.mp4
ffmpeg -loglevel error -y -i firefox-search.mkv -t 12.5 -c:v libx264 -crf 18 -pix_fmt yuv420p firefox-search-cut.mp4
