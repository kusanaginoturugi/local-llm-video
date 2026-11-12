"""第5弾の概要欄とサムネイル。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
NDLOCR = "https://github.com/ndl-lab/ndlocr-lite"
BOOK = "https://dl.ndl.go.jp/pid/1170887"
AOZORA = "https://www.aozora.gr.jp/cards/001779/card58053.html"
YOMITOKU = "https://github.com/kotaro-kinoshita/yomitoku"
ARTICLE = "https://claude.ai/artifact/QaLfsP48pZJ9tTHoK1QNLQ"

THUMBNAIL = {
    "number": 5,
    "color": (255, 214, 102),
    "title": "スキャンした本を",
    "title2": "検索できるPDF",
    "pill": ("GPUで", "1冊1分"),
    "metan": "met_s222",
    "zundamon": "zunmon_3019",
}


def description(chapters):
    return "\n".join([
        "『ローカル LLM で遊ぼう』第5弾。国立国会図書館の NDLOCR-Lite で、スキャンした本の PDF に透明な文字を重ね、",
        "検索できる PDF にします。手順は最低限（入れて、フォルダを作って、コマンド一本）だけを紹介します。",
        "CPU だけでも動きますが、GPU（RTX 4070）なら文庫 1 冊が約 1 分。精度の答え合わせもしました。",
        "",
        "■ 解説記事（手順・コマンド・計測の条件）",
        ARTICLE or "（公開準備中）",
        "",
        "■ かかった時間（NDLOCR-Lite v1.4.0、300dpi、2026-11-12〜13）",
        "文庫 356 ページ：CPU（Core i5-13400F）約 6 分（356.7 秒）、GPU（RTX 4070、--device cuda）1 分 8 秒（67.5 秒）",
        "一寸法師 208 コマ（見開きの写真）：CPU 4 分 55 秒、GPU 1 分 45 秒",
        "動画の CPU と GPU の画面は、実際の実行で端末に出た文字を時刻どおりに再生したものです（5 倍速）。",
        "GPU では onnxruntime を onnxruntime-gpu[cuda,cudnn]==1.31.1 に入れ替えています。",
        "",
        "■ 答え合わせ（正解率 約 99.4%）",
        "OCR の結果を青空文庫の『一寸法師』と 1 文字ずつ突き合わせました。青空文庫は新字・新かなに直した全集が底本なので、",
        "本の中で何度も出てくる置き換え（賣→売、ゐ→い など）は表記の違いとして外し、残りから 40 か所と、",
        "表記の違いに紛れていた怪しい置き換え 36 か所を、元の画像で確かめて見積もりました。",
        "句読点は数えていません。標本が小さいので、幅を持たせて 99.1〜99.7% くらいと見てください。",
        "紙を白くしてから OCR にかけると、この本ではかえって誤りが増えました（誤りの候補 628 → 1,443 か所）。",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ この動画で使ったもの",
        f"NDLOCR-Lite v1.4.0（国立国会図書館、CC BY 4.0）: {NDLOCR}",
        "デモの本: 江戸川亂歩『一寸法師』（亂歩傑作選集 第4卷、平凡社、1935）",
        f"国立国会図書館デジタルコレクション（保護期間満了）: {BOOK}",
        f"答え合わせ: 青空文庫『一寸法師』（底本 光文社文庫『江戸川乱歩全集 第2巻』、入力 nami、校正 まつもこ）: {AOZORA}",
        f"制作者の本番で使っている、もう一つの OCR（YomiToku）: {YOMITOKU}",
        "制作者の自炊本は書名・ページ数・時間だけを紹介し、ページの画像や本文は出していません。",
        "自炊した本の PDF は、自分で使う分だけにしてください。",
        "",
        "■ リンク",
        f"台本・計測スクリプト・答え合わせのスクリプト: {REPO}/tree/main/episodes/ep05",
        "",
        "■ これまでの回",
        "第1弾：llama-server を立ち上げよう https://youtu.be/3Sk9T1VqNsg",
        "第2弾：音声入力で Hello, Computer? https://youtu.be/k-ploGYRc_Q",
        "第3弾：声で会話するローカル AI",
        "第4弾：0.8B で爆速ページ翻訳（シリーズの前回）",
        "",
        "■ 制作",
        "台本・記事・検証・動画の組み立て: Claude Code（Claude Opus 5.5）",
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
        "#ローカルLLM #OCR #NDLOCR #自炊 #ずんだもん #四国めたん #VOICEVOX",
    ])
