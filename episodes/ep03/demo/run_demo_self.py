"""まとめのデモ: 解説のずんだもんの声で、パソコンのずんだもんに話しかける。demos.json に足す。

  python3 run_demo_self.py

run_demos.py と同じく、声 → whisper-server → llama-server の流れで、1 回目の返事を使う。
"""
import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request

import run_demos as rd  # noqa: E402  （読み込むと run_demos.py のデモも走るので、関数だけ使えるようにしてある）

HERE = os.path.dirname(os.path.abspath(__file__))
vc, ZUN = rd.vc, rd.ZUN


def zundamon_wav(text, path):
    """解説のずんだもん（ノーマル、速さ 1.18）の声を 16kHz モノラルで作る。"""
    q = urllib.parse.urlencode({"speaker": 3, "text": text})
    with urllib.request.urlopen(urllib.request.Request(f"{vc.VOICEVOX}/audio_query?{q}", method="POST")) as r:
        query = json.load(r)
    query["speedScale"] = 1.18
    req = urllib.request.Request(f"{vc.VOICEVOX}/synthesis?speaker=3", data=json.dumps(query).encode(),
                                 headers={"Content-Type": "application/json"})
    with tempfile.NamedTemporaryFile(suffix=".wav") as raw:
        raw.write(urllib.request.urlopen(req).read())
        raw.flush()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw.name, "-ar", "16000", "-ac", "1", path], check=True)


def heard(said):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "in.wav")
        zundamon_wav(said, path)
        return vc.transcribe(path)


path = os.path.join(HERE, "demos.json")
demos = json.load(open(path))
said = "ずんだもんに代わって"
demos["self_switch"] = {"said": said, "heard": heard(said), "reply": ZUN["greeting"]}
said = "ボクもずんだもんなのだ。オマエは本物のずんだもんなのだ？"
text = heard(said)
demos["self_talk"] = {"said": said, "heard": text, "reply": rd.reply(rd.FULL, [], text)}
json.dump(demos, open(path, "w"), ensure_ascii=False, indent=1)
for k in ("self_switch", "self_talk"):
    print(k, demos[k])
