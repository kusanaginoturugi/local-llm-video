#!/bin/sh
# 第5弾：Firefox の PDF ビューアで「明智」を検索し、本文をなぞる場面を撮る。
# 前提：ワークスペース 9 に、issun-boshi-cuda.pdf を開いた Firefox の浮いた窓（320,180 に 1920x1080）があり、
#       ydotoold が動いていること。撮るのはアドレスバーより下（ユーザー名入りのパスを写さない）。
# 撮影中（約 25 秒）はマウスとキーボードに触らない。
set -eu
cd "$(dirname "$0")"
# ydotool の絶対移動はマウスの加速でずれるので、カーソルは Hyprland に動かしてもらい、ydotool はボタンだけ押す
move() { hyprctl dispatch "hl.dsp.cursor.move({ x = $1, y = $2 })" >/dev/null; }
PDF=$(realpath ../ndl/issun-boshi-cuda.pdf)
OUT=firefox-search.mkv
[ -e "$OUT" ] && mv "$OUT" "firefox-search-$(date +%H%M%S).mkv"

# キー入力が Firefox に入るよう、PDF の窓へフォーカスを移す（終わったら元の窓へ戻す）
BACK=$(hyprctl activewindow -j | python3 -c 'import json,sys; print(json.load(sys.stdin).get("address", ""))')
WIN=$(hyprctl clients -j | python3 -c 'import json,sys; print(next(c["address"] for c in json.load(sys.stdin) if c["title"].startswith("issun-boshi-cuda.pdf")))')
hyprctl dispatch "hl.dsp.focus({ window = \"address:$WIN\" })" >/dev/null
sleep 1
# 40 コマ目を、検索バーを閉じた状態で出す
wtype -k Escape; sleep 0.3
wtype -M ctrl l -m ctrl; sleep 0.3; wtype "file://$PDF#page=39"; wtype -k Return; sleep 1
wtype -M ctrl l -m ctrl; sleep 0.3; wtype "file://$PDF#page=40"; wtype -k Return; sleep 2
move 2300 1300

wf-recorder -g "320,264 1920x996" -r 30 -f "$OUT" >/dev/null 2>&1 &
REC=$!
sleep 3
# 検索：1 文字ずつ打って Enter
wtype -M ctrl f -m ctrl; sleep 1
wtype -d 350 "明智"; sleep 0.8
wtype -k Return; sleep 3
# 「Highlight All」のチェックボックスを押す
move 688 1236; sleep 0.5
ydotool click 0xC0 >/dev/null 2>&1; sleep 0.5
move 2300 1300; sleep 3
# 次の一致（67 件目）は 41 コマ目なので進まない。検索を閉じる
wtype -k Escape; sleep 1
# 左ページの「山野夫人は…明智に…」の列を上から下へなぞる
move 1256 585; sleep 1
ydotool click 0x40 >/dev/null 2>&1
y=600
while [ "$y" -le 1150 ]; do
  move 1256 "$y"
  sleep 0.05
  y=$((y + 20))
done
ydotool click 0x80 >/dev/null 2>&1; sleep 3
move 2300 1300; sleep 2
kill -INT "$REC"
wait "$REC" 2>/dev/null || true
[ -n "$BACK" ] && hyprctl dispatch "hl.dsp.focus({ window = \"address:$BACK\" })" >/dev/null
echo "$(pwd)/$OUT: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT") 秒"
