"""確定した第4弾台本の章、画面指示、演出を生成する。"""
import csv
from pathlib import Path

from build_script import parse

HERE = Path(__file__).parent
LINES, CHAPTERS = parse()
STARTS = dict(CHAPTERS)

SCREENS = {
    1: "タイトル", 3: "つむぎが怒り顔でタイトルへ乱入",
    9: "ページ翻訳の本編", 13: "Local LLM Translator", 15: "翻訳の流れ",
    19: "PLaMo 0.8B・約0.57 GB",
    21: "Microsoft Learn 日本語版", 25: "英語版の原文",
    27: "英語版を PLaMo で翻訳した実画面", 28: "訳文の比較",
    34: "TranslateGemma 12B", 36: "TranslateGemma 4B", 38: "Hy-MT2",
    40: "PLaMo の翻訳品質", 44: "同じ記事で比較",
    45: "TranslateGemma 12B・約7.3 GB の実録",
    48: "PLaMo 0.8B・約0.57 GB の紹介",
    49: "PLaMo 実録・等速", 53: "PLaMo 実録・4倍スロー",
    58: "導入と設定", 59: "モデル入手", 61: "旧版のエラー",
    63: "対応版のバージョンと起動コマンド", 67: "Translation Settings",
    71: "翻訳・再翻訳・用語集", 73: "解説ページ",
    77: "普通に締める", 79: "つむぎが再乱入", 83: "クレジット",
}

REACT = {
    4: "zunmon_3015", 7: "zunmon_3019",
    10: "zunmon_3015", 12: "zunmon_3016", 18: "zunmon_3021",
    20: "zunmon_3021", 22: "zunmon_3019", 24: "zunmon_3015",
    26: "zunmon_3022", 28: "zunmon_3022", 30: "zunmon_3022",
    35: "zunmon_3019", 37: "zunmon_3015", 39: "zunmon_3022",
    41: "zunmon_3022", 43: "zunmon_3021", 47: "zunmon_3019",
    50: "zunmon_3019", 52: "zunmon_3019", 54: "zunmon_3022",
    56: "zunmon_3016", 62: "zunmon_3019", 66: "zunmon_3015",
    68: "zunmon_3015", 70: "zunmon_3022", 74: "zunmon_3015",
    76: "zunmon_3019", 80: "zunmon_3016",
}
MOTION = {
    3: "jump", 4: "shake", 5: "jump", 7: "jump", 12: "shake", 18: "shake",
    20: "shake", 22: "jump", 26: "jump", 28: "jump",
    35: "jump", 39: "jump", 43: "jump", 47: "jump",
    50: "jump", 52: "jump", 54: "jump", 62: "jump",
    70: "jump", 76: "shake", 80: "shake",
}
STYLE = {
    42: "ツンツン", 61: "ノーマル", 75: "ツンツン",
    20: "ツンツン", 52: "ツンツン",
}
YOMI = {29: "訳=ヤク", 31: "訳=ヤク", 61: "tokenizer=トークナイザー", 74: "訳=ヤク"}
INTONATION = {3: 1.3, 4: 1.2, 5: 1.3, 7: 1.2, 20: 1.3, 22: 1.25,
              43: 1.2, 50: 1.25, 52: 1.4, 76: 1.2, 79: 1.2, 81: 1.3, 83: 1.2}
GAP = {i: 2.4 for i in STARTS if i != 1}
GAP.update({3: 0.35, 4: 0.65, 5: 0.6, 7: 0.75, 8: 0.85, 23: 0.75, 32: 0.8, 43: 0.75,
            48: 15.0, 50: 4.0, 51: 0.8, 52: 0.65, 53: 0.8,
            57: 1.1, 63: 0.9, 71: 0.7, 78: 0.8, 79: 0.45})


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
