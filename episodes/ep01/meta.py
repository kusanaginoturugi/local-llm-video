"""第1弾の概要欄とサムネイルの文言。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
ARTICLE = "https://claude.ai/code/artifact/2be896e8-2ab9-4dd7-bf05-cff1beb45e71"
SCRIPT_DOC = "https://claude.ai/code/artifact/45ace86b-536a-4dd5-a09a-cb9db2f17fa1"

# 公開後に見つかった読み間違いの訂正。概要欄のいちばん上に置く
NOTE = ("※ 音声の読み間違いの訂正：動画の中の「Qwen 3（クウェンサン）」は、「クウェンスリー」と読むのが正しいです。"
        "「クエン酸」と聞こえるところがありますが、Alibaba のモデル Qwen 3 のことです。")

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
        NOTE,
        "",
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


def thumbnail(k):
    """サムネイル。1 つの llama-server から 2 つのモデルを切り替えて使うところを、そのまま絵にする。

    k は video/make_thumbnail.py から渡される道具（大きさ・フォント・SD 絵など）。
    """
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    W, H, font, out = k["W"], k["H"], k["font"], k["outlined"]
    ink, yellow, pink, green = (20, 20, 30), (255, 214, 64), (255, 110, 180), (120, 220, 80)

    # 背景: 写真を明るめに残し、緑から青へのグラデーションを重ねる（第2弾の青紫と見分けられるように）
    bg = k["cover"](Image.open(k["BG_IMAGE"]).convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.8).convert("RGBA")
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        t = x / W
        gd.line((x, 0, x, H), fill=(int(10 + 20 * t), int(120 - 50 * t), int(110 + 90 * t), 170))
    bg.alpha_composite(grad)
    d = ImageDraw.Draw(bg)

    # 上: シリーズ名と回数
    d.rounded_rectangle((24, 20, 500, 76), 14, fill=(0, 0, 0, 150))
    d.text((44, 48), "ローカル LLM で遊ぼう", font=font(k["BOLD"], 32), fill=(255, 255, 255), anchor="lm")
    d.rounded_rectangle((394, 28, 490, 68), 10, fill=pink)
    d.text((442, 48), "第1弾", font=font(k["BLACK"], 26), fill=(255, 255, 255), anchor="mm")

    # 見出し（2 行）
    out(d, (W // 2, 150), "自分のパソコンに", font(k["BLACK"], 88), (255, 255, 255), ink, 10)
    out(d, (W // 2, 265), "AI サーバーを立てる！", font(k["BLACK"], 96), yellow, ink, 12)

    # 真ん中: llama-server（窓口 1 つ）から 2 つのモデルへ
    d.rounded_rectangle((170, 365, 560, 485), 24, fill=(255, 255, 255), outline=ink, width=5)
    d.text((365, 405), "llama-server", font=font(k["BLACK"], 46), fill=ink, anchor="mm")
    d.text((365, 455), "窓口は 1 つ", font=font(k["BOLD"], 30), fill=(90, 90, 100), anchor="mm")
    for y in (380, 470):
        d.line((560, 425, 740, y), fill=yellow, width=8)
    for y, name in ((345, "Gemma 4"), (435, "Qwen3")):
        d.rounded_rectangle((740, y, 1110, y + 72), 18, fill=(255, 250, 225), outline=yellow, width=6)
        d.text((925, y + 36), name, font=font(k["BLACK"], 42), fill=ink, anchor="mm")
    out(d, (860, 535), "名前を変えるだけで切り替え", font(k["BOLD"], 30), (255, 255, 255), ink, 6)

    # 下: 何を使うか（左右のキャラの間に収める）
    d.rounded_rectangle((300, 575, 980, 665), 18, fill=(0, 0, 0, 170))
    d.text((640, 603), "llama.cpp × VRAM 12GB", font=font(k["BOLD"], 38), fill=green, anchor="mm")
    d.text((640, 641), "2 モデル常駐・切り替え一瞬・OOM 対策", font=font(k["BOLD"], 28), fill=(255, 255, 255), anchor="mm")

    # キャラクター: 左下にめたん、右下にずんだもん（喜んでいる表情）
    metan = k["sd"]("met_s214", 300)
    zun = k["sd"]("zunmon_3022", 290)
    bg.alpha_composite(metan, (10, H - metan.height + 80))
    bg.alpha_composite(zun, (W - zun.width - 20, H - zun.height + 20))
    return bg
