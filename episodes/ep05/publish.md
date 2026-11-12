# 第5弾 公開用メモ

## YouTube に渡すファイル

- タイトル案：`【ローカル LLM で遊ぼう #5】スキャンした本を検索できる PDF に｜NDLOCR-Lite × GPU`
- 動画：`out/video/video.mp4`（1920×1080、H.264/AAC、約 10 分 7 秒）
- サムネイル：`out/video/thumbnail.png`
- 概要欄：`out/video/description.txt`（`meta.py` から生成）
- 日本語字幕：`out/video/subtitles.srt`（台本 106 行、字幕の区切り 107 個）
- 解説記事：<https://claude.ai/artifact/QaLfsP48pZJ9tTHoK1QNLQ>（ソースは `article.html`）。いまは非公開なので、公開前に記事の共有メニューで「リンクを知っている全員」にする

## 確認済み

- 実録：CPU と GPU の端末の画面は、`ocr.py` を実際に流した記録（`demo/rec/bunko-*.jsonl`）を時刻どおりに再生したもの。Firefox の検索は実画面の録画（アドレスバーより下だけ）。
- タイミング：51 行目「え、もう終わった？」の時点で、GPU 側は `real 67.5 s` まで出て終わり、CPU 側は 71/356 ページ。
- 自炊本は書名・ページ数・時間だけを出し、ページの画像も本文も出していない。画面に出す本はすべて国立国会図書館デジタルコレクションの保護期間満了の『一寸法師』。
- 読み：`voice/check.py` で、ずれの大きい行を確認（割愛＝かつあい、屠る＝ほふる、言質＝げんち は VOICEVOX の読みどおりで、whisper の書き取りの癖）。

## 公開前にやること

- 解説記事を共有（上記）。
- 第4弾の YouTube の URL が決まっていれば、`meta.py` の「これまでの回」と README に入れる。
