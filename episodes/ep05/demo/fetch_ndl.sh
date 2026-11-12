#!/bin/sh
# 国立国会図書館デジタルコレクションから、デモに使う本の全コマを取ってきて 1 つの PDF にする。
# 江戸川乱歩『一寸法師』（1935）pid 1170887。公開範囲は保護期間満了（PDM）。
# 使い方: sh fetch_ndl.sh  → ndl/raw/*.jpg と ndl/issun-boshi.pdf
set -eu
PID=${PID:-1170887}
cd "$(dirname "$0")"
mkdir -p ndl/raw
[ -s ndl/manifest.json ] || curl -sSf -A 'Mozilla/5.0' -o ndl/manifest.json "https://dl.ndl.go.jp/api/iiif/$PID/manifest.json"
N=$(python3 -c 'import json; print(len(json.load(open("ndl/manifest.json"))["sequences"][0]["canvases"]))')
i=1
while [ "$i" -le "$N" ]; do
  f=ndl/raw/$(printf %03d "$i").jpg
  if [ ! -s "$f" ]; then
    # 速く取りに行くと 403 で止められるので、1 コマごとに間をあける
    curl -sSf -A 'Mozilla/5.0' --retry 3 -o "$f.part" \
      "https://dl.ndl.go.jp/api/iiif/$PID/R$(printf %07d "$i")/full/full/0/default.jpg"
    mv "$f.part" "$f"
    sleep 3
  fi
  i=$((i + 1))
done
# 画像に解像度の情報がないので 300dpi とみなす。ocr.py --pdf-render-dpi 300 で元の画素のまま読める
img2pdf --imgsize 300dpi ndl/raw/*.jpg -o ndl/issun-boshi.pdf
echo "ndl/issun-boshi.pdf: $N pages"

# 突き合わせ用の青空文庫版（作品 58053、底本は光文社文庫の全集。新字・新かな）
mkdir -p aozora
[ -s aozora/issun-boshi.txt ] || {
  curl -sSf -A 'Mozilla/5.0' -o aozora/58053.zip https://www.aozora.gr.jp/cards/001779/files/58053_ruby_62788.zip
  unzip -o -q -d aozora aozora/58053.zip
  iconv -f cp932 -t utf-8 aozora/issunboshi.txt > aozora/issun-boshi.txt
}
