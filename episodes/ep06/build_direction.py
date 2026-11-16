"""第6弾の台本から、章（screens.tsv）と演出（direction.tsv）を生成する。"""
import csv
import re
from pathlib import Path

from build_script import parse

HERE = Path(__file__).parent
LINES, CHAPTERS = parse()
STARTS = dict(CHAPTERS)

SCREENS = {
    1: "タイトル", 4: "本を買い間違えた", 6: "読みたかった本", 8: "英語版を買った理由", 11: "第4弾の翻訳の拡張",
    14: "Cloud Reader のページ", 18: "ページ内検索 0 件", 20: "目には見えても文字がない",
    23: "鍵は外さない", 25: "見えているものを読む", 27: "NDLOCR-Lite と tesseract", 28: "kindle-ja",
    30: "Claude Code と半日", 31: "kindle-ja の流れ", 32: "Emacs の画面", 36: "Emacs 以外でも読める",
    38: "一回押して一画面", 39: "今日の本", 40: "地下の国のアリス", 42: "実録：最初の版（2 倍速）", 45: "1 画面の時間（最初の版）",
    47: "つまずき 1", 49: "つまずき 2", 50: "つまずき 3", 51: "段落の規則", 53: "劇の台本だった",
    55: "別の本", 60: "時間の内訳", 64: "E4B と 12B", 66: "out of memory", 68: "今回の PC",
    70: "PLaMo", 74: "3 モデル", 75: "1 画面の時間（PLaMo）", 77: "時間の内訳（PLaMo）", 79: "PaddleOCR",
    81: "自炊本では外した", 84: "OCR の比べ（PaddleOCR）", 86: "入れるもの", 88: "OCR の比べ（RapidOCR）",
    90: "OCR サーバー", 91: "実録：今の版", 92: "1 画面の時間（今の版）", 94: "訳の比べ",
    99: "dear と too late", 103: "読み上げの流れ", 105: "読み上げの声", 109: "1.4 秒", 113: "紙の本を買った",
    118: "紙にした理由", 125: "使いどころ", 126: "まとめ", 128: "GitHub", 132: "普通に締める", 133: "クレジット",
}

# めたん・ずんだもんの表情（SD 絵）。つむぎの行は angry / happy で表情を変える（次に変わるまで続く）
# めたん：214 得意顔、215 ジト目、218 黒い怒り、221 元気、222 どんより
# ずんだもん：3009 すねる、3013 もぐもぐ、3015 はてな、3016 腕組みジト目、3017 うなだれ、3019 驚き、
#             3020 号泣、3021 衝撃、3022 大笑い、3030 小さくはてな
REACT = {
    1: "met_s222", 2: "zunmon_3015", 3: "happy", 4: "met_s222", 5: "zunmon_3030", 7: "zunmon_3021",
    10: "met_s214", 11: "zunmon_3022", 13: "zunmon_3013", 15: "angry", 16: "met_s222", 17: "zunmon_3015",
    22: "happy", 23: "met_s218", 24: "zunmon_3030", 29: "zunmon_3019", 30: "met_s214", 34: "met_s214",
    35: "zunmon_3015", 43: "zunmon_3022", 46: "zunmon_3030", 47: "met_s215", 48: "angry", 53: "met_s222",
    56: "zunmon_3021", 57: "happy", 58: "met_s222", 61: "zunmon_3019", 65: "zunmon_3015", 69: "zunmon_3030",
    71: "met_s222", 72: "zunmon_3017", 75: "met_s214", 77: "zunmon_3009", 78: "angry", 79: "met_s215",
    80: "zunmon_3015", 81: "met_s218", 82: "happy", 83: "met_s214", 85: "zunmon_3022", 86: "met_s222",
    87: "angry", 88: "met_s221", 89: "zunmon_3016", 91: "met_s214", 92: "happy", 93: "zunmon_3030",
    95: "angry", 97: "met_s215", 98: "zunmon_3021", 100: "happy", 101: "zunmon_3009", 104: "zunmon_3019",
    105: "met_s221", 108: "zunmon_3021", 111: "zunmon_3022", 113: "met_s215", 114: "zunmon_3021",
    115: "angry", 116: "met_s222", 119: "met_s218", 121: "met_s218", 122: "zunmon_3021", 124: "zunmon_3017",
    129: "happy", 130: "zunmon_3016", 133: "zunmon_3022",
}
MOTION = {
    11: "jump", 15: "shake", 29: "jump", 43: "jump", 48: "shake", 56: "shake", 61: "jump", 70: "jump",
    76: "jump", 78: "shake", 85: "jump", 87: "shake", 92: "jump", 95: "shake", 98: "jump", 108: "shake",
    111: "jump", 114: "jump", 115: "shake", 117: "shake", 122: "shake", 133: "jump",
}
STYLE = {23: "ツンツン", 58: "ささやき", 71: "ささやき", 72: "なみだめ", 108: "ツンツン", 121: "ツンツン",
         124: "なみだめ"}
