# 第6弾のメモ：Kindle の英語の本を、ローカル LLM で訳して読む

## 方針（2026-11-16）

- 題材は [kindle-ja](https://github.com/kusanaginoturugi/kindle-ja)。Kindle Cloud Reader の画面を 1 画面ずつ取り込み、OCR してローカル LLM で訳し、Emacs で読む。
- 経緯（制作者の実話。台本ではめたんの話にする）：
  1. Yudkowsky と Soares の *If Anyone Builds It, Everyone Dies*（超知能 AI の危険を論じた本）を読もうとした。
     セールをやっているという情報があり、探したら英語版が安く出ていた。日本語版は検索に出てこなかった。
  2. 英語版だと分かって買った（制作者：「英語版だというのはわかってて買った」）。第4弾のブラウザ拡張（Local LLM Translator）があれば、英語でも読めると思った。
  3. その拡張で訳そうとしたが、何も訳されない。ページ内検索で本文の単語がヒットしない。
     しかも買ったのは、同じ題名を借りた別の本（短い一幕劇）だった（「まさか全然違う本だとは思わなかった」）。気づいたのは、ツールを作って試しているとき。
  4. 画面を OCR して訳すツールを作った（Claude Code と、2026-11-16 の昼すぎまでの半日）。
  5. 本命は、結局日本語版の紙の本を買った（あとで探したら日本語版があった）。理由（制作者）：
     - 話題の本なので、回し読みしてみんなで共有したい。日本の Kindle は人に貸すことができない。
     - Kindle は実質的にはレンタルで、所有できない。「レンタルなのに物理本と同じ（値段）って商売としてどうかとおもう」。
     - 「やっぱり翻訳の質が微妙だから、ちゃんとした訳で読む」。
     台本では、めたんの意見として言わせる（Kindle の本は売買ではなく利用の許諾、という点は事実。値段の比べは一般論にとどめる）。
- 画面に出す本は、著作権の切れた英語の本だけ。間違えて買った一幕劇は著作権があるので、ページ・本文・作者名を出さない。
  「同じ題名の別の本」とだけ言い、けなさない。本命の本も引用しない（書名と、どういう本かだけ）。
- デモの本：*Alice's Adventures in Wonderland*（Lewis Carroll、1865、保護期間満了）。Kindle では無料の版がある。
  計測は Project Gutenberg の本文（eBook #11）で作ったページ画像で行った（下）。動画の画面は、Cloud Reader で無料版を開いて撮る（未撮影）。
- 撮るときは、タブやパネルが写らないよう、本文とアドレスバーより下だけにする（第5弾と同じ）。
- DRM は外さない。1 回のキー操作で 1 画面だけ。自分で買った本を、自分の画面で読むための道具、という線を守る。

## この PC

- AMD Ryzen 7 3700X（16 スレッド）、NVIDIA GeForce RTX 3060（VRAM 12GB）。第1〜5弾の RTX 4070 の PC とは別。
- llama.cpp はソースからビルドした v0.9.0（cd959ba、CUDA、`~/src/oss/llama.cpp-runtime`）。`--models-max 2`。
- `gemma-4-E4B-it-qat` は音声入力（voice-input）用に常駐（`sleep-idle-seconds = -1`、ctx 32768 × 2）。
- tesseract 5.5.4（英語、CPU のみ）、ImageMagick、grim / slurp、Hyprland、kitty、emacs-nox 31.1。

## Cloud Reader は本文が DOM にない（2026-11-16）

- Local LLM Translator（第4弾の拡張のフォーク）で Cloud Reader のページを訳そうとしても、何も訳されない。
- Firefox で、画面に見えている英単語を Ctrl+F で探してもヒットしない（制作者が確認）。拡張は DOM のテキストを訳すので、どう直しても訳せない。

## kindle-ja の流れ

1. `SUPER + Y` で、`grim` が画面の決まった範囲（`148,197 1000x1112`）を取り込む。範囲は `SUPER + SHIFT + Y`（`kindle-ja --select`）で選び直せる。
2. ImageMagick でグレーにして 2 倍に拡大し、tesseract（英語）で OCR。
3. 行末のハイフンをつなぎ、行を段落にまとめる。
4. llama-server の OpenAI 互換 API に送って訳す（既定は `gemma-4-E4B-it-qat`）。
5. Org ファイルに、見出し（日時）・原文の quote ブロック・訳の順で追記する。
6. kitty の `emacs -nw` で開く。追記を `auto-revert-mode` で読み直し、原文を畳んで、新しい見出しを窓の先頭に出す。

## 作っている途中で出た問題

- 最初は範囲をマウスで選んでいた → 毎回同じ範囲なので固定にした。スクショを画素で突き合わせて位置を決めた。
- 範囲に左のページ送りボタン「<」が入って、OCR が `/\` と読んだ → 本文の幅に狭めた。
- 拡大しないと、`I` を `1` と読んだ → 2 倍に拡大して読ませる（拡大しないほうが 0.2 秒速い）。
- tesseract は、段落の途中に空行を入れたり、段落の間に空行を入れなかったりする。戯曲の話者名（全部大文字の行）がト書きにくっついた
  → 段落の規則を作った（短い行のあとで切る、空行は文末記号のあとだけ、全部大文字の行は 1 行で 1 段落、行末ハイフンはつなぐ）。
- Emacs が追記のたびに末尾へ飛び、新しい訳の頭が画面の外に出た（`auto-revert-tail-mode`） → 新しい見出しを窓の先頭に置き、原文は畳む。
- 12B（`gemma-4-12b-it-qat-imatrix`）を既定にしていたら、E4B が載っているときに読み込めず、`cudaMalloc failed: out of memory` で API が 500 を返した
  → 既定を E4B にした。12B に切り替えるなら `~/.config/kindle-ja/model`。
- OCR を GPU にできないか → tesseract は CPU だけ。OCR は 1 ページ約 1.3 秒で、時間のほとんどは翻訳。GPU の OCR にしても縮むのは 1 秒ほどで、VRAM を LLM と取り合う。

## 計測（2026-11-16、*Alice* の第 1 章冒頭 253 語のページ画像）

ページ画像は Gutenberg の本文を Liberation Serif 21pt、幅 960px で描いたもの（1000x626）。`grim` だけスタブにして、ほかは本物で通した。

| 処理 | 時間 |
| --- | --- |
| 拡大 + OCR（tesseract、CPU） | 1.28 秒 |
| 1 ページ全体（E4B、3 回） | 5.60 / 5.56 / 5.54 秒（翻訳は約 4.3 秒） |
| 1 ページ全体（12B、3 回、E4B を降ろして） | 13.60 / 10.72 / 10.75 秒（1 回目は読み込みを含む） |
| 1 ページ全体（PLaMo 3 Translate 0.8B、3 回、E4B と同時に載せたまま） | 4.44 / 1.99 / 1.94 秒（1 回目は読み込みを含む。翻訳は約 0.65 秒） |

訳の比べ（同じページ）：

- E4B：読めるが、誤字（「うんざかり」）や、ぎこちない文（「見たことが一度もなかったという事実が閃いた」）がある。
- 12B：自然（「チョッキ」「〜かしら」）。ただし「Oh dear! Oh dear!」の繰り返しが 1 回に減っていた。
- PLaMo：「Oh dear! Oh dear!」を「あらまあ！ あらまあ！」と 2 回とも訳す。ただし川の土手の bank を「銀行」と訳した（2 回とも同じ）。waistcoat は「ウェストコート」のまま。
- どれも、一冊を通して読むには人の訳に及ばない、というのが制作者の結論。

## シリーズのつながり（AGENTS.md の確認）

- 第5弾の締め：つむぎ「言質とったからね。次回もよろしく」→ めたん「それも、考えとく」。第6弾も、つむぎは最初からいる。
- 第4弾の拡張（Local LLM Translator）が、今回は訳せない側で出てくる。
- 第5弾の OCR（NDLOCR-Lite は日本語用）。今回は英語なので tesseract。
- ずんだもんの「LLM はないがしろにされる仲間」（第5弾）。今回は時間のほとんどが LLM で、主役に戻る。でも最後は日本語版に負ける。
- めたんは「常に金欠」（公式）。セールの安さに乗った理由にする。英語版と分かって買った、という事実は変えない（初稿では「値段しか見ずに買ったら英語だった」にしていたが、制作者の指摘で直した）。

## PLaMo に切り替えた（2026-11-16）

- 台本の初稿を見た制作者：「plamo-3-translate-0.8b を使うべきだった」。第4弾の主役なのに、kindle-ja を作るときは会話モデル（E4B）で訳していた。
- kindle-ja の既定を `plamo-3-translate-0.8b` にした（kindle-ja f39f18a）。PLaMo の chat template は先頭の system を無視し、
  翻訳先を `chat_template_kwargs.target_lang` で受け取る（既定は ja）。kindle-ja は `target_lang=ja` を付けて送る。
- PLaMo と E4B は同時に VRAM に載る（両方 loaded を確認）。12B と違って、音声入力の E4B を降ろさなくていい。
- PLaMo にすると 1 画面 1.95 秒のうち OCR が 1.3 秒で、時間の大半は OCR に戻る。

## OCR も GPU に（2026-11-16）

PLaMo にすると、1 画面 1.95 秒のうち tesseract の OCR（拡大込み）が 1.3 秒になった。制作者：「plamo-3-translate が軽いから、PaddleOCR でいけるんじゃないかな？」
「PaddleOCR は日本語でダメだったから汚名返上の機会をあたえたい」。

- 前振り（bookscan-epub の記録）：自炊本（日本語・縦書き）で PaddleOCR 3.7.0 の PP-OCRv6 を NDLOCR-Lite と突き合わせたら、句読点・括弧の脱落が多かった。
  目視で比べた範囲に、PaddleOCR が本文の正答を補った箇所はなく、本文の候補から外して参考表示にした（bookscan-epub/docs/progress.md）。
- PaddlePaddle は Python 3.14 向けの wheel がない（CPU 版も GPU 版も）。uv で Python 3.12 を入れ、paddlepaddle-gpu 3.4.0（cu129）と paddleocr 3.7.0 で試した。環境は約 10GB。
  最初は uv が PyPI の paddlepaddle-gpu 2.6.2 を拾った（`--index-strategy unsafe-best-match` で 3.4.0 に）。/tmp（tmpfs）に入れようとして容量が尽きたので、ディスクに置き直した。試したあと消した。
- RapidOCR 3.10.0（PaddleOCR のモデルを onnxruntime で動かす）は、システムの Python 3.14 に onnxruntime-gpu[cuda,cudnn] 1.31.1 で入る（約 2.7GB）。既定のモデルは PP-OCRv6 small（多言語、英語も日本語も）。

同じ Kindle の画面（制作者が買った一幕劇のスクショ、1000x1112。手元の比べにだけ使い、動画には出さない）。2 回目以降の時間と、tesseract（2 倍）と単語が食い違った数：

| OCR | 画像 | 1 ページ | 食い違い |
| --- | --- | --- | --- |
| tesseract 5.5.4（CPU） | 2 倍 | 約 0.9 秒（＋拡大 0.2〜0.4 秒） | 基準 |
| RapidOCR PP-OCRv6 small（GPU） | 等倍 | 0.43 秒 | 10（made! → madel、AGI → AGl、alignment → alignmnent など） |
| RapidOCR PP-OCRv6 small（GPU） | 2 倍 | 0.57 秒 | 0 |
| RapidOCR PP-OCRv6 medium（GPU） | 等倍 | 0.51 秒 | 5 |
| RapidOCR PP-OCRv6 medium（GPU） | 2 倍 | 0.81 秒 | 0 |
| PaddleOCR 3.7.0 本体 PP-OCRv6 medium（GPU） | 等倍 | 0.49 秒 | 0 |
| PaddleOCR 3.7.0 本体 PP-OCRv6 medium（GPU） | 2 倍 | 0.77 秒 | 0 |

- アリスの合成ページでは、tesseract も RapidOCR も Gutenberg の原文と単語の食い違い 0（きれいすぎて差が出ない）。
- PaddleOCR 本体の初期化は 2.6 秒（初回はモデルのダウンロード込みで 19 秒）。GPU メモリは確保の最大 756MB（auto_growth）。
- RapidOCR の初回は cuDNN の探索で 1.6〜2.3 秒。`cudnn_conv_algo_search` を `HEURISTIC` にすると初回 0.68 秒で、2 回目以降は同じくらい。`DEFAULT` は Fallback になって遅い。
- 制作者は RapidOCR を選んだ（軽いから）。kindle-ja に、常駐の OCR サーバー `kindle-ja-ocrd`（RapidOCR small、2 倍に拡大、127.0.0.1:8093、10 分使われなければ終了）を足した（kindle-ja 9d567b9）。
  段落は行の中心の間隔で決める（Kindle は段落の間を少し広く空ける：2 倍で 65〜67 に対して 74〜83）。tesseract は予備。
- 全部本物で通すと（grim だけスタブ、Alice のページ、PLaMo）：1 回目 5.44 秒（OCR サーバーの起動込み）、2 回目以降 1.03 / 0.98 / 1.00 秒。

## 録画の予定（未撮影）

- Cloud Reader で無料版のアリスを開き、第 1 章の冒頭のページを出す。本文とアドレスバーより下だけを撮る。
- 1 本目：最初の版（`KINDLE_JA_OCR=tesseract`、モデル `gemma-4-E4B-it-qat`）で `SUPER + Y` → Emacs に訳が出るまで（6 章「5.6 秒」）。
- 2 本目：PLaMo ＋ tesseract（9 章「一画面 1.9 秒」）。
- 3 本目：今の版（OCR サーバー ＋ PLaMo）（10 章「一画面 1.0 秒」）。OCR サーバーは先に起こしておく。

## 読み（2026-11-16、VOICEVOX 0.25.2 の audio_query で確認）

- 辞書なしでも読めた：Emacs（イーマックス）、Baidu（バイドゥ）、PaddleOCR、RapidOCR、tesseract（テセラクト）、Kindle、PC、AI、一画面、言質、金欠、綴り。
  読みを固定し、字幕で最初に読みを添えるために `dict.tsv` に入れた（annotate=yes）。tesseract は「テッセラクト」にした。
- 辞書で直した：E4B（イーヨンビー → イーフォービー）、RTX 3060（サンゼンロクジュウ → サンマルロクマル）、Oh dear（オー、エイチ、ディアー → オーディア）、
  本の題名（アニョン、エヴェリョオネ → カタカナで指定）、一幕劇（ひとまくげき → イチマクゲキ）、kindle-ja（キンドル、ジャ → キンドル、ジェーエー）。
- 「訳は」「訳が」「訳で」を「わけ」と読む。辞書で「訳」を置き換えると「翻訳」も壊れるので、direction.tsv の yomi で行ごとに直す（行番号は 2026-11-16 の台本）：
  - 32「訳は、Emacs に…新しい訳が上に来る」：`訳は=ヤクワ;訳が=ヤクガ;上に=ウエニ`（「上に」を「じょうに」と読む）
  - 36「訳はファイルに…」、64「訳は、たしかに自然」、93「訳はちゃんと…」、118「訳は翻訳専用の…」：`訳は=ヤクワ`
  - 114「ちゃんとした訳で…」：`訳で=ヤクデ`
  - 66「翻訳が止まる」は「ホンヤクガ」と読めているので何もしない（「訳が」を置き換えると壊れる）。
- 12GB は audio_query の kana で「ジュウ/ニギガバイト」と出るが、「/」は抑揚の区切りで、音は「じゅうにギガバイト」。

## 読み上げ（2026-11-16）

- 制作者：「けっこう軽くできたね。これから VOICEVOX に話させるのもできそうだ」「やろう。ネタの出し惜しみはなしだ」。
- kindle-ja-say（kindle-ja c8f5b6e）：訳を文に分け、1 文目を流しているあいだに次の文を合成して pw-play で流す。次のページで前の読み上げを止める。
  `~/.config/kindle-ja/voice` に「話者ID 速さ」。制作者の設定は `3 1.18`（ずんだもん、シリーズと同じ 1.18 倍）。止めるキーは `SUPER + CTRL + Y`。
- この PC の VOICEVOX ENGINE は Docker の `voicevox/voicevox_engine:cpu-latest`（CPU、127.0.0.1:50021）。GPU 版は自宅の PC だけ（制作者）。
  CPU でも合成は再生の約 5 倍の速さ（43 字で合成 1.53 秒・音 7.5 秒、123 字で 3.87 秒・21.3 秒、ずんだもん）。
- kindle-ja から通しで（OCR サーバー・PLaMo・VOICEVOX は本物、再生だけ記録に差し替え）：訳を書き終えてから 1 文目が鳴るまで約 1.4 秒。
- 台本 12 章のずんだもんの読み上げの行は、実際に kindle-ja-say が読んだ 1 文目（PLaMo の訳）と同じ文。
