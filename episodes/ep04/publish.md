# 第4弾 公開用メモ

## YouTube に渡すファイル

- タイトル案：`【ローカル LLM で遊ぼう #4】0.8B で爆速ページ翻訳｜PLaMo 3 Translate`
- 動画：`out/video/video.mp4`（1920×1080、H.264/AAC、8分3秒）
- サムネイル：`out/video/thumbnail.png`
- 概要欄：`out/video/description.txt`（`meta.py` から生成）
- 日本語字幕：`out/video/subtitles.srt`（83行）
- 解説ページ：<https://local-llm-plamo-translate-guide.brownhost.chatgpt.site/>

## 確認済み

- 動画・字幕・解説サイトの動画は同じ版。解説サイトの日本語字幕も83行。サイト掲載用の動画は配信上限に収めるため再圧縮した。
- ダウンロード画面には `llama-server -hf pfnet/plamo-3-translate-0.8b-GGUF:Q4_K_M` を表示。
- 概要欄に PFN 公式比較図の出典、VOICEVOX 3人、BGM、春日部つむぎSD絵、`Codex GPT-6-Sol` の制作表記がある。
- `EPISODE=ep03 python3 video/render.py --still 1`、Python 構文確認、サイト内の参照先確認、`git diff --check` を通過。

## 公開状態

- 解説サイトの版10を公開済み。動画・字幕・実録・クレジットを反映した。
- YouTube への動画アップロードは制作者が行う。
- 再描画に必要な公式イラスト・公式比較図・春日部つむぎSD絵は `assets/official/` に置き、リポジトリには含めない。完成動画はサイトの公開素材に含める。
