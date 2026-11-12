"""第5弾の画面。行番号ごとに背景に出す画面を決める。"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "video"))
from slidekit import big, bullets, flow, image, table, term, title


def screencam(file, label, speed=1, source_start=0):
    return ("screencam", f"demo/{file}", label, speed, source_start)


# 残り 0.6 パーセントの工夫。めたんが話すたびに 1 行ずつ増える
EFFORT = [
    "行の画像に余白を足して、読み直す",
    "OCR を二つ（NDLOCR-Lite と YomiToku）",
    "ルビを外す・パとバを単語で読み直す",
    "傾きを直し、文字の位置も回して重ねる",
    "食い違いを LLM（Gemma 4 12B）に二回聞く",
    "最後は人が画像で決める（一冊 231 か所）",
    "旧字体の対応表（掴 → 摑）",
]


def effort(n):
    return bullets("残り 0.6 パーセントのために", EFFORT[:n])


SLIDES = {
    1: title("ローカル LLM で遊ぼう", "第5弾：スキャンした本を、検索できる PDF に"),
    5: table("この動画を作った AI", ["回", "台本・検証・動画の組み立て"], [
        ["第1〜3弾", "Claude Code"],
        ["第4弾", "Codex（つむぎの SD 絵も）"],
        ["第5弾", "Claude Code"],
    ], hl=[1]),
    11: big("スキャンした PDF は、ページの写真"),
    14: flow("検索できない PDF", [("PDF", "ページの写真だけ"), ("検索", "0 件")]),
    16: flow("検索できる PDF の作り方", [("ページの画像", "スキャンのまま"),
                                         ("OCR", "画像から文字を読み取る"),
                                         ("透明な文字", "同じ位置に重ねる")]),
    21: bullets("NDLOCR-Lite", ["国立国会図書館が公開している OCR（CC BY 4.0）",
                                "縦書きの日本語に強い",
                                "GPU なしでも動く（GPU も使える）",
                                "PDF を入れて、検索できる PDF を出せる"]),
    27: table("わたくしの自炊本", ["項目", "内容"], [
        ["冊数", "83 冊（スキャンした文庫など）"],
        ["中身", "ページの画像だけ"],
        ["この動画に出すもの", "書名・ページ数・かかった時間だけ"],
    ]),
    31: image("issun-040.jpg"),
    35: term(["NDLOCR-Lite を入れる（Python 3.11 以上）",
              "$ git clone https://github.com/ndl-lab/ndlocr-lite",
              "$ cd ndlocr-lite",
              "$ pip install -r requirements.txt",
              "$ cd src"]),
    36: term(["検索できる PDF を作る",
              "$ mkdir out",
              "$ python3 ocr.py --sourcepdf issun-boshi.pdf --output out \\",
              "    --pdf-output issun-boshi-ocr.pdf --pdf-render-dpi 300"], hl=[2, 3]),
    39: term(["作業用のフォルダ（--output）がないと",
              "$ python3 ocr.py --sourcepdf issun-boshi.pdf --output nai …",
              "Output Directory is not found.",
              "$ echo $?",
              "0"], hl=[2]),
    45: table("文庫 1 冊（356 ページ、300dpi）", ["", "かかった時間"], [
        ["CPU（Core i5-13400F）", "約 6 分（356.7 秒）"],
    ]),
    49: term(["GPU で動かす（onnxruntime を GPU 版に入れ替える）",
              "$ pip uninstall onnxruntime",
              "$ pip install 'onnxruntime-gpu[cuda,cudnn]==1.31.1'",
              "$ python3 ocr.py … --device cuda"], hl=[3]),
    50: screencam("rec/bunko-cpu-vs-gpu-x5.mp4", "文庫 356 ページ／CPU と GPU の実録・5倍速"),
    55: table("かかった時間（300dpi）", ["本", "CPU", "GPU（RTX 4070）"], [
        ["文庫 356 ページ", "約 6 分", "1 分 8 秒"],
        ["一寸法師 208 コマ（見開き）", "4 分 55 秒", "1 分 45 秒"],
    ]),
    57: screencam("rec/firefox-search-cut.mp4", "Firefox で「明智」を検索／実録"),
    59: image("issun-040-visible.jpg"),
    60: image("pdftotext-040.png"),
    63: title("答え合わせ", "青空文庫の『一寸法師』と並べる"),
    65: table("同じ文でも、表記が違う", ["1935 年の本（OCR）", "青空文庫（2004 年の全集）"], [
        ["賣場・變な・樣", "売場・変な・様"],
        ["ゐる・いふ", "いる・いう"],
    ]),
    67: flow("答え合わせの手順", [("1 文字ずつ並べる", "OCR と青空文庫"),
                                  ("何度も出る置き換え", "表記の違いとして外す"),
                                  ("残りから 40 か所", "元の画像で確かめる")]),
    69: big("字の正解率　約 99.4%"),
    71: image("ocr-miss.jpg"),
    73: image("ocr-miss-yatai.jpg"),
    74: big("残りの 0.6 パーセント"),
    77: image("issun-040-clean.jpg"),
    79: table("紙を白くすると（一寸法師の本文 約 8 万 7 千字）", ["OCR に渡した画像", "誤りの候補"], [
        ["そのまま", "628 か所"],
        ["白くする（わたくしの設定）", "1,443 か所"],
        ["白くする（薄い線を残す設定）", "1,179 か所"],
    ], hl=[0]),
    84: effort(1), 85: effort(2), 86: effort(3), 87: effort(4), 88: effort(5),
    90: effort(6), 92: effort(7),
    95: big("99.4% はコマンド一本。残り 0.6% に二週間。"),
    99: bullets("まとめ", ["NDLOCR-Lite を入れる（CPU だけでも動く）",
                           "作業用のフォルダを先に作る",
                           "ocr.py --sourcepdf … --pdf-output … の一本",
                           "GPU なら、文庫 1 冊が約 1 分"]),
    101: big("自炊した本は、自分で使う分だけ"),
    103: bullets("詳しい手順と数字", ["概要欄の記事に掲載",
                                     "コマンドと計測の条件",
                                     "答え合わせのやり方"]),
    106: title("それでは、また次回。", "ローカル LLM で遊ぼう 第5弾"),
    107: title("次回も見てね！", "音声：VOICEVOX:四国めたん／ずんだもん／春日部つむぎ"),
}
