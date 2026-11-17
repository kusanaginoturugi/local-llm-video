"""番外編の台本から、章（screens.tsv）と演出（direction.tsv）を生成する。

落語なので、これまでの回より速く話し、行と行の間を詰める。間は、オチや言い間違いの前だけ空ける。
見た目は Live2D（第7弾と同じ）。react には Live2D の表情・モーションの名前を書く（characters.md の「見た目」）。
この PC にはモデルがないので、名前は下の EXP・MOTION_NAMES と照らし合わせるだけ。モデルでの確かめは render.py がする。
"""
import csv
from pathlib import Path

from build_script import parse

HERE = Path(__file__).parent
LINES, CHAPTERS = parse()
STARTS = dict(CHAPTERS)
NARRATION = {99, 217}  # めたんが語る地の文
OHAYASHI = {15: "out/debayashi/open_yose.wav", 268: "out/debayashi/close_yose.wav"}  # demo/debayashi.py で作る

SCREENS = {
    1: "タイトル", 4: "国会図書館の速記本", 9: "めくり『二人癖』", 15: "高座（出囃子）", 16: "熊さんの家",
    63: "ご隠居の家", 99: "語り", 100: "熊さんの家（ぬかだらけの八五郎）", 156: "ご隠居の家",
    199: "詰将棋の盤（歩三兵と桂香）", 217: "語り", 218: "八五郎の家（将棋盤）", 223: "王様は裸",
    256: "噺のあと", 260: "LLM の現代語訳", 262: "「詰まろうか」→「詰まるか」", 266: "普通に締める", 268: "追い出し（クレジット）",
}

# 話す速さ（VOICEVOX の speedScale）。これまでの回は めたん 1.0、ずんだもん 1.18、つむぎ 1.0
TALK = {"めたん": 1.05, "ずんだもん": 1.22, "つむぎ": 1.05}   # はじめにと噺のあと
HANASHI = {"めたん": 1.12, "ずんだもん": 1.28, "つむぎ": 1.12}  # 噺（16〜255 行）
SPEED = {99: 1.0, 217: 1.0,   # 語りは落ち着いて
         245: 1.0}            # 「これは、詰まらないわね」は、考え込んだあとで、ゆっくり

# 行の前の間（秒）。噺の中はふだん 0.2 秒（これまでの回は 0.35 秒）
HANASHI_GAP = 0.2
GAP = {
    8: 0.2,                       # 「言ったじゃん」はすかさず
    15: 1.0, 16: 0.6,             # 「はじまり、はじまり」→ 出囃子 → 噺
    18: 0.15, 42: 0.15,           # 「え？」
    46: 0.15, 49: 0.1, 50: 0.3,   # 「乗ったのだ」「けち」「二億万両」
    57: 0.5,                      # 手を締める
    60: 0.6,                      # 熊の家を出て、ひとり言
    63: 1.8, 156: 1.8,            # ご隠居の家へ（場面が変わる）
    99: 1.2, 217: 1.2,            # 語りの前
    100: 1.0, 218: 1.0,           # 語りのあと、熊が来る・八五郎の家
    111: 0.4, 113: 0.3,           # 「おばさんを百本」のあと
    122: 0.5, 124: 0.4,           # 「ははーん」「つま……はいり……」
    137: 0.4, 138: 0.15,          # 「飲めるのだ」→ すかさず「はい、言った」
    154: 0.7, 155: 0.3,           # 「あれは、うそ」
    164: 0.3, 170: 0.3, 172: 0.15,
    182: 0.4, 183: 0.15,          # 「火でも、つけるのだ？」→ すかさず
    226: 0.3, 237: 0.2, 238: 0.3,
    241: 0.6, 242: 0.8,           # 考え込む → 「詰まろうか」
    245: 1.0, 246: 0.1,           # 「これは、詰まらないわね」→ すかさず「やい、言ったのだ！」
    255: 0.5,                     # オチ
    256: 2.0,                     # 噺のあと
    262: 0.4, 265: 0.5, 266: 1.0, 268: 0.8,
}

