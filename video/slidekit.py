"""回ごとの slides.py で使う画面の部品。台本の行番号ごとに出す画面を SLIDES に書き、指定のない行は直前の画面を引き継ぐ。

種類:
  title(大見出し, 小見出し)
  image(ファイル名)            その回の slides/ の画像
  term(行のリスト, hl=強調する行番号)   ターミナル風
  code(見出し, 行のリスト, hl=...)     設定ファイルなど
  table(見出し, ヘッダー, 行, hl=...)
  bullets(見出し, 項目)
  big(文字)                     大きな一文
  flow(見出し, 箱, hl=..., notes=...)  箱を矢印でつなぐ流れ図。箱は (名前, 説明…)、notes は (ラベル, 文, 強調するか)
  todo(説明)                    まだ録っていない画面の仮置き
  chat(見出し, 発言, hl=...)     会話の吹き出し。発言は (話し手, 文)。話し手が「あなた」なら右、それ以外は左
"""


def title(main, sub=""):
    return ("title", main, sub)


def image(name):
    return ("image", name)


def term(lines, hl=()):
    return ("term", lines, set(hl))


def code(head, lines, hl=()):
    return ("code", head, lines, set(hl))


def table(head, header, rows, hl=()):
    return ("table", head, header, rows, set(hl))


def bullets(head, items):
    return ("bullets", head, items)


def big(text):
    return ("big", text)


def todo(text):
    return ("todo", text)


def flow(head, boxes, hl=(), notes=()):
    return ("flow", head, boxes, set(hl), list(notes))


def chat(head, msgs, hl=()):
    return ("chat", head, list(msgs), set(hl))
