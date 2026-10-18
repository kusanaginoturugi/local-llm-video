#!/bin/sh
# 東北ずん子・ずんだもんプロジェクトの公式イラストを取ってくる。
# 再配布を避けるため、リポジトリには画像そのものを入れていない。
# 利用条件: https://zunko.jp/guideline.html
set -eu
cd "$(dirname "$0")"
mkdir -p official
curl -fL -o official/met012.png https://zunko.jp/sozai/methane/met012.png
curl -fL -o official/zunmon003.png https://zunko.jp/sozai/zundamon/zunmon003.png

# リアクション用の SD 絵（めたんの一部は PSD でしか配布されていないので ffmpeg で PNG にする）
mkdir -p official/sd
for f in met_s214 met_s215 met_s218 met_s221 met_s222; do
  curl -fL -o official/sd/$f.psd https://zunko.jp/sozai/methane/$f.psd
  ffmpeg -loglevel error -y -i official/sd/$f.psd official/sd/$f.png && rm official/sd/$f.psd
done
for f in 3009 3013 3015 3016 3017 3019 3020 3021 3022 3030; do
  curl -fL -o official/sd/zunmon_$f.png https://zunko.jp/sozai/zundamon/zunmon_$f.png
done
