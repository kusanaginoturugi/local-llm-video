#!/bin/sh
# 東北ずん子・ずんだもんプロジェクトの公式イラストを取ってくる。
# 再配布を避けるため、リポジトリには画像そのものを入れていない。
# 利用条件: https://zunko.jp/guideline.html
set -eu
cd "$(dirname "$0")"
mkdir -p official
# キャラクターは SD 絵で統一する。ふだんの絵（めたん met_s209、ずんだもん zunmon_3002）と、
# リアクション用の表情違い。めたんの一部は PSD でしか配布されていないので ffmpeg で PNG にする
mkdir -p official/sd
curl -fL -o official/sd/met_s209.png https://zunko.jp/sozai/methane/met_s209.png
curl -fL -o official/sd/zunmon_3002.png https://zunko.jp/sozai/zundamon/zunmon_3002.png
for f in met_s214 met_s215 met_s218 met_s221 met_s222; do
  curl -fL -o official/sd/$f.psd https://zunko.jp/sozai/methane/$f.psd
  ffmpeg -loglevel error -y -i official/sd/$f.psd official/sd/$f.png && rm official/sd/$f.psd
done
for f in 3009 3013 3015 3016 3017 3019 3020 3021 3022 3030; do
  curl -fL -o official/sd/zunmon_$f.png https://zunko.jp/sozai/zundamon/zunmon_$f.png
done
# 第4弾の春日部つむぎ。映像利用可、素材の再配布不可。
# https://kasukabe294.booth.pm/items/3474402
curl -fL -o official/tsumugi.webp https://voicevox.hiroshiba.jp/_astro/portrait-kasukabe_tsumugi.BhVWXYsI_jzt5L.webp
# 第4弾で引用する Preferred Networks の図13。出典を概要欄に記す。
curl -fL -o official/pfn-figure13.png https://pfn-web-static-contents-kuroco.s3.ap-northeast-1.amazonaws.com/files/a/public/news/press-performance-log-no-lead-comparison.png
