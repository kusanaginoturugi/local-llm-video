"""第3弾の画面。台本の行番号ごとに出す画面で、指定のない行は直前の画面を引き継ぐ。

デモの会話は demo/demos.json（実際に voice-chat と同じ流れで出した返事）を、数字は記事の実測を写したもの。
"""
import json
import os

from slidekit import big, bullets, chat, code, flow, table, term, title  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = json.load(open(os.path.join(HERE, "demo", "demos.json")))
YOU = "あなた（ひまり）"


def said(key):
    return (YOU, DEMO[key]["heard"])


def answer(key, who="ずんだもん"):
    return (who, DEMO[key]["reply"])


HEAD = "voice-chat（SUPER + SHIFT + H で話しかける）"

BOXES = [
    ("録音", "キーで開始・終了", "pw-record"),
    ("whisper-server", "声を文字に", "第2弾"),
    ("llama-server", "返事を考える", "第1弾"),
    ("VOICEVOX", "1 文ずつ声に", "今回"),
    ("再生", "pw-play", "次の文を合成中"),
]


def diagram(hl=(), note=True):
    notes = [("声が出るまで", "約 0.2 秒（GPU 版の VOICEVOX）", True)] if note else []
    return flow("話しかけると、声で返事が返ってくる", BOXES, hl=hl, notes=notes)


STEPS = ("改善の記録", ["改善", "やったこと", "結果"], [
    ["1", "まず素直につなぐ", "1.83 秒。ずんだもんにならない"],
    ["2", "人物像を書く", "一人称と語尾がずんだもんに"],
    ["3", "会話の決まりを足す", "短く話し、最後に質問する"],
    ["4", "1 文ずつ読む", "0.95 秒"],
    ["5", "使ってみて見つかった穴をふさぐ", "割り込み・履歴・「(音楽)」"],
    ["6", "VOICEVOX を GPU 版にする", "0.22 秒"],
    ["7", "名前を呼んでキャラを交代する", "めたん・つむぎとも話せる"],
])
PERSONA = [
    "[[character]]",
    'name = "ずんだもん"',
    "speaker = 3       # VOICEVOX の声の番号",
    'persona = """',
    "あなたは「ずんだもん」です。ずんだ餅の精で、年齢の概念はありません。",
    "やや不幸属性があり、ないがしろにされることもしばしばです。",
    "その辺をふらふらすることと、自分を大きく見せることが趣味です。",
    "一人称は「ボク」か「ずんだもん」、相手のことは「オマエ」と呼びます。",
    "語尾に「〜のだ」「〜なのだ」をつけて話します。",
    '"""',
]
RULES = [
    "これは音声での会話です。返事は読み上げられるので、次のことを守ってください。",
    "・1〜3 文の短い話し言葉で返す。",
    "・箇条書き、見出し、記号、絵文字、URL は使わない。",
    "・数字や英語は、読み上げやすい書き方にする。",
    "・会話が続くよう、最後に相手への短い質問を 1 つ添える。",
    "・相手が話を終えようとしているとき（おやすみ、ありがとう、またね等）は、",
    "  質問せずに気持ちよく締める。",
]
STREAM = [
    "$ curl -sN http://127.0.0.1:8080/v1/chat/completions -d @req_stream.json",
    'data: {"choices":[{"delta":{"content":"ボ"}}], ...}',
    'data: {"choices":[{"delta":{"content":"ク"}}], ...}',
    'data: {"choices":[{"delta":{"content":"は"}}], ...}',
    "   …",
    "data: [DONE]",
]
MEDIANS = ("声が出るまで（中央値・5 つの話しかけ）", ["", "返事を全部待ってから読む", "1 文ずつ読む"], [
    ["VOICEVOX CPU 版", "1.83 秒", "0.95 秒"],
    ["VOICEVOX GPU 版", "0.38 秒", "0.22 秒"],
])
PER_PROMPT = ("1 文ずつ読む場合の、声が出るまで", ["話しかけ", "CPU 版", "GPU 版"], [
    ["雨の日の過ごし方", "1.04 秒", "0.26 秒"],
    ["疲れている", "0.88 秒", "0.14 秒"],
    ["おすすめの晩ごはん", "1.01 秒", "0.22 秒"],
    ["ずんだ餅の作り方", "0.59 秒", "0.18 秒"],
    ["週末の行き先", "0.95 秒", "0.22 秒"],
])
VRAM = ("VRAM（RTX 4070、12GB）", ["部品", "VRAM"], [
    ["llama-server（gemma-4-E4B-it qat）", "5,490 MiB"],
    ["whisper-server（medium）", "2,180 MiB"],
    ["VOICEVOX ENGINE（GPU 版）", "770 MiB"],
    ["合計（ブラウザなども含む）", "9,325 / 12,282 MiB"],
])
TOML = [
    "[[character]]",
    'name = "四国めたん"',
    'aliases = ["めたん", "メタン", "四国めたん"]   # 文字起こしでこう書かれても同じキャラ',
    "speaker = 2",
    'greeting = "四国めたんよ。わたくしに何か用かしら？"',
    'persona = """ … """',
]

