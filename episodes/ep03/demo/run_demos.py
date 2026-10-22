"""第3弾のデモの返事を、実際の流れ（めたんの声 → whisper-server → llama-server）で作る。

  python3 run_demos.py > demos.json

めたんの声は VOICEVOX で作り、whisper-server で文字にしてから voice-chat と同じ組み立てで LLM に渡す。
返事は作り直さず、1 回目に出たものを使う。
"""
import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

loader = importlib.machinery.SourceFileLoader("vc", os.path.expanduser("~/src/voice-chat/voice-chat"))
spec = importlib.util.spec_from_loader("vc", loader)
vc = importlib.util.module_from_spec(spec)
loader.exec_module(vc)
chars, _ = vc.load_characters()
ZUN, MET = chars["ずんだもん"], chars["四国めたん"]


def metan_wav(text, path):
    """めたん（ノーマル）の声を 16kHz モノラルで作る。"""
    q = urllib.parse.urlencode({"speaker": 2, "text": text})
    with urllib.request.urlopen(urllib.request.Request(f"{vc.VOICEVOX}/audio_query?{q}", method="POST")) as r:
        query = json.load(r)
    req = urllib.request.Request(f"{vc.VOICEVOX}/synthesis?speaker=2", data=json.dumps(query).encode(),
                                 headers={"Content-Type": "application/json"})
    with tempfile.NamedTemporaryFile(suffix=".wav") as raw:
        raw.write(urllib.request.urlopen(req).read())
        raw.flush()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw.name, "-ar", "16000", "-ac", "1", path], check=True)


def reply(system, history, text):
    body = {"model": vc.MODEL, "temperature": 0.7, "max_tokens": 300,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content": system}, *history, {"role": "user", "content": text}]}
    req = urllib.request.Request(vc.LLM, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["choices"][0]["message"]["content"].strip()


def heard(said):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "in.wav")
        metan_wav(said, path)
        return vc.transcribe(path)


ONE_LINE = "あなたはずんだもんです。"
PERSONA = ZUN["persona"].strip()
FULL = PERSONA + "\n" + vc.RULES.strip()
FULL_MET = MET["persona"].strip() + "\n" + vc.RULES.strip()

out = {}
rain = "明日は雨らしいんだけど、何して過ごそうかな"
for key, system, history, said in [
    ("open", FULL, [], rain),
    ("one_line", ONE_LINE, [], rain),
    ("persona", PERSONA, [], rain),
]:
    text = heard(said)
    out[key] = {"said": said, "heard": text, "reply": reply(system, history, text)}
    print(key, out[key], file=sys.stderr)

# 改善 3: 雨 → 映画 → またね（履歴つき）
hist = []
for key, said in [("rain", rain), ("movie", "映画かなあ。最近見てないし"), ("bye", "ありがとう、じゃあまたね")]:
    text = heard(said)
    r = reply(FULL, hist, text)
    hist += [{"role": "user", "content": text}, {"role": "assistant", "content": r}]
    out[key] = {"said": said, "heard": text, "reply": r}
    print(key, out[key], file=sys.stderr)

# 改善 5: 遮る（返事の頭だけ使う）、「(音楽)」に答える
for key, said in [("interrupt", "ずんだ餅の作り方を詳しく教えて")]:
    text = heard(said)
    out[key] = {"said": said, "heard": text, "reply": reply(FULL, [], text)}
out["music"] = {"said": "（無音）", "heard": "(音楽)", "reply": reply(FULL, [], "(音楽)")}

# 改善 7: めたんに交代して、お金の話
text = heard("めたんに代わって")
out["switch"] = {"said": "めたんに代わって", "heard": text, "reply": MET["greeting"]}
text = heard("最近お金がなくてさ")
out["money"] = {"said": "最近お金がなくてさ", "heard": text, "reply": reply(FULL_MET, [], text)}
for k in ("interrupt", "music", "switch", "money"):
    print(k, out[k], file=sys.stderr)
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
