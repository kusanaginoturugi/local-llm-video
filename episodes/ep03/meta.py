"""第3弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
CODE = "https://github.com/kusanaginoturugi/voice-chat"
ARTICLE = "https://claude.ai/artifact/XUxWANTPfE6osvRi4zTb6U"
SCRIPT_DOC = "https://claude.ai/artifact/XVRqxtD2fCeVedg1qbSC9c"
EP01 = "https://youtu.be/3Sk9T1VqNsg"
EP02 = "https://youtu.be/k-ploGYRc_Q"

# サムネイル（video/make_thumbnail.py）
THUMBNAIL = {
    "number": 3,
    "color": (164, 222, 70),            # 背景の色（第3弾はずんだ色）
    "title": "ずんだもんと",
    "title2": "声で会話",
    "pill": ("返事まで", "0.2秒"),
    "metan": "met_s214",
    "zundamon": "zunmon_3022",
}


def description(chapters):
    """概要欄の文面。chapters は「0:00 見出し」の行のリスト。"""
    return "\n".join([
        "声で話しかけると、キャラクターが声で返事をする AI を作る、「ローカル LLM で遊ぼう」シリーズの第3弾です。",
        "第2弾の whisper.cpp で声を文字にし、第1弾の llama-server が返事を考え、VOICEVOX が読み上げます。",
        "最初に素直につないだ版から、遅い・足りないを 1 つずつ直して、返事まで約 0.2 秒になるまでを、四国めたんとずんだもんの掛け合いで解説します。",
        "",
        "■ この動画で分かること",
        "・VOICEVOX ENGINE を Docker で動かし、curl で声を作る方法",
        "・小さな LLM にキャラを演じさせるシステムプロンプトの書き方（人物像と会話の決まり）",
        "・返事を 1 文ずつ受け取って読み上げ、待ち時間を半分にする方法",
        "・VOICEVOX を GPU 版にして、声が出るまで約 0.2 秒にする方法",
        "・名前を呼んでキャラを交代する方法",
        "",
        "■ 撮影環境",
        "Arch 系 Linux / NVIDIA GeForce RTX 4070（VRAM 12GB）/ llama.cpp build 11429 / whisper-cpp 1.9.5 / VOICEVOX ENGINE 0.25.2",
        "モデル: gemma-4-E4B-it（qat）、Whisper medium",
        "デモで voice-chat に話しかける声は冥鳴ひまり（VOICEVOX）です。その声を whisper.cpp で文字にし、返事はその場で LLM が作ったものです。",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ 元になった記事と台本（GPU 版の入れ方やシステムプロンプトの全文は記事に）",
        f"記事: {ARTICLE}",
        f"台本: {SCRIPT_DOC}",
        "",
        "■ 動画で作った voice-chat",
        CODE,
        "",
        "■ これまでの回",
        f"第1弾：llama-server を立ち上げよう {EP01}",
        f"第2弾：音声入力で \"Hello, Computer ?\" しようぜ {EP02}",
        "",
        "■ ソースコード（台本・音声合成・動画生成）",
        REPO,
        "",
        "■ 制作",
        "台本・記事・検証・動画の組み立て: Claude Code",
        "",
        "■ クレジット",
        "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん / VOICEVOX:冥鳴ひまり",
        "イラスト: 東北ずん子・ずんだもんプロジェクト公式素材をもとに作成",
        "キャラクターの設定: VOICEVOX「ボイボ寮」、東北ずん子・ずんだもんプロジェクト公式サイト",
        "BGM: 魔王魂「アコースティック51」 https://maou.audio/bgm_acoustic51/ （CC BY 4.0）",
        "背景写真: SankalpSasnur「RGB desktop computer setup with keyboard and monitor」（CC0）",
        "https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg",
        "",
        "■ ひとこと",
        "動画の最後で冥鳴ひまりさんが「出番が少ない」と乱入していますが、本当に出番がなかったのは春日部つむぎさんです。",
        "voice-chat のキャラとして用意して、キャラの交代で名前まで出したのに、一度もしゃべっていません。つむぎさん、ごめんなさい。",
        "",
        "■ 謝辞",
        "オープンソースでツールを作ってくれた皆様方。",
        "素晴らしい楽曲をクリエイティブ・コモンズで公開してくれている作曲者様。",
        "可愛い絵柄のずんだもんたちを描いてくれた絵師さん。",
        "素敵な音声合成を作っていただいた皆様。",
        "生成 AI という、とてつもなく全く新しく面白くて強力なアシスタントを作ってくれた方々。",
        "そして、動画作成のきっかけを与えてくれた友達。ありがとうございます。",
        "",
        "#ローカルLLM #VOICEVOX #ずんだもん #四国めたん #llamacpp #whispercpp",
    ])