# 行ごとの読み。「訳は・訳が・訳で・訳を」は自動で足す（下の yomi()）
YOMI = {
    3: "死んだ目=しんだめ",
    32: "上に=ウエニ",
    94: "dear, dear! I shall be too late!=ディア、ディア！ アイ、シャル、ビー、トゥー、レイト！",
    99: "dear=ディア",
    49: "I=アイ",
    51: "行=ギョウ",      # 「くだり」と読む
    52: "行=ギョウ",      # 「大文字の行って」を「いって」と読む
    86: "3.12=さんてんいちに",
    105: "1.18=イッテンイチハチ",   # ひらがなだと VOICEVOX が「いってんじゅうはち」と読む
    91: "5 分の 1=ごぶんのいち",
}
INTONATION = {11: 1.2, 29: 1.3, 43: 1.3, 61: 1.2, 70: 1.3, 76: 1.3, 85: 1.3, 92: 1.2, 98: 1.3, 111: 1.3,
              114: 1.3, 115: 1.2, 117: 1.3}
GAP = {i: 2.4 for i in STARTS if i != 1}
GAP.update({
    43: 2.7,   # 42 から実録（2 倍速、頭 1.5 秒を飛ばす）を流し、訳が Emacs に出る 4.75 秒後に「出てきたのだ！」。42 行は 2.26 秒
    15: 1.2,   # 14 で拡張のボタンを押してから、何も起きないのを見せる間
    54: 0.4, 58: 0.8, 71: 1.0, 113: 1.0,
})


def yomi(no, text):
    """「訳は」「訳が」「訳で」「訳を」を「わけ」と読まないよう、「翻訳」でない「訳」だけ読みを足す。"""
    parts = [YOMI[no]] if no in YOMI else []
    for particle in "はがでを":
        if re.search(rf"(?<!翻)訳{particle}", text) and f"翻訳{particle}" not in text:
            parts.append(f"訳{particle}=ヤク{'ワ' if particle == 'は' else particle}")
    return ";".join(parts)


def write(name, header, rows):
    with (HERE / name).open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


section = ""
screens = []
for no, (speaker, _) in enumerate(LINES, 1):
    section = STARTS.get(no, section)
    screens.append((no, section, speaker, SCREENS.get(no, "")))
write("screens.tsv", ("no", "section", "speaker", "screen"), screens)
write("direction.tsv",
      ("no", "speaker", "style", "intonation", "gap", "motion", "react", "yomi", "kana", "memo"),
      ((no, speaker, STYLE.get(no, "") if speaker in ("めたん", "ずんだもん") else "",
        INTONATION.get(no, ""), GAP.get(no, ""), MOTION.get(no, ""), REACT.get(no, ""),
        yomi(no, text), "", "") for no, (speaker, text) in enumerate(LINES, 1)))
