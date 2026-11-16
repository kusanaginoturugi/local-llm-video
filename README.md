# ローカル LLM で遊ぼう（動画制作）

YouTube の解説動画シリーズ「ローカル LLM で遊ぼう」を作るためのリポジトリです。
台本から VOICEVOX で音声を合成し、口パクつきの解説動画と概要欄の文面までを生成します。

- 第1弾：llama-server を立ち上げよう（2026-10-18 公開、`episodes/ep01/`）
  - 動画: https://youtu.be/3Sk9T1VqNsg
  - 記事: https://claude.ai/code/artifact/2be896e8-2ab9-4dd7-bf05-cff1beb45e71
  - 台本: https://claude.ai/code/artifact/45ace86b-536a-4dd5-a09a-cb9db2f17fa1
- 第2弾：whisper.cpp で音声入力を作ろう（2026-10-22 公開、`episodes/ep02/`）
  - 動画: https://youtu.be/k-ploGYRc_Q
  - 記事: https://claude.ai/artifact/Bdmebajj8SxkXZtU4cznmS
  - 台本: https://claude.ai/artifact/PJcRLgEeSwghav4EFVSSHE
  - 解説しているスクリプト: https://github.com/kusanaginoturugi/voice-input/tree/main/lite
- 第3弾：声で話しかけると声で返事をする AI（制作中、`episodes/ep03/`）
  - 記事: https://claude.ai/artifact/XUxWANTPfE6osvRi4zTb6U
  - 台本: https://claude.ai/artifact/XVRqxtD2fCeVedg1qbSC9c
  - 作った voice-chat: https://github.com/kusanaginoturugi/voice-chat
  - 台本は `episodes/ep03/build_script.py` から script.tsv と screens.tsv を書き出す。デモの返事（「パソコンのずんだもん」などの行）は `demo/run_demos.py` で実際に作った `demo/demos.json` を使う
- 第4弾：Local LLM Translator と PLaMo 3 Translate 0.8B（`episodes/ep04/`）
  - 動画: https://youtu.be/TUADm3MbcKE
  - 解説ページ: https://local-llm-plamo-translate-guide.brownhost.chatgpt.site/
  - 台本は `episodes/ep04/build_script.py`、演出は `episodes/ep04/build_direction.py` から生成する
  - `demo/benchmark.py` で拡張の Custom 設定に近い API リクエストを実測。`demo/results-gpu.json` と `demo/results-cpu.json` が原記録
  - 動画の速度画面は、拡張で同じ記事を翻訳した `demo/browser-translategemma12b-glow-tab.mkv` と `demo/browser-plamo-glow-tab.mkv` の実録。PLaMo は等速と4倍スローで見せる。両方ともキャッシュをオフにして Translation glow effect を有効にした
  - `demo/capture_tab.mjs` はブラウザのタブを直接録画する。12B はスクロール開始を8秒遅らせ、PLaMo は2秒後に開始する。12B の llama.cpp に言語を指定するため、録画時だけ `demo/translategemma_proxy.py` を使った
  - API の実測値と計測条件は `demo/results-gpu.json` と解説ページにまとめる。ブラウザの実録は体感用
  - 拡張の PLaMo 設定と実測条件は `episodes/ep04/notes.md` を参照
  - つむぎの乱入は公式イラストを参考にしたSD絵の怒り・笑顔差分を中央に表示する。画像は再配布せず、ローカルの `assets/official/tsumugi-sd-angry.png` と `assets/official/tsumugi-sd-happy.png` に置く

- 第5弾：スキャンした本を NDLOCR-Lite で検索できる PDF に（`episodes/ep05/`）
  - 記事: https://claude.ai/artifact/QaLfsP48pZJ9tTHoK1QNLQ（ソースは `episodes/ep05/article.html`）
  - 台本は `episodes/ep05/build_script.py`、演出と章は `episodes/ep05/build_direction.py` から生成する
  - デモの本は国立国会図書館デジタルコレクションの江戸川亂歩『一寸法師』（1935、保護期間満了）。`demo/fetch_ndl.sh` で取ってきて PDF にし、青空文庫版も落とす
  - OCR の環境は `demo/setup.sh`（NDLOCR-Lite v1.4.0 と onnxruntime-gpu）。答え合わせは `demo/compare_aozora.py` と `demo/crop_candidates.py`、紙を白くする実験は `demo/clean.py`
  - CPU と GPU の端末の画面は `video/termrec.py` で実行の記録を取り、時刻どおりに再生して作った（`demo/rec/`）。Firefox の検索の画面は `demo/rec/record_firefox.sh` で撮った
  - 計測と答え合わせの数字、判断の経緯は `episodes/ep05/notes.md`

