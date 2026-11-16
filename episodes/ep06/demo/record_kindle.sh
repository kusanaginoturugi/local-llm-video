#!/bin/sh
# 第6弾：Kindle Cloud Reader の『地下の国のアリス』の Chapter I で、kindle-ja を計測・撮影する。
#
# 使い方: record_kindle.sh 出力先ディレクトリ
#   STEPS（既定 "measure 12b page rec-first rec-final find"）で、やる段だけを選べる。計測の時間は timings.tsv に足していく。
#
# 前提：
#   - ワークスペース 9 に、Firefox（左、22,66 に 1251x1352）と kindle-ja の Emacs の窓（右）だけがある
#   - Firefox は Kindle のタブで、Chapter I のページを出している
#   - kindle-ja、kindle-ja-ocrd、llm-unload が入っている
# 実行中（数分）はワークスペースを切り替えない・マウスとキーボードに触らない。
# 撮る直前に毎回ワークスペース 9 か確かめ、違えば止める（別の画面を読んだり撮ったりしないため）。
# 撮ったものには、確かめるまで個人の画面が入っているかもしれないので、まず作業用の場所に出す。
set -eu

out=${1:?usage: record_kindle.sh OUTDIR}
mkdir -p "$out/org" "$out/stub"
out=$(cd "$out" && pwd)
org="$out/org"
# 本文の範囲（Chapter I の見出しから、見えている最後の行まで）。目次のリンクは外す
geometry="150,625 995x715"
# Firefox の中身（タブとアドレスバーより下）と、録画の範囲（Firefox と Emacs。上の帯はあとで隠す）
firefox_body="23,154 1250x1260"
rec_area="22,66 2516x1352"

# 通知は録画に写るので止める
printf '#!/bin/sh\nexit 0\n' > "$out/stub/notify-send"
chmod +x "$out/stub/notify-send"
PATH="$out/stub:$PATH"
export PATH KINDLE_JA_DIR="$org" KINDLE_JA_GEOMETRY="$geometry" KINDLE_JA_VOICE=off

back=$(hyprctl activeworkspace -j | jq -r .id)
hyprctl dispatch "hl.dsp.focus({ workspace = 9 })" >/dev/null
trap 'hyprctl dispatch "hl.dsp.focus({ workspace = $back })" >/dev/null' EXIT
sleep 1.5
# カーソルは Emacs の右下の隅へ（録画の範囲に写らないよう、画面の端）
hyprctl dispatch "hl.dsp.cursor.move({ x = 2559, y = 1439 })" >/dev/null

on9() {
  ws=$(hyprctl activeworkspace -j | jq -r .id)
  [ "$ws" = 9 ] || { echo "ワークスペースが $ws になったので止めた" >&2; exit 1; }
}

focus_firefox() {
  ff=$(hyprctl clients -j | jq -r '.[] | select(.workspace.id == 9 and (.class | test("firefox"))) | .address')
  hyprctl dispatch "hl.dsp.focus({ window = \"address:$ff\" })" >/dev/null
  sleep 0.5
}

# 取り込む範囲の先頭が Chapter I の見出しで、本文が続いているか OCR で確かめる。
# 違えば、まず Esc でページ内検索の欄を閉じ（欄が開いていると Kindle がページを組み直す）、次に右矢印で送る（3 回まで）
ensure_chapter() {
  for _ in 1 2 3; do
    on9
    grim -g "$geometry" "$out/check.png"
    text=$(tesseract "$out/check.png" - -l eng 2>/dev/null)
    if printf '%s\n' "$text" | sed '/^[[:space:]]*$/d' | head -n 1 | grep -q '^Chapter' &&
      printf '%s\n' "$text" | grep -q 'Alice was beginning'; then
      rm -f "$out/check.png"
      return 0
    fi
    focus_firefox
    wtype -k Escape
    sleep 2
    grim -g "$geometry" "$out/check.png"
    tesseract "$out/check.png" - -l eng 2>/dev/null | sed '/^[[:space:]]*$/d' | head -n 1 | grep -q '^Chapter' && continue
    wtype -k Right
    sleep 2
  done
  echo "Chapter I のページが出せなかった" >&2
  exit 1
}

timed() {  # timed ラベル 本 [環境変数…]
  label=$1 book=$2
  shift 2
  rm -f "$org/$book.org"
  on9
  s=$(date +%s.%N)
  result=ok
  env "$@" kindle-ja "$book" >/dev/null 2>&1 || result=failed
  e=$(date +%s.%N)
  printf '%s\t%s\t%.2f\t%s\n' "$label" "$book" "$(echo "$e - $s" | bc)" "$result" | tee -a "$out/timings.tsv"
}

steps=${STEPS:-measure 12b page rec-first rec-final find}
step() { case " $steps " in *" $1 "*) return 0 ;; esac; return 1; }

