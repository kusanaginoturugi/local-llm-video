"""第5弾の台本から、章（screens.tsv）と演出（direction.tsv）を生成する。"""
import csv
from pathlib import Path

from build_script import parse

HERE = Path(__file__).parent
LINES, CHAPTERS = parse()
STARTS = dict(CHAPTERS)

SCREENS = {
    1: "タイトル", 5: "この動画を作った AI", 11: "スキャンした PDF は写真", 14: "検索できない PDF",
    16: "検索できる PDF の作り方", 21: "NDLOCR-Lite", 27: "わたくしの自炊本", 31: "一寸法師（NDL・保護期間満了）",
    35: "入れ方", 36: "コマンド一本", 39: "フォルダがないとき", 45: "CPU の時間",
    49: "GPU 版に入れ替える", 50: "CPU と GPU の実録（5倍速）", 55: "かかった時間の表",
    57: "Firefox で検索（実録）", 59: "文字の層を青く描いた見開き", 60: "pdftotext で抜き出した文字",
    63: "答え合わせ", 65: "表記の違い", 67: "答え合わせの手順", 69: "正解率 約 99.4%",
    71: "読み間違いの例", 73: "蔵書印と屋臺", 77: "紙を白くした見開き", 79: "白くしたときの誤りの数",
    84: "工夫が 1 行ずつ増える", 95: "コマンド一本と二週間", 99: "まとめ", 101: "自分で使う分だけ",
    103: "概要欄の記事", 106: "普通に締める", 107: "クレジット",
}

# めたん・ずんだもんの表情（SD 絵）。つむぎの行は angry / happy で表情を変える（次に変わるまで続く）
REACT = {
    2: "zunmon_3015", 3: "happy", 4: "met_s214", 9: "zunmon_3017", 13: "angry", 17: "happy",
    19: "met_s214", 20: "zunmon_3016", 24: "zunmon_3015", 26: "zunmon_3009", 30: "zunmon_3015",
    40: "zunmon_3015", 42: "zunmon_3021", 46: "zunmon_3022", 47: "met_s214", 48: "zunmon_3019",
    53: "zunmon_3021", 62: "zunmon_3015", 68: "zunmon_3015", 70: "zunmon_3022",
    75: "met_s222", 76: "zunmon_3019", 78: "zunmon_3022", 82: "zunmon_3015",
    84: "met_s215", 85: "met_s222", 86: "met_s215", 87: "met_s222", 88: "met_s215",
    89: "zunmon_3022", 90: "met_s222", 92: "met_s215", 93: "angry", 94: "zunmon_3020",
    95: "met_s222", 96: "zunmon_3009", 97: "happy", 98: "met_s218", 104: "zunmon_3015", 107: "zunmon_3022",
}
MOTION = {
    3: "jump", 13: "shake", 22: "jump", 42: "shake", 48: "jump", 51: "jump", 53: "jump",
    58: "jump", 70: "jump", 72: "jump", 78: "jump", 80: "jump", 89: "jump", 93: "shake",
    94: "shake", 100: "jump", 105: "jump",
}
STYLE = {75: "ささやき", 42: "ツンツン", 53: "ツンツン", 94: "なみだめ", 98: "ツンツン"}
YOMI = {35: "3.11=さんてんいちいち", 31: "1935年=せんきゅうひゃくさんじゅうごねん"}
INTONATION = {3: 1.2, 13: 1.2, 22: 1.3, 42: 1.3, 51: 1.3, 53: 1.4, 58: 1.2, 70: 1.3,
              72: 1.2, 80: 1.2, 89: 1.3, 93: 1.2, 105: 1.2}
GAP = {i: 2.4 for i in STARTS if i != 1}
GAP.update({
    51: 7.7,   # 実録を流して、GPU が終わる（流し始めて 13.5 秒）直後に「え、もう終わった？」。50 行は 6.3 秒
    58: 4.0,   # 検索の実録で、一致が光るのを待つ
    75: 1.0, 91: 0.4, 93: 0.6, 94: 0.4,
})


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
        YOMI.get(no, ""), "", "") for no, (speaker, _) in enumerate(LINES, 1)))