- 第6弾：Kindle の英語の本を、手元の LLM で訳して読む（`episodes/ep06/`）
  - 作った kindle-ja: https://github.com/kusanaginoturugi/kindle-ja
  - 台本は `episodes/ep06/build_script.py`、演出と章は `episodes/ep06/build_direction.py` から生成する
  - デモの本は Kindle の 0 円の『地下の国のアリス』（Alice's Adventures Under Ground、1886 年の手書き本の複製、保護期間満了）。制作者が買った本のページや本文は出さない
  - 計測・実録・静止画は `demo/record_kindle.sh`（ワークスペース 9 に Firefox と kindle-ja の Emacs を並べて撮る）。実録は `demo/rec/`、静止画は `slides/`
  - 計測の数字、撮影でつまずいたこと、判断の経緯は `episodes/ep06/notes.md`
  - 第6弾は RTX 3060 の PC で作った（第5弾までは RTX 4070）。この PC にはつむぎの SD 絵がないので、確認用の動画はダミーの絵で組み立てた

第1〜3弾の制作には Claude Code、画面の撮影には Claude in Chrome を使用しました。第4弾の台本・記事・検証・動画の組み立てには Codex GPT-6-Sol、第5・6弾には Claude Code（Claude Opus 5.5）を使用しました。

## 構成

回ごとのファイルは `episodes/epNN/` にまとめ、作る回は環境変数 `EPISODE`（例 `EPISODE=ep01`）で選びます。指定がなければいちばん新しい回です。

| パス | 中身 |
| --- | --- |
| `episodes/epNN/script.tsv` | 台本（行番号・話者・セリフ） |
| `episodes/epNN/direction.tsv` | 行ごとの演出（声のスタイル・抑揚・前の間・動き・リアクションの SD 絵）と、その行だけの読み（`yomi`） |
| `episodes/epNN/dict.tsv` | この回だけで使う読み |
| `episodes/epNN/screens.tsv` | 行ごとのセクション名と、台本の「画面」欄 |
| `episodes/epNN/slides.py` | 行番号ごとに背景に出す画面（表・ターミナル・スクショなど） |
| `episodes/epNN/slides/` | その回の構成図とスクリーンショット |
| `episodes/epNN/meta.py` | 概要欄の文面とサムネイルの文言 |
| `episodes/epNN/demo/` | 撮影や検証に使った設定と素材 |
| `episodes/epNN/out/` | 生成物（音声 `voice/`、動画・概要欄・字幕・サムネイル `video/`）。リポジトリには入れない |
| `characters.md` | 登場キャラクターの公式設定と、この動画での扱い（話し方・お互いの呼び方） |
| `episode.py` | 作る回を決め、その回のファイルの場所を返す |
| `voice/dict_common.tsv` | シリーズ共通の読み（毎回出てくる技術用語） |
| `voice/synth.py` | VOICEVOX で一括合成し、その回の `out/voice/` に wav とタイムラインを出す |
| `voice/score.py` | 音名と長さを並べたテキストから、VOICEVOX の歌の楽譜（JSON）を作る。direction.tsv の sing 列に .txt を書けば synth.py が直接読む |
| `voice/check.py` | 合成した声を whisper-server で文字起こしし、台本とずれている行を一覧にする |
| `video/slidekit.py` | `slides.py` で使う画面の部品（title・table・term・flow など） |
| `video/make_mouths.py` | 公式の SD 絵から口パク用の差分（閉じ・半開き・開き）を作る |
| `video/termshot.py` | コマンドを仮想の端末で動かし、画面を PNG にする（pyte が必要） |
| `video/termrec.py` | コマンドを仮想の端末で動かして出力と時刻を記録し、あとで動画にする（pyte が必要） |
| `video/render.py` | 動画 `video.mp4`、概要欄 `description.txt`、字幕 `subtitles.srt`（`--srt`）を作る |
| `video/make_thumbnail.py` | サムネイル `thumbnail.png`（1280x720）を作る |
| `assets/fetch_official.sh` | 公式の SD 絵（ふだんの絵とリアクション用の表情違い）を zunko.jp から取ってくる |
| `assets/fetch_bgm.sh` | BGM（魔王魂）を取ってくる |
| `assets/bg/rgb_desk.jpg` | 背景写真（CC0） |

