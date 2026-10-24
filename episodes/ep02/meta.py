"""第2弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
CODE = "https://github.com/kusanaginoturugi/voice-input/tree/main/lite"
ARTICLE = "https://claude.ai/artifact/Bdmebajj8SxkXZtU4cznmS"
SCRIPT_DOC = "https://claude.ai/artifact/PJcRLgEeSwghav4EFVSSHE"
EP01 = "https://youtu.be/3Sk9T1VqNsg"

# サムネイル（video/make_thumbnail.py）
THUMBNAIL = {
    "number": 2,
    "color": (255, 165, 200),           # 背景の色（第2弾はピンク）
    "title": "しゃべるだけで",
    "title2": "整った文章",
    "pill": ("全部", "ローカル"),
    "metan": "met_s214",
    "zundamon": "zunmon_3019",
}


def description(chapters):
    """概要欄の文面。chapters は「0:00 見出し」の行のリスト。"""
    return "\n".join([
        "自分のパソコンだけで動く音声入力を作る、「ローカル LLM で遊ぼう」シリーズの第2弾です。",
        "whisper.cpp で声を文字にし、第1弾で立てた llama-server でフィラーや言い直しを清書して、",
        "カーソルの位置に打ち込むまでを、四国めたんとずんだもんの掛け合いで解説します。",
        "",
        "■ この動画で分かること",
        "・whisper.cpp の入手と、日本語向けのモデルの選び方（small / large-v3-turbo / medium の実測）",
        "・whisper-cli での文字起こしと、whisper-server での常駐",
        "・llama-server での清書と、thinking を切って速くする方法",
        "・シェルスクリプト 92 行の音声入力 voice-input と、改行を入れない理由",
        "",
        "■ 撮影環境",
        "Arch 系 Linux / NVIDIA GeForce RTX 4070（VRAM 12GB）/ whisper-cpp 1.9.5 / llama.cpp build 11429",
        "デモの声は、本人の声の代わりに VOICEVOX で作った音声を使っています。",
        "",
        "■ 補足：クラウドの音声入力について",
        "動画では「ふつうの音声入力は、声をサーバーへ送って文字にする」と簡単に説明しましたが、実際はサービスや端末によって違います。",
        "最近のスマホには、端末の中だけで文字にする方式（オンデバイス）が使えるものがあり、その場合は声も文字も外に出ません。",
        "サーバーで処理する場合も、送った内容を保存しないサービスがあります（Apple の音声入力は、改善のための提供を許可したときだけ保存されます）。",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ 元になった記事と台本",
        f"記事: {ARTICLE}",
        f"台本: {SCRIPT_DOC}",
        "",
        "■ 動画で解説しているスクリプト（voice-input 簡略版）",
        CODE,
        "",
        "■ 第1弾：llama-server を立ち上げよう",
        EP01,
        "",
        "■ ソースコード（台本・音声合成・動画生成）",
        REPO,
        "",
        "■ 制作",
        "台本・記事・検証・動画の組み立て: Claude Code",
        "Hugging Face と GitHub の画面の撮影: Claude in Chrome",
        "",
        "■ クレジット",
        "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん",
        "イラスト: 東北ずん子・ずんだもんプロジェクト公式素材をもとに作成",
        "BGM: 魔王魂「アコースティック51」 https://maou.audio/bgm_acoustic51/ （CC BY 4.0）",
        "背景写真: SankalpSasnur「RGB desktop computer setup with keyboard and monitor」（CC0）",
        "https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg",
        "",
        "■ 謝辞",
        "オープンソースでツールを作ってくれた皆様方。",
        "素晴らしい楽曲をクリエイティブ・コモンズで公開してくれている作曲者様。",
        "可愛い絵柄のずんだもんたちを描いてくれた絵師さん。",
        "素敵な音声合成を作っていただいた皆様。",
        "生成 AI という、とてつもなく全く新しく面白くて強力なアシスタントを作ってくれた方々。",
        "そして、動画作成のきっかけを与えてくれた友達。ありがとうございます。",
        "",
        "#ローカルLLM #whispercpp #音声入力 #ずんだもん #四国めたん #VOICEVOX",
    ])
