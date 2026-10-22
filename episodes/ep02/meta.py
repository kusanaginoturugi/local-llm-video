"""第2弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
CODE = "https://github.com/kusanaginoturugi/voice-input/tree/main/lite"
ARTICLE = "https://claude.ai/artifact/Bdmebajj8SxkXZtU4cznmS"
SCRIPT_DOC = "https://claude.ai/artifact/PJcRLgEeSwghav4EFVSSHE"
EP01 = "https://youtu.be/3Sk9T1VqNsg"

# サムネイル（video/make_thumbnail.py）
THUMBNAIL = {
    "badge": "第2弾",
    "title": "whisper.cpp",
    "title2": "で音声入力！",
    "sub": "全部ローカル・シェル 92 行",
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


def thumbnail(k):
    """サムネイル。「えっと、あの…」が整った文章に変わるところを、そのまま絵にする。

    k は video/make_thumbnail.py から渡される道具（大きさ・フォント・SD 絵など）。
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    W, H, font, out = k["W"], k["H"], k["font"], k["outlined"]
    ink, yellow, pink, green = (20, 20, 30), (255, 214, 64), (255, 110, 180), (120, 220, 80)

    # 背景: 写真を明るめに残し、青から紫へのグラデーションを重ねる
    bg = k["cover"](Image.open(k["BG_IMAGE"]).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.8).convert("RGBA")
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        t = x / W
        gd.line((x, 0, x, H), fill=(int(30 + 90 * t), int(60 - 20 * t), int(170 + 40 * t), 170))
    bg.alpha_composite(grad)
    d = ImageDraw.Draw(bg)

    # 上: シリーズ名と回数
    d.rounded_rectangle((24, 20, 500, 76), 14, fill=(0, 0, 0, 150))
    d.text((44, 48), "ローカル LLM で遊ぼう", font=font(k["BOLD"], 32), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((394, 28, 490, 68), 10, fill=pink)
    d.text((442, 48), "第2弾", font=font(k["BLACK"], 26), fill=(255, 255, 255), anchor="mm")

    # 見出し（2 行）
    out(d, (W // 2, 150), "しゃべるだけで", font(k["BLACK"], 92), (255, 255, 255), ink, 10)
    out(d, (W // 2, 265), "整った文章に！", font(k["BLACK"], 104), yellow, ink, 12)

    # 真ん中: 吹き出し（話したまま）→ 整った文章
    bx0, by0 = 150, 345
    d.rounded_rectangle((bx0, by0, bx0 + 480, by0 + 150), 26, fill=(255, 255, 255), outline=ink, width=5)
    f = font(k["BOLD"], 40)
    d.text((bx0 + 30, by0 + 48), "えっと、あの、", font=f, fill=(150, 150, 160), anchor="lm")
    d.text((bx0 + 30, by0 + 108), "火曜日、いや水曜日…", font=f, fill=(150, 150, 160), anchor="lm")
    w1 = f.getlength("えっと、あの、")
    w2 = f.getlength("火曜日、")
    for x0, x1, y in ((bx0 + 30, bx0 + 30 + w1, by0 + 48), (bx0 + 30, bx0 + 30 + w2, by0 + 108)):
        d.line((x0, y, x1, y), fill=(235, 60, 60), width=6)  # 消える言葉に赤い線
    d.polygon([(655, 390), (735, 420), (655, 450)], fill=yellow, outline=ink)
    d.rounded_rectangle((760, 350, 1130, 490), 22, fill=(255, 250, 225), outline=yellow, width=7)
    d.text((945, 397), "水曜日の", font=font(k["BLACK"], 48), fill=ink, anchor="mm")
    d.text((945, 451), "10時からです。", font=font(k["BLACK"], 44), fill=ink, anchor="mm")

    # 下: 何を使うか（左右のキャラの間に収める）
    d.rounded_rectangle((300, 560, 980, 650), 18, fill=(0, 0, 0, 170))
    d.text((640, 588), "whisper.cpp × ローカル LLM", font=font(k["BOLD"], 38), fill=green, anchor="mm")
    d.text((640, 626), "全部自分のパソコンで", font=font(k["BOLD"], 30), fill=(255, 255, 255), anchor="mm")

    # キャラクター: 左下にめたん、右下にずんだもん（驚いた表情）
    metan = k["sd"]("met_s214", 300)
    zun = k["sd"]("zunmon_3019", 290)
    bg.alpha_composite(metan, (10, H - metan.height + 80))
    bg.alpha_composite(zun, (W - zun.width - 20, H - zun.height + 20))
    return bg