## 必要なもの

- Python 3（Pillow、numpy）
- ffmpeg
- VOICEVOX ENGINE（既定は `http://localhost:50021`。`VOICEVOX_URL` で変えられる）
- フォント：Noto Sans CJK JP、PlemolJP Console（AUR の `ttf-plemoljp-bin`。第5弾までは Cica）（パスは `video/render.py` の先頭）

## 作り方

```sh
sh assets/fetch_official.sh      # 公式イラストを取得（PSD の変換に ffmpeg を使う）
sh assets/fetch_bgm.sh           # BGM を取得
python3 video/make_mouths.py     # 口パク用の差分を作る
python3 voice/synth.py           # 音声を合成（--kana all で読みの確認）
python3 video/render.py          # 動画と概要欄を作る
EPISODE=ep01 python3 video/render.py   # 前の回を作り直す
```

読みの置き換えは、行ごとの読み（`direction.tsv` の `yomi` 列、例 `九割五分=きゅうわりごぶ;黄色=きいろ`）→ この動画の辞書 → シリーズ共通の辞書の順に当てます。
VOICEVOX 本体のユーザー辞書は変更しません。英字の語は単語の区切りでだけ置き換えます（`ini` は `Gemini` には当たりません）。
1 か所だけの読み間違いは辞書に入れず、行ごとの読みで直してください。`annotate` 列が `yes` の語は、字幕で最初に出たときだけ「VRAM（ブイラム）」のように読みを添えます。

耳が VOICEVOX の読み方に慣れると、聞き間違えやすい読みに気づきにくくなります。`python3 voice/check.py` で合成した声を whisper-server に文字起こしさせ、台本とずれている行を、ずれの大きい順に出せます（第1弾では「Qwen 3」が「クエン酸」と書き取られて見つかりました）。英語をカタカナで書き取るだけのずれも出るので、上から耳で確かめてください。

確認用に、`video/render.py --preview 30`（先頭 30 秒）、`--still 64`（64 行目の 1 コマ）、`--description`（概要欄だけ）が使えます。

## ライセンスと利用条件

このリポジトリのコード、台本、演出データ、構成図は MIT License です（`LICENSE`）。背景写真と、次に挙げる素材は除きます。

次のものは、それぞれの規約に従ってください。

- 音声：VOICEVOX で合成した四国めたん・ずんだもん・春日部つむぎの音声は、[VOICEVOX 利用規約](https://voicevox.hiroshiba.jp/term/)と各音源の利用規約に従います。公開時はクレジット表記「VOICEVOX:四国めたん」「VOICEVOX:ずんだもん」「VOICEVOX:春日部つむぎ」が必要です。
- イラスト：四国めたん・ずんだもんのイラストは[東北ずん子・ずんだもんプロジェクト](https://zunko.jp/)の公式素材です。[キャラクター利用ガイドライン](https://zunko.jp/guideline.html)に従ってください。再配布を避けるため、画像そのものと口パク差分はリポジトリに含めていません。
- Live2D モデル：四国めたん・ずんだもん（坂本アヒル式）は[東北ずん子・ずんだもんプロジェクト公式ショップ](https://shop.zunko.jp/)で購入したものです。ローカルの `assets/live2d/` に置き、リポジトリには含めません。
- 春日部つむぎ：第4弾のSD絵は[KASUKABEproject の公式立ち絵](https://kasukabe294.booth.pm/items/3474402)を参考に生成・編集したものです。画像はリポジトリに含めず、動画に使用します。
- スクリーンショット：`episodes/ep01/slides/hf-*.png` と `episodes/ep02/slides/hf-whisper-files.png` は Hugging Face の画面、`episodes/ep02/slides/voxtype-github.png` は GitHub の画面です。
- BGM：[魔王魂](https://maou.audio/)「[アコースティック51](https://maou.audio/bgm_acoustic51/)」（CC BY 4.0）。公開時はクレジット表記「BGM：魔王魂」が必要です。リポジトリには曲ファイルを含めていません。
- 背景写真：SankalpSasnur「[RGB desktop computer setup with keyboard and monitor](https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg)」（CC0、Wikimedia Commons）。
