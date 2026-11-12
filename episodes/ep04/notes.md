# 第4弾 制作メモ

## Microsoft Learn の訳文比較（2026-11-12 完了）

- `CommandDescription.Help` の日本語ページは「コマンドのストリングを助けて。」。英語版の原文は `Help string for the command.`。隔離 Chromium に拡張を読み込み、英語版の実ページを PLaMo 3 Translate 0.8B で翻訳すると「コマンドのヘルプ文字列。」となった。翻訳後の DOM の該当段落には拡張が付けた `data-translated="true"` があり、完了表示は `368/368 elements (100%)`。英語版の一文だけを同じモデルの API に別途送った場合は「コマンドの文字列を補完してください。」で、文脈や拡張の分割により結果が変わる。常に良訳になるという主張はしない。
- 日本語版と翻訳後の静止画は `slides/mslearn-ja.png`、`slides/mslearn-plamo.png`。英語原文の画面は `slides/mslearn-en.png`。実録は `demo/mslearn-plamo-raw.mkv`、再録可能な手順は `demo/capture_mslearn.sh`。拡張のキャッシュはオフ、Custom 形式、1件ずつ、温度0。進捗は画面右上に移した。
- 見せ方の軸は「翻訳済みのページを読んでも意味が通らず、原文へ戻って確認する面倒さ」。日本語ページ→英語原文→PLaMo で翻訳する実画面→訳文比較の順にした。Google 翻訳の `man cat`→「男猫」は、2026-11-12 にブラウザ画面でも再現して `slides/google-man-cat.png` に保存。別の文脈なし短文例として扱い、同じページや同条件の比較に見せない。解説サイトには実画面、原文、各訳文、出典を並べた。

## 今回の見せ方

- 冒頭はタイトルを出して二人が話し始めた直後に、つむぎが怒り顔で中央へ割り込む。締めの直後にも再乱入する。SD立ち絵は春日部つむぎ公式イラストを参考に imagegen で作成し、既存の二人と顔の大きさを画面で合わせた。表情は怒り・笑顔の2枚。素材は再配布せず `assets/official/tsumugi-sd-angry.png` と `assets/official/tsumugi-sd-happy.png` に置く。
- 主題は Local LLM Translator によるページ翻訳と、PLaMo 3 Translate 0.8B Q4_K_M の短文翻訳速度。
- 四国めたんは前回の予告どおり第4弾からタメ口。冒頭でずんだもんが戸惑い、終盤でもその変化に触れる。
- 翻訳品質は、PFN の図13が示す比較対象・評価範囲と、制作者の TranslateGemma 12B→4B、Hy-MT2→PLaMo 0.8B という使用感を分けて扱う。「man cat」→「男猫」は過去に困った誤訳の例であり、今回のモデル間で同一条件の比較実験をした結果ではない。
- 公式の比較図は PFN の記事の図13をそのまま表示する。画像の取得元は `assets/fetch_official.sh` に記録し、画面と概要欄で出典を示す。比較図の範囲は言語ペアごとに異なるため、全言語で優位とは言わない。
- モデル一覧の容量は手元の GGUF Q4_K_M ファイルの実サイズを十進 GB に丸めた。TranslateGemma 12B 7,300,794,112 バイト（約7.30 GB）、TranslateGemma 4B 2,489,909,760 バイト（約2.49 GB）、Hy-MT2 **7B** 4,624,650,016 バイト（約4.62 GB）、PLaMo 0.8B 573,126,848 バイト（約0.57 GB）。
- 拡張の設定画面はユーザー提供の画像 `slides/plamo-custom-settings.png`。`slides/translator-popup.png` は拡張のリポジトリにあるプレビュー画像。
- 動画では速度を数値で説明せず、TranslateGemma 12B の実画面のあとに PLaMo 0.8B の実画面を等速で見せ、ずんだもんの「速すぎてわからない」という反応から4倍スローにつなぐ。API 実測値、生成速度、速度の理由は解説ページに置く。
- 拡張の実画面も別途録画した。同じ縦長の自作記事（77要素）を PLaMo 0.8B と TranslateGemma 12B Q4_K_M で訳す。両方 RTX 4070 に全層オフロード、キャッシュ無効、同時リクエスト1件。12B は冒頭を静止させてからゆっくりスクロールし、PLaMo は等速のあと同じ録画を4倍スローで見せる。進捗表示を記事の右上に移し、ブラウザ標準翻訳の表示が混じらないよう記事部分を切り出す。

## 計測

