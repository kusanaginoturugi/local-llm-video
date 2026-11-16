"""第6弾の画面。行番号ごとに背景に出す画面を決める。

画面に出す本は、著作権の切れた『地下の国のアリス』（Alice's Adventures Under Ground、1886 年の手書き本の複製。Kindle の 0 円の版）だけ。
制作者が買った本（一幕劇・本命の本）のページや本文は出さない。訳の比べは、このページを手元のモデルで訳したもの。
実録と静止画は demo/record_kindle.sh で撮った（Firefox のタブとアドレスバーは録画で白く塗った）。
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "video"))
from slidekit import big, bullets, flow, image, table, title


def screencam(file, label, speed=1, source_start=0):
    return ("screencam", f"demo/{file}", label, speed, source_start)


# つまずいたところ。めたんが話すたびに 1 行ずつ増える
STUMBLE = [
    "ページ送りの矢印を文字と読んだ → 本文の幅だけ撮る",
    "I を 1 と読んだ → 2 倍に引き伸ばしてから読む",
    "段落が切れる・くっつく → 段落の規則を作る",
]


def stumble(n):
    return bullets("作っていて、つまずいたところ", STUMBLE[:n])


# 紙の本にした理由。めたんが話すたびに増える
REASONS = [
    "話題の本なので、読み終わったら回し読みしたい",
    "日本の Kindle の本は、人に貸せない",
    "買っても、読む権利を借りているだけ（実質レンタル）",
    "なのに値段は、紙の本と同じくらい",
    "人が訳した本には、まだ敵わない",
]


def reasons(n):
    return bullets("紙の日本語版にした理由", REASONS[:n])


def models(hl):
    return table("同じページを訳す（1 画面、Chapter I の冒頭）", ["モデル", "1 画面", "VRAM"], [
        ["Gemma 4 E4B", "約 8 秒", "音声入力用に、いつも載せている"],
        ["Gemma 4 12B", "約 15 秒", "E4B と同時には載らない"],
        ["PLaMo 3 Translate 0.8B", "約 2.1 秒", "E4B と一緒に載る"],
    ][: 3 if 2 in hl else 2], hl=hl)


def ocr(hl):
    return table("Kindle の画面を OCR で読む（1 画面）", ["OCR", "画像", "1 画面", "tesseract との食い違い"], [
        ["tesseract（CPU）", "2 倍", "0.9 秒", "（基準）"],
        ["PaddleOCR 本体（GPU）", "そのまま", "0.49 秒", "0"],
        ["RapidOCR（GPU）", "そのまま", "0.43 秒", "10（! を l と読む など）"],
        ["RapidOCR（GPU）", "2 倍", "0.57 秒", "0"],
    ], hl=hl)


def translations(hl):
    return table("dear, dear! I shall be too late!（ウサギのひとりごと）", ["モデル", "訳"], [
        ["Gemma 4 E4B", "「ああ、ああ！ 遅れてしまうわ！」"],
        ["Gemma 4 12B", "「おっと、おっと！ 遅れてしまう！」"],
        ["PLaMo 0.8B", "「あなた、あなた！ もう手遅れよ！」"],
    ], hl=hl)


def times(hl):
    return table("1 画面の時間", ["版", "OCR", "翻訳", "1 画面"], [
        ["最初の版", "tesseract（CPU）", "Gemma 4 E4B", "約 8 秒"],
        ["翻訳を替える", "tesseract（CPU）", "PLaMo 0.8B", "約 2.1 秒"],
        ["OCR も替える", "RapidOCR（GPU）", "PLaMo 0.8B", "約 1.5 秒"],
    ][: max(hl) + 1], hl=hl)


SLIDES = {
    1: title("ローカル LLM で遊ぼう", "第6弾：Kindle の英語の本を、手元の LLM で訳して読む"),
    4: big("Kindle で、本を買い間違えた"),
    6: table("読みたかった本", ["", ""], [
        ["書名", "If Anyone Builds It, Everyone Dies"],
        ["著者", "Eliezer Yudkowsky、Nate Soares（2025）"],
        ["中身", "人より賢い AI を作ったら、人類はみんな死ぬ"],
    ]),
    8: bullets("英語版を買った", ["セールで、英語版が安く出ていた",
                                 "日本語版は、検索に出てこなかった",
                                 "第4弾の翻訳の拡張があれば、英語でも読めるはず"]),
    11: title("Local LLM Translator", "第4弾：ページを丸ごと、手元の LLM で翻訳する拡張"),
    14: image("kindle-page.png"),
    18: image("kindle-find.png"),
    20: flow("目には見えても、文字がない", [("Kindle Cloud Reader", "ページを絵として描く"),
                                           ("ページ内検索", "0 件"),
                                           ("翻訳の拡張", "訳す文字がない")]),
    23: big("本の鍵（DRM）は外さない"),
    25: flow("見えているものを読む", [("画面", "1 画面ずつ撮る"), ("OCR", "絵から文字に"),
                                     ("手元の LLM", "日本語に訳す")]),
    27: table("OCR", ["", "得意なもの"], [
        ["NDLOCR-Lite（第5弾）", "日本語の縦書き"],
        ["tesseract", "英語など、横書き"],
    ], hl=[1]),
    28: title("kindle-ja", "github.com/kusanaginoturugi/kindle-ja"),
    30: big("Claude Code と相談しながら、半日で"),
    31: flow("kindle-ja の流れ（最初の版）", [("SUPER + Y", "画面の本文を撮る"), ("tesseract", "OCR"),
                                            ("llama-server", "手元の LLM で訳す"), ("Emacs", "Org ファイルに足す")]),
    32: image("emacs-alice.png"),
    36: bullets("Emacs 以外でも読める", ["訳は、テキストファイル（Org）に足していくだけ",
                                       "変更を読み直せるエディタなら読める",
                                       "書き換えは、自分のコーディングエージェントに頼む"]),
    38: big("一回押して、一画面"),
    39: table("今日の本", ["", ""], [["書名", "Alice's Adventures Under Ground（地下の国のアリス）"],
                                  ["中身", "『不思議の国のアリス』の元になった、キャロルの手書きの本（1886 年の複製）"],
                                  ["値段", "Kindle の 0 円の版"]]),
    40: image("kindle-page.png"),
    42: screencam("rec/kindle-first.mp4", "実録：最初の版（tesseract ＋ Gemma 4 E4B）・2 倍速", speed=2, source_start=1.5),
    45: times([0]),
    47: stumble(1),
    49: stumble(2),
    50: stumble(3),
    51: bullets("段落の規則（tesseract）", ["短い行のあとで切る", "行の終わりのハイフンはつなぐ",
                                         "全部大文字の行は、それだけで一段落"]),
    53: big("あの本、劇の台本だった"),
    55: big("題名が同じだけの、別の本"),
    60: table("1 画面の時間（tesseract ＋ E4B）", ["処理", "時間"], [
        ["拡大と OCR（tesseract、CPU）", "1.3 秒"],
        ["翻訳（Gemma 4 E4B）", "7 秒"],
    ], hl=[1]),
    64: models([1]),
    66: big("cudaMalloc failed: out of memory"),
    68: table("今回の PC", ["", ""], [["CPU", "Ryzen 7 3700X"], ["GPU", "RTX 3060（VRAM 12GB）"],
                                      ["第5弾まで", "RTX 4070 の PC"]]),
    70: title("PLaMo 3 Translate 0.8B", "第4弾の主役。翻訳専用の小さいモデル"),
    74: models([2]),
    75: times([1]),
    77: table("1 画面の時間（tesseract ＋ PLaMo）", ["処理", "時間"], [
        ["拡大と OCR（tesseract、CPU）", "1.3 秒"],
        ["翻訳（PLaMo 0.8B）", "0.9 秒"],
    ], hl=[0]),
    79: title("PaddleOCR", "Baidu の OCR。GPU で動く"),
    81: bullets("PaddleOCR（わたくしの自炊本の作業で）", ["日本語の縦書きで、句読点やかっこを落とした",
                                                        "目で比べた範囲で、正しく補った箇所はなかった",
                                                        "本文の候補から外した"]),
    84: ocr([1]),
    86: table("入れるもの", ["", "Python", "大きさ"], [
        ["PaddleOCR 本体", "3.12 を別に用意（3.14 向けがない）", "約 10GB"],
        ["RapidOCR", "いつもの 3.14", "約 2.7GB"],
    ]),
    88: ocr([3]),
    90: flow("OCR サーバー（kindle-ja-ocrd）", [("kindle-ja", "画像を送る"),
                                               ("RapidOCR（GPU）", "2 倍に拡大して読む"),
                                               ("段落", "行の間隔で組み立てる")],
             notes=[("寝る", "10 分使わなければ終わって、VRAM を返す", False)]),
    91: screencam("rec/kindle-final.mp4", "実録：今の版（RapidOCR ＋ PLaMo 0.8B）・等倍", speed=1, source_start=1.5),
    92: times([2]),
    94: translations([]),
    95: translations([0]),
    96: translations([1]),
    97: translations([2]),
    99: table("dear と too late", ["英語", "ここでの意味", "PLaMo の訳"], [
        ["dear, dear!", "おやおや（困ったときの声）", "あなた、あなた！"],
        ["I shall be too late!", "遅れちゃう！", "もう手遅れよ！"],
    ]),
    103: flow("読み上げ（kindle-ja-say）", [("訳", "文に分ける"), ("VOICEVOX", "1 文ずつ合成"),
                                          ("pw-play", "流しながら次の文を作る")]),
    105: table("読み上げの声", ["", ""], [["話者", "ずんだもん"], ["速さ", "1.18 倍"]]),
    109: big("訳が出てから、1.4 秒で読み始める"),
    113: big("日本語版を、紙の本で買った"),
    118: reasons(1),
    119: reasons(3),
    121: reasons(4),
    123: reasons(5),
    125: bullets("kindle-ja の使いどころ", ["日本語版がない本", "とりあえず中身を知りたい本"]),
    126: bullets("まとめ", ["Kindle の本は、ページの中に文字がない",
                           "鍵は外さず、1 画面ずつ OCR して手元の LLM で訳す",
                           "OCR は GPU の RapidOCR、訳は PLaMo 0.8B で 1 画面 1 秒",
                           "訳は VOICEVOX で読み上げもできる"]),
    128: title("kindle-ja", "github.com/kusanaginoturugi/kindle-ja"),
    132: title("それでは、また次回。", "ローカル LLM で遊ぼう 第6弾"),
    133: title("次回も見てね！", "音声：VOICEVOX:四国めたん／ずんだもん／春日部つむぎ"),
}