# VOICEVOX のスタイル（めたん・ずんだもんだけ）
STYLE = {
    17: "ツンツン", 21: "ツンツン", 134: "ツンツン", 148: "ツンツン",   # 熊さんの「つまらない」「くだらない」
    62: "ささやき",                                                   # ひとり言で悪だくみ
    155: "なみだめ", 156: "なみだめ", 160: "なみだめ", 258: "なみだめ",
    226: "ささやき",                                                  # 「しめた、なのだ」は小声で（ヒソヒソは 10 dB 小さすぎた）
    265: "ヘロヘロ",
}
INTONATION = {98: 1.3, 153: 1.3, 170: 1.2, 209: 1.3, 246: 1.3, 254: 1.3, 261: 1.3, 267: 1.2,
              99: 0.9, 217: 0.9}  # 語りは抑揚を抑えて
MOTION = {98: "jump", 100: "shake", 134: "shake", 138: "jump", 139: "shake", 153: "shake", 183: "shake",
          209: "jump", 246: "jump", 249: "shake", 254: "jump", 255: "jump", 261: "jump", 267: "jump"}

# 表情。3 人とも Live2D の「表情+モーション」（その行のあいだだけ）。
# SD 絵の名前（zunmon_3017 など）は、その行だけ Live2D の代わりに SD 絵を出す（1 本に数回まで）
# 将棋のしぐさ：ずんだもんの pose_chop を、駒をパチンと打つ手に見立てる
REACT = {
    1: "pose_microphone", 2: "pose_Jaw+mtnBody_think", 3: "happy", 4: "exp_laugh+mtnBody_point", 5: "exp_surprise",
    6: "exp_wink+mtnBody_point", 7: "exp_angry+mtnBody_no", 8: "happy", 9: "exp_1", 10: "exp_laugh",
    14: "exp_wink+mtnBody_yes",
    # 二人の約束
    16: "exp_smile+mtnBody_wave", 17: "exp_sad+mtnFace_sad", 18: "exp_surprise+mtnFace_surprise", 20: "pose_cross",
    21: "exp_sad", 24: "exp_laugh+mtnBody_laugh", 26: "exp_laugh2", 27: "exp_angry+mtnBody_no", 28: "pose_cross",
    32: "exp_angry+mtnBody_point", 33: "exp_1+mtnBody_point", 34: "exp_surprise2+mtnBody_tremble",
    35: "exp_laugh2+mtnFace_laugh", 38: "exp_1", 39: "exp_angry", 40: "exp_angry+mtnBody_angry",
    41: "exp_laugh+mtnBody_point", 42: "exp_surprise", 44: "exp_1+mtnBody_think", 46: "pose_Upper",
    48: "exp_smile", 49: "exp_angry", 50: "pose_Upper", 51: "exp_angry2+mtnBody_no", 54: "exp_surprise2",
    55: "exp_wink+mtnBody_point", 57: "exp_laugh+mtnBody_yes", 60: "exp_laugh2+mtnFace_laugh", 61: "exp_laugh",
    62: "pose_Jaw+mtnBody_think",
    # ご隠居の知恵（一）
    63: "exp_smile+mtnBody_wave", 64: "happy", 67: "exp_shy", 71: "exp_sad2", 74: "angry", 76: "exp_shy",
    79: "exp_shy2+mtnFace_shy", 80: "happy", 81: "exp_laugh+mtnBody_yes", 83: "pose_Upper", 85: "exp_laugh",
    87: "exp_surprise", 88: "angry", 89: "pose_Jaw+mtnBody_think", 90: "happy", 94: "exp_laugh+mtnBody_yes",
    95: "angry", 97: "happy", 98: "exp_laugh2+mtnBody_laugh",
    # 一回目
    100: "exp_angry3+mtnBody_angry", 101: "exp_surprise+mtnFace_surprise", 104: "exp_angry+mtnBody_point",
    106: "pose_cross", 108: "pose_Jaw+mtnBody_think", 110: "exp_surprise2", 111: "exp_surprise+mtnFace_surprise",
    112: "exp_sad2", 113: "exp_laugh2+mtnFace_laugh", 114: "exp_angry", 121: "pose_Upper",
    122: "exp_angry+mtnBody_point", 124: "exp_surprise+mtnFace_surprise", 125: "exp_laugh2", 126: "exp_1",
    127: "exp_angry+mtnBody_point", 128: "exp_wink", 130: "pose_Waist", 131: "pose_chop",
    134: "exp_angry2+mtnBody_angry", 135: "exp_surprise", 136: "exp_sad4", 137: "exp_laugh+mtnBody_laugh",
    138: "exp_laugh2+mtnBody_point", 139: "exp_surprise2+mtnBody_tremble", 142: "exp_angry+mtnBody_no",
    145: "exp_sad3", 146: "exp_angry2", 149: "exp_sad2", 152: "exp_wink", 153: "exp_angry3+mtnBody_angry",
    154: "exp_laugh+mtnFace_laugh", 155: "zunmon_3017",
    # ご隠居の知恵（二）
    156: "exp_sad3", 157: "happy", 160: "exp_sad2+mtnFace_sad", 162: "exp_sad", 164: "happy", 166: "exp_angry",
    171: "exp_angry+mtnBody_point", 172: "angry", 175: "pose_Jaw", 177: "exp_angry3+mtnBody_tremble",
    179: "happy", 180: "exp_laugh", 182: "pose_Upper", 183: "angry", 186: "pose_Jaw+mtnBody_think",
    188: "exp_laugh+mtnBody_yes", 189: "happy", 190: "exp_sad", 192: "exp_smile", 198: "exp_smile",
    202: "exp_laugh+mtnBody_yes", 204: "exp_laugh2", 209: "exp_laugh2+mtnBody_laugh", 211: "pose_Upper",
    216: "exp_smile+mtnBody_wave",
    # 二回目
    218: "pose_chop+mtnBody_think", 219: "exp_laugh", 220: "pose_Jaw+mtnBody_think", 221: "exp_surprise",
    222: "pose_chop", 223: "exp_1+mtnBody_point", 224: "exp_laugh", 225: "exp_1", 226: "exp_laugh2+mtnFace_laugh",
    227: "exp_1+mtnBody_think", 228: "exp_angry+mtnBody_point", 229: "exp_laugh2+mtnFace_laugh", 230: "exp_sad",
    232: "exp_smile", 233: "exp_1+mtnBody_think", 234: "exp_surprise2+mtnBody_tremble", 235: "exp_angry",
    236: "pose_Jaw", 237: "exp_1", 238: "exp_laugh+mtnBody_yes", 239: "exp_1+mtnBody_think", 240: "exp_laugh2",
    241: "exp_sad4+mtnBody_think", 242: "exp_laugh2+mtnFace_laugh", 243: "exp_1+mtnBody_think",
    244: "exp_laugh2+mtnBody_point", 245: "exp_sad+mtnFace_sad", 246: "exp_laugh2+mtnBody_laugh",
    247: "exp_surprise+mtnFace_surprise", 248: "exp_laugh+mtnBody_wave", 249: "exp_angry2+mtnBody_angry",
    250: "exp_angry", 251: "exp_sad4", 253: "exp_sad3+mtnBody_no", 254: "exp_laugh2+mtnBody_laugh",
    255: "exp_wink+mtnBody_point",
    # 噺のあと
    256: "happy", 257: "exp_wink", 258: "exp_sad3+mtnFace_sad", 260: "exp_1", 261: "pose_Upper",
    262: "exp_sad4", 264: "exp_1+mtnBody_yes", 265: "exp_sad3", 266: "exp_laugh+mtnBody_yes",
    267: "exp_laugh+mtnBody_wave",
}

