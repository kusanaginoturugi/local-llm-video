"""明治の落語の速記を、手元の LLM（llama-server）に場面ごとに現代語に直させる。

使い方:
  python3 modernize.py                    # 翻刻（source/futari-guse.txt）を場面ごとに訳す
  python3 modernize.py --ocr ocr.txt      # 国会図書館の OCR の生の文字（ルビまじり）を 1 つの場面として訳す
  python3 modernize.py --example --scene 4  # 直し方の見本を足して、4 番目の場面だけ
  MODEL=gemma-4-E4B-it-qat python3 modernize.py

出力は llm/<モデル名>/ に、場面ごとの訳（NN.txt）と、条件・時間・finish_reason などの記録（run.json）。
"""
import argparse
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "source", "futari-guse.txt")
URL = os.environ.get("LLAMA_URL", "http://127.0.0.1:8080/v1/chat/completions")
MODEL = os.environ.get("MODEL", "gemma-4-12b-it-qat-imatrix")

SYSTEM = """あなたは、明治時代の落語の速記本を、今の人が読める言葉に直す編集者です。
入力は、柳家小さん（3代目）の『二人癖』の速記の一場面です。旧字・旧仮名で、話者は行の頭に書いてあります
（八＝八五郎、熊＝熊さん、主＝ご隠居、甲・乙＝まくらの小噺の二人、地＝地の文）。

次の決まりで、現代の話し言葉に直してください。
- 1 行に 1 つのせりふ。行の頭の話者の名前はそのまま残す。行を足したり、まとめたりしない。
- 旧字・旧仮名は、今の漢字と仮名づかいにする。読みにくい当て字は仮名にする。
- 江戸っ子の口調（「〜じゃねえか」「〜しねえ」）は、少しなら残してよい。
- 話の要は口癖の言葉遊び。熊の「詰まらねえ」、八の「飲める」、仕掛けの「詰まろうか」は、必ずその言葉のまま残す。
- 「（口へ入れる）」のような、かっこの中の動きの書きこみは残す。
- 〔 〕の中は翻刻者の注。訳には入れない。【p37】のようなページの印は消す。
- 説明や感想、前置きを付け足さない。直した本文だけを出す。"""

# --example のときに足す、直し方の見本（この 4 行は手で直した）
EXAMPLE = """
直し方の見本：
入力
八　何う爲たい熊、久しく逢はなかつたなア
熊　取つたつて詰らねへ
八　百本の大根が詰らうか
熊　夫りやア云ふ迄も無へ
出力
八　どうした熊、久しぶりだな。
熊　当たったって、詰まらねえ。
八　百本の大根が、詰まろうか。
熊　そりゃあ、言うまでもねえ。
「詰らうか」は「詰まるか」ではなく、必ず「詰まろうか」にする（「詰まるか」と聞くと「詰まない」と答えられてしまうので、仕掛けにならない）。
「夫」は「それ」、「何う」は「どう」、「爲る」は「する」と読む。旧仮名（云ふ、遣らう）は残さない。"""

SYSTEM_OCR = SYSTEM + """
入力は OCR で読み取った文字で、振り仮名が本文にまざり、読み間違いもあります。話者の印は「八「」のような形です。
振り仮名や読み間違いを取りのぞいて、話の筋が通るように直してください。"""


def scenes(path):
    """## の見出しごとに分ける。"""
    out, title, buf = [], None, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#") and not line.startswith("## "):
            continue
        if line.startswith("## "):
            if title:
                out.append((title, "\n".join(buf).strip()))
            title, buf = line[3:], []
        elif line.strip():
            buf.append(line)
    if title:
        out.append((title, "\n".join(buf).strip()))
    return out


def ask(system, text):
    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
        "max_tokens": 6000,
        "temperature": 0.3,
    }
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    t = time.time()
    res = json.load(urllib.request.urlopen(req, timeout=1800))
    return res, time.time() - t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr", help="OCR の生の文字のファイル（1 つの場面として訳す）")
    ap.add_argument("--example", action="store_true", help="直し方の見本をプロンプトに足す")
    ap.add_argument("--scene", type=int, action="append", help="この番号の場面だけ訳す（何度でも）")
    args = ap.parse_args()
    name = re.sub(r"[^\w.-]", "_", MODEL) + ("-ocr" if args.ocr else "") + ("-example" if args.example else "")
    outdir = os.path.join(HERE, "llm", name)
    os.makedirs(outdir, exist_ok=True)
    if args.ocr:
        jobs, system = [("OCR の生の文字", open(args.ocr, encoding="utf-8").read().strip())], SYSTEM_OCR
    else:
        jobs, system = scenes(SOURCE), SYSTEM
    if args.example:
        system += EXAMPLE
    numbered = [(i, t) for i, t in enumerate(jobs, 1) if not args.scene or i in args.scene]
    log = {"model": MODEL, "url": URL, "temperature": 0.3, "max_tokens": 6000, "system": system, "scenes": []}
    for i, (title, text) in numbered:
        res, sec = ask(system, text)
        c = res["choices"][0]
        out = c["message"]["content"].strip()
        with open(os.path.join(outdir, f"{i:02d}.txt"), "w", encoding="utf-8") as f:
            f.write(f"## {title}\n\n{out}\n")
        u = res.get("usage", {})
        rec = {"no": i, "title": title, "seconds": round(sec, 1), "finish_reason": c.get("finish_reason"),
               "prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens"),
               "lines_in": text.count("\n") + 1, "lines_out": out.count("\n") + 1}
        log["scenes"].append(rec)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
    with open(os.path.join(outdir, "run.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
