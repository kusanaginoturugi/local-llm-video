"""第1弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
ARTICLE = "https://claude.ai/code/artifact/2be896e8-2ab9-4dd7-bf05-cff1beb45e71"
SCRIPT_DOC = "https://claude.ai/code/artifact/45ace86b-536a-4dd5-a09a-cb9db2f17fa1"

# サムネイル（video/make_thumbnail.py）
THUMBNAIL = {
    "badge": "第1弾",
    "title": "llama-server",           # 1 行目（黄色・大きく）
    "title2": "を立ち上げよう！",        # 2 行目
    "sub": "2 モデル常駐・切り替え一瞬・OOM 対策",
    "metan": "met_s214",                # 左に置くめたんの SD 絵
    "zundamon": "zunmon_3022",          # 右に置くずんだもんの SD 絵
}


def description(chapters):
    """概要欄の文面。chapters は「0:00 見出し」の行のリスト。"""
    return "\n".join([
        "自分のパソコンで LLM（大規模言語モデル）のサーバーを立ち上げる、「ローカル LLM で遊ぼう」シリーズの第1弾です。",
        "llama.cpp の llama-server を使い、Hugging Face から落とした 2 つのモデルを 1 つのサーバーで切り替えて使えるようにして、",
        "systemd で常駐させるところまでを、四国めたんとずんだもんの掛け合いで解説します。",
        "",
        "■ この動画で分かること",
        "・llama.cpp の入手と、Hugging Face でのモデルの探し方",
        "・コンテキスト長と VRAM の関係（設定なしで起動すると何が起きるか）",
        "・ルーターモードとプリセット（models.ini）で、モデルごとに設定する方法",
        "・小さなモデルを 2 つ常駐させて、切り替えを一瞬にする方法",
        "・OOM（メモリ不足）の見分け方と、llama-fit-params での見積もり",
        "・systemd で常駐させる方法",
        "",
        "■ 撮影環境",
        "Arch 系 Linux / NVIDIA GeForce RTX 4070（VRAM 12GB）/ llama.cpp build 11429",
        "モデル: Gemma 4 E4B（Q4_K_M）、Qwen3 4B（Q4_K_M）",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ 元になった記事と台本",
        f"記事: {ARTICLE}",
        f"台本: {SCRIPT_DOC}",
        "",
        "■ ソースコード（台本・音声合成・動画生成）",
        REPO,
        "",
        "■ 制作",
        "台本・記事・検証・動画の組み立て: Claude Code",
        "Hugging Face と Web UI の画面の撮影: Claude in Chrome",
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
        "#ローカルLLM #llamacpp #ずんだもん #四国めたん #VOICEVOX",
    ])