# つむぎ（坂本アヒル式。上の REACT の angry / happy は、SD 絵のころの書き方の名残なので、ここで置き換える）
TSUMUGI = {
    3: "exp_laugh", 8: "exp_laugh2+mtnFace_laugh", 11: "pose_pointing", 13: "exp_angry2",
    64: "exp_wink", 68: "exp_1", 74: "exp_angry", 78: "exp_1+mtnBody_no", 80: "pose_peacesign",
    88: "exp_angry2+mtnFace_angry", 90: "pose_pointing+mtnBody_point", 95: "exp_angry+mtnBody_no", 97: "exp_wink",
    157: "exp_laugh+mtnFace_laugh", 164: "exp_laugh3+mtnBody_laugh", 170: "exp_laugh2+mtnBody_laugh",
    172: "exp_angry+mtnBody_no", 179: "exp_1+mtnBody_think", 183: "exp_angry2+mtnBody_angry", 189: "exp_laugh",
    193: "exp_surprise", 207: "pose_pointing", 213: "pose_peacesign",
    256: "exp_surprise2+mtnFace_surprise", 259: "exp_laugh+mtnFace_laugh", 263: "exp_angry+mtnBody_no",
}
REACT.update(TSUMUGI)

# Live2D のモデルにある名前（characters.md の「見た目」と、つむぎのモデルの model3.json から）。書き間違いをここで止める
EXP = {
    "めたん": {"exp_laugh", "exp_laugh2", "exp_sad", "exp_sad2", "exp_sad3", "exp_sad4", "exp_angry", "exp_angry2",
              "exp_angry3", "exp_shy", "exp_shy2", "exp_surprise", "exp_wink", "exp_1", "exp_2", "exp_3", "exp_4",
              "exp_5", "exp_6", "pose_Middle", "pose_Waist", "pose_manju", "pose_microphone"},
    "ずんだもん": {"exp_smile", "exp_laugh", "exp_laugh2", "exp_sad", "exp_sad2", "exp_sad3", "exp_angry", "exp_angry2",
                "exp_angry3", "exp_shy", "exp_shy2", "exp_surprise", "exp_surprise2", "exp_sleep", "exp_01", "exp_02",
                "exp_03", "exp_04", "exp_05", "pose_Upper", "pose_cross", "pose_chop", "pose_Jaw"},
    "つむぎ": {"exp_1", "exp_2", "exp_3", "exp_4", "exp_angry", "exp_angry2", "exp_laugh", "exp_laugh2", "exp_laugh3",
             "exp_sad", "exp_sad2", "exp_sad3", "exp_shy", "exp_shy2", "exp_surprise", "exp_surprise2", "exp_wink",
             "pose_Middle", "pose_Middle2", "pose_Middle3", "pose_peacesign", "pose_peacesign2", "pose_peacesign3",
             "pose_pointing"},
}
EXTRA_MOTIONS = {"ずんだもん": {"mtnBody_wave"}, "つむぎ": {"mtnFace_angry", "mtnBody_peacesign"}}
MOTION_NAMES = {"mtnBody_angry", "mtnBody_laugh", "mtnBody_no", "mtnBody_point", "mtnBody_think", "mtnBody_tremble",
                "mtnBody_yes", "mtnFace_laugh", "mtnFace_sad", "mtnFace_shy", "mtnFace_surprise"}