rain = [said("rain"), answer("rain")]
movie = rain + [said("movie"), answer("movie")]
bye = movie + [said("bye"), answer("bye")]
switch = [said("switch"), answer("switch", "四国めたん")]
money = switch + [said("money"), answer("money", "四国めたん")]
interrupt_head = DEMO["interrupt"]["reply"].split("。")[0] + "。"
ME = "あなた（解説のずんだもん）"
self1 = [(ME, DEMO["self_switch"]["heard"]), answer("self_switch")]
self2 = self1 + [(ME, DEMO["self_talk"]["heard"]), answer("self_talk")]

SLIDES = {
    1: title("ローカル LLM で遊ぼう", "第3弾：声で話しかけると声で返事をする AI"),
    4: bullets("voice-chat に話しかける役", ["冥鳴ひまり（VOICEVOX）",
                                         "解説のめたん・ずんだもんとは別の声で話しかける",
                                         "返事をするのは、パソコンの中の voice-chat"]),
    7: chat(HEAD, []),
    8: chat(HEAD, [said("open")]),
    9: chat(HEAD, [said("open"), answer("open")], hl=[1]),
    13: diagram(hl=[]),
    15: big("RTX 4070・VRAM 12GB"),
    20: table(*STEPS),
    21: diagram(note=False),
    22: diagram(hl=[1], note=False),
    23: diagram(hl=[2], note=False),
    24: diagram(hl=[3], note=False),
    31: term(["$ docker pull voicevox/voicevox_engine:cpu-latest",
              "$ docker run -d --name voicevox --restart unless-stopped \\",
              "    -p 127.0.0.1:50021:50021 voicevox/voicevox_engine:cpu-latest",
              "$ curl http://127.0.0.1:50021/version",
              '"0.25.2"']),
    32: term(['$ curl -s -X POST "http://127.0.0.1:50021/audio_query?speaker=3" \\',
              '    --get --data-urlencode "text=こんにちは、ずんだもんなのだ" > query.json',
              '$ curl -s -H "Content-Type: application/json" -X POST -d @query.json \\',
              '    "http://127.0.0.1:50021/synthesis?speaker=3" -o zunda.wav',
              "$ pw-play zunda.wav"]),
    35: big("GPU 版の入れ方は、概要欄の記事へ"),
    37: title("改善 1：まず素直につなぐ", "部品を順番に呼ぶだけ"),
    38: code("システムプロンプト", ["あなたはずんだもんです。"]),
    41: chat(HEAD, [said("one_line")]),
    42: chat(HEAD, [said("one_line"), answer("one_line")], hl=[1]),
    45: big("話し終えてから声が出るまで 1.83 秒"),
    48: title("改善 2：人物像を書く", "LLM はずんだもんを知らない"),
    49: bullets("人物像なしで「ずんだもんってどんなキャラクター？」", [
        "東北地方の枝豆（ずんだ）をモチーフにした、かわいらしく元気なキャラクター",
        "一人称：「ずんだもん」（名前をそのまま使う）、「あたし」",
        "「〜のだ」には触れない"]),
    51: bullets("人物像なしで「四国めたんってどんなキャラクター？」", [
        "「申し訳ありませんが、「四国めたん」というキャラクターについて、私の知識の中には具体的な情報がありません。」"]),
    54: code("characters.toml（ずんだもんの人物像・抜粋）", PERSONA, hl=[4, 5, 6, 7, 8]),
    55: bullets("公式のプロフィール（VOICEVOX ボイボ寮・zunko.jp）", [
        "ずんだ餅の精。年齢の概念なし",
        "やや不幸属性があり、ないがしろにされることもしばしば",
        "趣味：その辺をふらふらすること、自分を大きく見せること",
        "一人称：ずんだもん、僕／二人称：オマエ"]),
    61: chat(HEAD, [said("persona")]),
    62: chat(HEAD, [said("persona"), answer("persona")], hl=[1]),
    65: title("改善 3：会話の決まりを足す", "読み上げ向けに、短く、最後に質問"),
    67: code("会話の決まり（全キャラ共通）", RULES),
    68: code("会話の決まり（全キャラ共通）", RULES, hl=[4]),
    71: chat(HEAD, [said("rain")]),
    72: chat(HEAD, rain, hl=[1]),
    73: chat(HEAD, rain + [said("movie")]),
    74: chat(HEAD, movie, hl=[3]),
    77: chat(HEAD, movie + [said("bye")]),
    78: chat(HEAD, bye, hl=[5]),
    80: table("質問の語尾が「〜のだ？」になる割合", ["質問の語尾の決まり", "質問の数", "「〜のだ？」"], [
        ["なし", "24 個", "18 個（75%）"], ["あり", "31 個", "30 個（97%）"]], hl=[1]),
    82: big("全文と書き方のコツは、概要欄の記事へ"),
    83: title("改善 4：1 文ずつ読む", "どこに時間がかかっている？"),
    85: table("声が出るまでの内訳（返事を全部待つ作り）", ["", "かかった時間"], [
        ["返事を書く（llama-server）", "0.21〜0.33 秒"],
        ["声を作る（VOICEVOX CPU 版）", "1.2〜1.9 秒"]], hl=[1]),
    88: term(STREAM, hl=[1, 2, 3]),
    89: flow("1 文できたら、すぐ読み始める", [
        ("llama-server", "少しずつ届く", "「。」で 1 文に"),
        ("VOICEVOX", "1 文ずつ声に", "次の文も先に"),
        ("再生", "読み始める", "その間に次を合成")]),
    91: big("1.83 秒 → 0.95 秒"),
    93: title("改善 5：使ってみて見つかった穴をふさぐ", "作っているときには気づかない"),
    96: chat(HEAD, [said("interrupt")]),
    97: chat(HEAD, [said("interrupt"), ("ずんだもん", interrupt_head + "\n（ここでキーを押して止める）")], hl=[1]),
    105: chat(HEAD, [(YOU, "（何も言わずにキーを押した）\n文字起こし：(音楽)")]),
    106: chat(HEAD, [(YOU, "（何も言わずにキーを押した）\n文字起こし：(音楽)"), answer("music")], hl=[1]),
    110: title("改善 6：VOICEVOX を GPU 版にする", "声を作る時間を減らす"),
    113: table(*PER_PROMPT),
    115: table(*MEDIANS, hl=[1]),
    116: big("GPU 版の入れ方は、概要欄の記事へ"),
    117: big("1.83 秒 → 0.95 秒 → 0.22 秒"),
    118: title("改善 7：名前を呼んでキャラを交代する", "ずんだもん・めたん・つむぎ"),
    119: code("characters.toml（めたん・抜粋）", TOML, hl=[2]),
    121: chat(HEAD, [said("switch")]),
    122: chat(HEAD, switch, hl=[1]),
    126: chat(HEAD, switch + [said("money")]),
    127: chat(HEAD, money, hl=[3]),
    129: bullets("四国めたん（VOICEVOX ボイボ寮より）", [
        "高等部二年生、17 歳。常に金欠。趣味は中二病妄想",
        "誰にでも遠慮しないので、基本的にタメ口",
        "性格は若干ツンデレ気味",
        "一人称：わたくし／二人称：貴女、アンタ"]),
    139: table(*STEPS),
    140: table(*VRAM, hl=[3]),
    143: bullets("概要欄にあるもの", ["コード：github.com/kusanaginoturugi/voice-chat",
                                   "記事：声で話しかけると声で返事をする AI（作り方の詳細）"]),
    145: chat(HEAD, []),
    146: chat(HEAD, self1[:1]),
    147: chat(HEAD, self1, hl=[1]),
    148: chat(HEAD, self2[:3]),
    149: chat(HEAD, self2, hl=[3]),
    153: title("ご視聴ありがとうございました",
               "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん / VOICEVOX:冥鳴ひまり / イラスト: 東北ずん子・ずんだもんプロジェクト公式素材をもとに作成"),
}
