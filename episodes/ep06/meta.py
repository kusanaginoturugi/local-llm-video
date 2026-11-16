"""第6弾の概要欄とサムネイル。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
KINDLE_JA = "https://github.com/kusanaginoturugi/kindle-ja"
TRANSLATOR = "https://github.com/kusanaginoturugi/offline-browser-translate"
PLAMO = "https://huggingface.co/pfnet/plamo-3-translate-0.8b-GGUF"
RAPIDOCR = "https://github.com/RapidAI/RapidOCR"
PADDLEOCR = "https://github.com/PaddlePaddle/PaddleOCR"
TESSERACT = "https://github.com/tesseract-ocr/tesseract"
ALICE = "https://www.gutenberg.org/ebooks/19002"
ARTICLE = ""

THUMBNAIL = {
    "number": 6,
    "color": (150, 210, 255),
    "title": "Kindleの英語の本を",
    "title2": "手元のLLMで読む",
    "pill": ("1画面", "1.5秒"),
    "metan": "met_s222",
    "zundamon": "zunmon_3022",
}


def description(chapters):
    return "\n".join([
        "『ローカル LLM で遊ぼう』第6弾。Kindle で買った英語の本を、手元の LLM で訳して読みます。",
        "Kindle Cloud Reader はページの中に文字がないので、翻訳の拡張は効きません。そこで画面を 1 画面ずつ OCR して、",
        "手元の LLM で訳し、Emacs に足していく kindle-ja を作りました。本の鍵（DRM）は外しません。",
        "最初は 1 画面 約 8 秒。翻訳を PLaMo 3 Translate 0.8B に、OCR を GPU の RapidOCR に替えて、1 画面 約 1.5 秒になりました。",
        "訳を VOICEVOX で読み上げることもできます。",
        "",
        *(["■ 解説記事", ARTICLE, ""] if ARTICLE else []),
        "■ kindle-ja（スクリプト・計測・使い方）",
        KINDLE_JA,
        "訳は普通のテキストファイル（Org）に足していくだけなので、Emacs 以外のエディタでも読めます。",
        "表示の部分は、自分のコーディングエージェントに頼んで書き換えてください。",
        "",
        "■ 1 画面の時間（Kindle Cloud Reader の Chapter I の冒頭、見出しと本文 約 360 語、Ryzen 7 3700X、RTX 3060 12GB、llama.cpp v0.9.0）",
        "最初の版（tesseract ＋ Gemma 4 E4B）：約 8 秒（OCR 1.3 秒、翻訳 7.0 秒）",
        "Gemma 4 12B：約 15 秒（E4B と同時には VRAM に載らない）",
        "翻訳を PLaMo 3 Translate 0.8B に：約 2.1 秒（翻訳 0.9 秒）",
        "OCR も GPU の RapidOCR（常駐）に：約 1.5 秒（OCR 0.5 秒）",
        "3 回ずつ測った値（モデルを読み込んだあと）。動画の実録は 1 回分です（最初の版は 2 倍速）。",
        "",
        "■ OCR の比べ（Kindle の画面 1 枚、tesseract（2 倍に拡大）と単語が食い違った数）",
        "PaddleOCR 3.7 本体（PP-OCRv6 medium、GPU、拡大なし）：0.49 秒、食い違い 0（環境は Python 3.12 込みで約 10GB）",
        "RapidOCR 3.10（PP-OCRv6 small、GPU、2 倍に拡大）：0.57 秒、食い違い 0（約 2.7GB）。kindle-ja はこちら",
        "比べに使った画面は制作者が買った本なので、動画には出していません。",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ この動画で使ったもの",
        "デモの本: Lewis Carroll『Alice's Adventures Under Ground』（地下の国のアリス。1864 年の手書き本を 1886 年に複製したもの、保護期間満了。Kindle の 0 円の版）",
        f"同じ本の Project Gutenberg 版: {ALICE}",
        f"PLaMo 3 Translate 0.8B（Preferred Networks）: {PLAMO}",
        f"RapidOCR: {RAPIDOCR}",
        f"PaddleOCR: {PADDLEOCR}",
        f"tesseract: {TESSERACT}",
        f"Local LLM Translator（第4弾の拡張、制作者のフォーク）: {TRANSLATOR}",
        "制作者が買った本（同じ題名の一幕劇、本命の本）は、ページや本文を出していません。",
        "Kindle の本は、自分の画面で読む分だけにしてください。訳した Org ファイルも人に渡さないでください。",
        "",
        "■ リンク",
        f"台本・演出・計測のメモ: {REPO}/tree/main/episodes/ep06",
        "",
        "■ これまでの回",
        "第1弾：llama-server を立ち上げよう https://youtu.be/3Sk9T1VqNsg",
        "第2弾：音声入力で Hello, Computer? https://youtu.be/k-ploGYRc_Q",
        "第3弾：声で会話するローカル AI",
        "第4弾：0.8B で爆速ページ翻訳 https://youtu.be/TUADm3MbcKE",
        "第5弾：スキャンした本を検索できる PDF に",
        "",
        "■ 制作",
        "台本・検証・kindle-ja・動画の組み立て: Claude Code（Claude Opus 5.5）",
        "",
        "■ クレジット",
        "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん / VOICEVOX:春日部つむぎ",
        "イラスト: 東北ずん子・ずんだもんプロジェクト公式素材をもとに作成",
        "春日部つむぎSD立ち絵: 公式イラストを参考に生成・編集（原案 KASUKABEproject／春日部つくし）",
        "https://kasukabe294.booth.pm/items/3474402",
        "BGM: 魔王魂『アコースティック51』 https://maou.audio/bgm_acoustic51/ （CC BY 4.0）",
        "背景写真: SankalpSasnur『RGB desktop computer setup with keyboard and monitor』（CC0）",
        "https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg",
        "",
        "#ローカルLLM #Kindle #OCR #PLaMo #ずんだもん #四国めたん #VOICEVOX",
    ])