SD = {p.stem for p in (HERE.parent.parent / "assets" / "official" / "sd").glob("*.png")}


def check(no, speaker, react):
    if not react:
        return
    if react in SD:
        return
    names = react.split("+")
    exps = [n for n in names if n in EXP[speaker]]
    motions = [n for n in names if n in MOTION_NAMES | EXTRA_MOTIONS.get(speaker, set())]
    assert len(exps) + len(motions) == len(names) and len(exps) <= 1 and len(motions) <= 1, (no, speaker, react)


def section_of(no):
    return max(s for s in STARTS if s <= no)


def write(name, header, rows):
    with (HERE / name).open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def speed(no, speaker):
    if speaker == "お囃子":
        return ""
    return SPEED.get(no, (HANASHI if 16 <= no <= 255 else TALK)[speaker])


def gap(no):
    if no in GAP:
        return GAP[no]
    return HANASHI_GAP if 16 <= no <= 255 else ""


section = ""
screens = []
for no, (speaker, text) in enumerate(LINES, 1):
    section = STARTS.get(no, section)
    screens.append((no, section, speaker, SCREENS.get(no, "")))
    check(no, speaker, REACT.get(no, ""))
    assert (speaker == "お囃子") == (no in OHAYASHI), (no, speaker)
    assert no not in NARRATION or speaker == "めたん", no
    assert no not in STYLE or speaker in ("めたん", "ずんだもん"), no
write("screens.tsv", ("no", "section", "speaker", "screen"), screens)
write("direction.tsv",
      ("no", "speaker", "style", "intonation", "speed", "gap", "motion", "react", "sound", "yomi", "kana", "memo"),
      ((no, speaker, STYLE.get(no, ""), INTONATION.get(no, ""), speed(no, speaker), gap(no), MOTION.get(no, ""),
        REACT.get(no, ""), OHAYASHI.get(no, ""), "", "", "語り" if no in NARRATION else "")
       for no, (speaker, text) in enumerate(LINES, 1)))
