# ローカル LLM で遊ぼう（動画制作）

YouTube の解説動画シリーズ「ローカル LLM で遊ぼう」を作るためのリポジトリです。
台本から VOICEVOX で音声を合成し、口パクつきの解説動画と概要欄の文面までを生成します。

- 第1弾：llama-server を立ち上げよう（2026-10-18 公開、`episodes/ep01/`）
  - 動画: https://youtu.be/3Sk9T1VqNsg
  - 記事: https://claude.ai/code/artifact/2be896e8-2ab9-4dd7-bf05-cff1beb45e71
  - 台本: https://claude.ai/code/artifact/45ace86b-536a-4dd5-a09a-cb9db2f17fa1
- 第2弾：whisper.cpp で音声入力を作ろう（制作中、`episodes/ep02/`）
  - 記事: https://claude.ai/artifact/Bdmebajj8SxkXZtU4cznmS
  - 台本: https://claude.ai/artifact/PJcRLgEeSwghav4EFVSSHE
  - 解説しているスクリプト: https://github.com/kusanaginoturugi/voice-input/tree/main/lite

台本・記事・検証・動画の組み立ては Claude Code、画面の撮影は Claude in Chrome で行いました。

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
| `episode.py` | 作る回を決め、その回のファイルの場所を返す |
| `voice/dict_common.tsv` | シリーズ共通の読み（毎回出てくる技術用語） |
| `voice/synth.py` | VOICEVOX で一括合成し、その回の `out/voice/` に wav とタイムラインを出す |
| `voice/check.py` | 合成した声を whisper-server で文字起こしし、台本とずれている行を一覧にする |
| `video/slidekit.py` | `slides.py` で使う画面の部品（title・table・term・flow など） |
| `video/make_mouths.py` | 公式の SD 絵から口パク用の差分（閉じ・半開き・開き）を作る |
| `video/termshot.py` | コマンドを仮想の端末で動かし、画面を PNG にする（pyte が必要） |
| `video/render.py` | 動画 `video.mp4`、概要欄 `description.txt`、字幕 `subtitles.srt`（`--srt`）を作る |
| `video/make_thumbnail.py` | サムネイル `thumbnail.png`（1280x720）を作る |
| `assets/fetch_official.sh` | 公式の SD 絵（ふだんの絵とリアクション用の表情違い）を zunko.jp から取ってくる |
| `assets/fetch_bgm.sh` | BGM（魔王魂）を取ってくる |
| `assets/bg/rgb_desk.jpg` | 背景写真（CC0） |

## 必要なもの

- Python 3（Pillow、numpy）
- ffmpeg
- VOICEVOX ENGINE（既定は `http://localhost:50021`。`VOICEVOX_URL` で変えられる）
- フォント：Noto Sans CJK JP、Cica（パスは `video/render.py` の先頭）

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

- 音声：VOICEVOX で合成した四国めたん・ずんだもんの音声は、[VOICEVOX 利用規約](https://voicevox.hiroshiba.jp/term/)と[音源利用規約](https://zunko.jp/con_ongen_kiyaku.html)に従います。公開時はクレジット表記「VOICEVOX:四国めたん」「VOICEVOX:ずんだもん」が必要です。
- イラスト：四国めたん・ずんだもんのイラストは[東北ずん子・ずんだもんプロジェクト](https://zunko.jp/)の公式素材です。[キャラクター利用ガイドライン](https://zunko.jp/guideline.html)に従ってください。再配布を避けるため、画像そのものと口パク差分はリポジトリに含めていません。
- スクリーンショット：`episodes/ep01/slides/hf-*.png` と `episodes/ep02/slides/hf-whisper-files.png` は Hugging Face の画面、`episodes/ep02/slides/voxtype-github.png` は GitHub の画面です。
- BGM：[魔王魂](https://maou.audio/)「[アコースティック51](https://maou.audio/bgm_acoustic51/)」（CC BY 4.0）。公開時はクレジット表記「BGM：魔王魂」が必要です。リポジトリには曲ファイルを含めていません。
- 背景写真：SankalpSasnur「[RGB desktop computer setup with keyboard and monitor](https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg)」（CC0、Wikimedia Commons）。