# 1. 計測（別の Org に書くので、右の Emacs の画面は変わらない）
if step measure; then
for i in 1 2 3; do timed "tesseract+E4B" "m-e4b-$i" KINDLE_JA_OCR=tesseract KINDLE_JA_LLM_MODEL=gemma-4-E4B-it-qat; done
for i in 1 2 3; do timed "tesseract+PLaMo" "m-plamo-$i" KINDLE_JA_OCR=tesseract; done
systemctl --user start kindle-ja-ocrd.service
until curl -sf --max-time 1 http://127.0.0.1:8093/health >/dev/null 2>&1; do sleep 0.5; done
for i in 1 2 3; do timed "ocrd+PLaMo" "m-final-$i"; done
fi
# 12B は E4B と同時に載らないので、E4B を降ろして測り、あとで載せ直す（載っていなければ降ろさない）
# OCR サーバー（約 1GB）と PLaMo も降ろさないと、12B（約 7.9GB）が入りきらない
if step 12b; then
systemctl --user stop kindle-ja-ocrd.service
llm-unload gemma-4-E4B-it-qat plamo-3-translate-0.8b >/dev/null 2>&1 || :
for i in 1 2 3; do timed "tesseract+12B" "m-12b-$i" KINDLE_JA_OCR=tesseract KINDLE_JA_LLM_MODEL=gemma-4-12b-it-qat-imatrix; done
llm-unload gemma-4-12b-it-qat-imatrix >/dev/null 2>&1 || :
curl -s -m 120 http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"gemma-4-E4B-it-qat","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' >/dev/null
fi

# 2. 静止画：ページ
if step page; then
ensure_chapter
grim -g "$firefox_body" "$out/kindle-page.png"
fi

# 3. 実録：Emacs の alice.org を空にしてから、キーを押す代わりに kindle-ja を動かす
# 右の Emacs の窓が開いている Org ファイル（kitty … emacs -nw ファイル）に書く
view_org() {
  pid=$(hyprctl clients -j | jq -r '.[] | select(.workspace.id == 9 and .class == "kindle-ja") | .pid')
  tr '\0' '\n' < "/proc/$pid/cmdline" | sed -n '/^-nw$/{n;p;q}'
}

record() {  # record ファイル名 [環境変数…]
  name=$1
  shift
  view=$(view_org)
  [ -n "$view" ] || { echo "kindle-ja の Emacs の窓が見つからない" >&2; exit 1; }
  printf '#+title: %s\n' "$(basename "$view" .org)" > "$view"
  sleep 2  # Emacs が読み直すのを待つ
  # Firefox にフォーカスを移すとカーソルが窓の中央に飛ぶので、録画の前に隅へ戻す
  hyprctl dispatch "hl.dsp.cursor.move({ x = 2559, y = 1439 })" >/dev/null
  on9
  wf-recorder -g "$rec_area" -r 30 -f "$out/$name.mkv" >/dev/null 2>&1 &
  rec=$!
  sleep 2
  on9
  s=$(date +%s.%N)
  env KINDLE_JA_DIR="$(dirname "$view")" "$@" kindle-ja "$(basename "$view" .org)" >/dev/null 2>&1
  e=$(date +%s.%N)
  printf 'rec %s\t%.2f\n' "$name" "$(echo "$e - $s" | bc)" | tee -a "$out/timings.tsv"
  sleep 6
  kill -INT "$rec"
  wait "$rec" || :
}

if step rec-first || step rec-final; then
ensure_chapter
# 実録の前に、使うモデルと OCR サーバーを起こしておく（読み込みの時間を写さない）
curl -s -m 120 http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"gemma-4-E4B-it-qat","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' >/dev/null
curl -s -m 120 http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"plamo-3-translate-0.8b","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' >/dev/null
systemctl --user start kindle-ja-ocrd.service
until curl -sf --max-time 1 http://127.0.0.1:8093/health >/dev/null 2>&1; do sleep 0.5; done
# OCR サーバーは、起こした直後の 1 枚目だけ GPU の計算方法を探して遅い。同じ大きさの画像を 2 回読ませて温める
grim -g "$geometry" "$out/warm.png"
curl -sf --data-binary @"$out/warm.png" http://127.0.0.1:8093/ocr >/dev/null
curl -sf --data-binary @"$out/warm.png" http://127.0.0.1:8093/ocr >/dev/null
rm -f "$out/warm.png"
if step rec-first; then record rec-first KINDLE_JA_OCR=tesseract KINDLE_JA_LLM_MODEL=gemma-4-E4B-it-qat; fi
if step rec-final; then record rec-final; fi
on9
grim -g "1287,66 1251x1352" "$out/emacs.png"
fi
# 4. 静止画：ページ内検索で 0 件（本文にしかない daisy を探す。上の書名の帯は文字として入っているので Alice は当たる）。検索欄が出ると Kindle がページを組み直すので最後に撮り、あとで Chapter I に戻す。
# 日本語入力（SKK）を通すと英字が「▽ありえ」のようになるので、打たずにクリップボードから貼る。
# クリップボードの文字は、終わったら元に戻す
if step find; then
on9
focus_firefox
clip=$(wl-paste -n 2>/dev/null || :)
printf 'daisy' | wl-copy >/dev/null 2>&1
wtype -M ctrl f -m ctrl
sleep 1
wtype -M ctrl v -m ctrl
sleep 2
on9
grim -g "$firefox_body" "$out/kindle-find.png"
wtype -k Escape
printf '%s' "$clip" | wl-copy >/dev/null 2>&1  # wl-copy は裏に残るので、出力を切り離す
hyprctl dispatch "hl.dsp.cursor.move({ x = 2559, y = 1439 })" >/dev/null
sleep 2
ensure_chapter
fi
echo "撮り終わった"
