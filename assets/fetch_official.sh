#!/bin/sh
# 東北ずん子・ずんだもんプロジェクトの公式イラストを取ってくる。
# 再配布を避けるため、リポジトリには画像そのものを入れていない。
# 利用条件: https://zunko.jp/guideline.html
set -eu
cd "$(dirname "$0")"
mkdir -p official
curl -fL -o official/met012.png https://zunko.jp/sozai/methane/met012.png
curl -fL -o official/zunmon003.png https://zunko.jp/sozai/zundamon/zunmon003.png