- 2026-11-10、RTX 4070 12GB、Core i5-13400F。モデルは `pfnet/plamo-3-translate-0.8b-GGUF` の `Q4_K_M`（573,126,848 バイト）。
- PLaMo 対応のローカル `llama.cpp` ビルドを使用。ディストリビューションの `llama-server` は `unknown tokenizer: 'plamo3'` で読み込めなかった。
- 視聴者向けの入手手順は第1弾と同じ `llama-server -hf pfnet/plamo-3-translate-0.8b-GGUF:Q4_K_M` に統一する。対応ビルドの `llama-server --help` で `-hf` と量子化指定を確認。起動時に Hugging Face から自動取得するため、別の `hf download` は不要。
- GPU は全層オフロード。サンドボックス内からは NVIDIA ドライバが見えなかったため、サーバーを許可済みのサンドボックス外実行で起動した。GPU は `nvidia-smi` で RTX 4070 と確認。
- `demo/benchmark.py` は 6 種の英文を逐次翻訳。初回を除く 5 文の API 応答時間の中央値を表示。GPU `0.046秒/文`（5 文合計 `0.231秒`）、CPU `0.327秒/文`。入力文と返答、各時間は `results-gpu.json` と `results-cpu.json` に保存。
- `demo/results.json` の GPU 生成速度は測定対象5件で約505〜518 tokens/秒。モデルが小さいと重みの読み出し量と計算量を抑えやすいが、速度は GPU、量子化、実装、入出力長にも左右される。これを解説ページで説明する。
- 送信形式は拡張の Custom 設定に寄せた。system は `[plamo-translate]\ntarget_lang=ja`、user は `[0]: 英文`。`temperature=0`。モデル読み込みとブラウザの分割・DOM 書き換えは時間に含めない。結果の品質は短い例での確認に限る。
- 最初に測った通常の API 形式と、CPU が別作業と競合していたときの値は `results-api-gpu.json` と `results-api-cpu.json` に残す。動画では使わない。

## 拡張の設定と確認

- Provider は `LMStudio / OpenAI-compatible`、URL は `http://127.0.0.1:8000`、対象モデルは PLaMo。
- Request Format は `Custom`、User Prompt は `{{texts}}`。`Use structured JSON output` をオフ、`Max Items per Batch` を `1` にする。
- 英語→日本語は System Prompt 空欄でも PLaMo の自動判定で動く。翻訳先を明示するときは `[plamo-translate]` の次行に `target_lang={{targetCode}}`。拡張の targetLanguage の選択は、変数をプロンプトに入れなければモデルに届かない。
- 拡張のコードでは `Custom` は plain-text 専用扱いではないが、JSON 出力をオフにし 1 件ずつ送ると、PLaMo の `[0]: 訳文` を単一項目として解析できる。実際の API に拡張と同形のリクエストを送り、構造化 JSON 指定ありでは `{"translations": []}`、なしでは `[0]: 今朝荷物が届きました。` が返ることを確認した。
- 2026-11-11 に隔離 Chromium へ fork の unpacked 拡張を読み込み、`demo/browser-article.html` を両モデルで実際に翻訳した。長い記事の生録画は `demo/browser-plamo-long-raw.mkv` と `demo/browser-translategemma12b-long-raw.mkv`。`demo/capture_browser.sh` が起動・録画・完了待ち・スクロールを行う。両方全層 GPU、キャッシュ無効、1件ずつ。PLaMo は Custom 形式、12B は TranslateGemma 専用形式を使う。ブラウザ画面の録画は体感デモであり、モデル速度の厳密な比較値ではない。
- `man cat`→`男猫` は Google 翻訳の応答で 2026-11-11 に再現した（下記の再現リンクと翻訳応答 API）。元の文脈がない短い入力なので、PLaMo との品質比較の根拠には使わない。別の現行の誤訳例として Microsoft Learn の `Help string for the command.`→「コマンドのストリングを助けて。」を英日両ページで確認した。Firefox / Chrome の実画面比較は第三者の2026年の記事で確認し、自分の環境では再現実験をしていない。
- 読みの見直しで `タメ口`→`タメグチ`、モデル名・小数の読みを辞書に追加。`二重波括弧 texts` は台詞を言い換え、最後の `同じ文` は `さっきの英文` に変更して誤読を避けた。

## 参照

- PLaMo のモデルカード・起動方法・翻訳指定・ライセンス: https://huggingface.co/pfnet/plamo-3-translate-0.8b-GGUF
- PFN の翻訳品質比較（図13）: https://www.preferred.jp/ja/blog/tech/plamo-3-translate-weight-release
- 拡張の上流コードと使い方: https://github.com/Eldoprano/offline-browser-translate
- 制作時に参照した fork: https://github.com/kusanaginoturugi/offline-browser-translate
- Google 翻訳の `man cat` 再現リンク: https://translate.google.com/?sl=en&tl=ja&text=man%20cat&op=translate
- 同じ入力の翻訳応答 API: https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=man%20cat
- Microsoft Learn 英語: https://learn.microsoft.com/en-us/dotnet/api/microsoft.bot.builder.formflow.commanddescription.help?view=botbuilder-dotnet-3.0
- Microsoft Learn 日本語: https://learn.microsoft.com/ja-jp/dotnet/api/microsoft.bot.builder.formflow.commanddescription.help?view=botbuilder-dotnet-3.0
- Firefox / Chrome の同一ページ翻訳の実画面: https://laboradian.com/?p=43617
