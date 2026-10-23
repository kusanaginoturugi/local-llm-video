"""第3弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
CODE = "https://github.com/kusanaginoturugi/voice-chat"
ARTICLE = "https://claude.ai/artifact/XUxWANTPfE6osvRi4zTb6U"
SCRIPT_DOC = "https://claude.ai/artifact/XVRqxtD2fCeVedg1qbSC9c"
EP01 = "https://youtu.be/3Sk9T1VqNsg"
EP02 = "https://youtu.be/k-ploGYRc_Q"

# サムネイル（video/make_thumbnail.py）
THUMBNAIL = {
    "badge": "第3弾",
    "title": "声で話すと",
    "title2": "声で返事！",
    "sub": "whisper.cpp × llama.cpp × VOICEVOX",
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


def thumbnail(k):
    """サムネイル。話しかけるとずんだもんが声で返事をするところを、そのまま絵にする。

    k は video/make_thumbnail.py から渡される道具（大きさ・フォント・SD 絵など）。
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    W, H, font, out = k["W"], k["H"], k["font"], k["outlined"]
    ink, yellow, pink, green = (20, 20, 30), (255, 214, 64), (255, 110, 180), (120, 220, 80)

    # 背景: 写真を明るめに残し、緑から橙へのグラデーションを重ねる（第1弾の緑青、第2弾の青紫と見分けられるように）
    bg = k["cover"](Image.open(k["BG_IMAGE"]).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.8).convert("RGBA")
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        t = x / W
        gd.line((x, 0, x, H), fill=(int(40 + 180 * t), int(140 - 40 * t), int(70 - 30 * t), 170))
    bg.alpha_composite(grad)
    d = ImageDraw.Draw(bg)

    # 上: シリーズ名と回数
    d.rounded_rectangle((24, 20, 500, 76), 14, fill=(0, 0, 0, 150))
    d.text((44, 48), "ローカル LLM で遊ぼう", font=font(k["BOLD"], 32), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((394, 28, 490, 68), 10, fill=pink)
    d.text((442, 48), "第3弾", font=font(k["BLACK"], 26), fill=(255, 255, 255), anchor="mm")

    # 見出し（2 行）
    out(d, (W // 2, 150), "ずんだもんと", font(k["BLACK"], 92), (255, 255, 255), ink, 10)
    out(d, (W // 2, 265), "声でおしゃべり！", font(k["BLACK"], 104), yellow, ink, 12)

    # 真ん中: あなた（右）の吹き出しと、ずんだもん（左）の返事
    d.rounded_rectangle((640, 340, 1130, 420), 24, fill=(70, 120, 200), outline=ink, width=4)
    d.text((885, 380), "明日は雨。何しよう？", font=font(k["BOLD"], 40), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle((280, 430, 910, 545), 26, fill=(255, 255, 255), outline=ink, width=5)
    d.text((595, 468), "おうちでゆっくりするのだ。", font=font(k["BLACK"], 40), fill=ink, anchor="mm")
    d.text((595, 512), "オマエは何が好きなのだ？", font=font(k["BLACK"], 36), fill=(40, 140, 40), anchor="mm")
    out(d, (430, 380), "返事まで 約0.2秒", font(k["BLACK"], 44), yellow, ink, 8)

    # 下: 何を使うか（左右のキャラの間に収める）
    d.rounded_rectangle((300, 560, 980, 650), 18, fill=(0, 0, 0, 170))
    d.text((640, 588), "whisper.cpp × llama.cpp × VOICEVOX", font=font(k["BOLD"], 32), fill=green, anchor="mm")
    d.text((640, 626), "全部自分のパソコンの中で", font=font(k["BOLD"], 30), fill=(255, 255, 255), anchor="mm")

    # キャラクター: 左下にめたん、右下にずんだもん（喜んでいる表情）
    metan = k["sd"]("met_s214", 300)
    zun = k["sd"]("zunmon_3022", 290)
    bg.alpha_composite(metan, (10, H - metan.height + 80))
    bg.alpha_composite(zun, (W - zun.width - 20, H - zun.height + 20))
    return bg
