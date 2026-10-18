#!/bin/sh
# BGM を魔王魂から取ってくる（CC BY 4.0、https://maou.audio/rule/）。
# 曲ページからのダウンロードとして取得する。リポジトリには曲ファイルを入れていない。
set -eu
cd "$(dirname "$0")"
mkdir -p bgm
curl -fL -A 'Mozilla/5.0' -e https://maou.audio/bgm_acoustic51/ \
  -o bgm/maou_loop_bgm_acoustic51.mp3 https://maou.audio/sound/bgm/maou_loop_bgm_acoustic51.mp3
