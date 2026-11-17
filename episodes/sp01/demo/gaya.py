"""追い出し太鼓に、客席のがや（笑い声と、帰りぎわのおしゃべり）を重ねる。拍手は試したが、やめた（applause の説明）。

制作者：「太鼓だけだとちょっとさみしい。がやをいれて試してみよう」。
声は、動画に出ているめたん・ずんだもん・つむぎの VOICEVOX の声だけを使う（クレジットが増えない）。
スタイル・声の高さ・速さを変えて別の人に聞こえるようにし、何十個も重ねる。拍手は手拍子の音を合成する。
重ねたあと、出囃子と同じ「寄席で鳴っている音」の加工（debayashi.py の YOSE）をかける。

  python3 debayashi.py && python3 gaya.py   # → ../out/debayashi/gaya.wav、close_gaya.wav、close_gaya_yose.wav
  SEED=3 python3 gaya.py                     # 別の並びにする
  BED=1 python3 gaya.py                      # 拍手の下に General MIDI の Applause を薄く敷く

VOICEVOX（127.0.0.1:50021）が動いていること。
"""
import io
import json
import os
import random
import subprocess
import urllib.parse
import urllib.request
import wave

import numpy as np

import debayashi

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out", "debayashi")
ENGINE = os.environ.get("VOICEVOX", "http://127.0.0.1:50021")
SEED = int(os.environ.get("SEED", "11"))
BED = os.environ.get("BED", "") == "1"  # 1 なら、Hand Clap の下に Applause の音色を敷く
SR = 48000

# めたん（ノーマル・あまあま・ツンツン・セクシー）、ずんだもん（ノーマル・あまあま・ツンツン・セクシー）、つむぎ
STYLES = [2, 0, 6, 4, 3, 1, 7, 5, 8]
# 終演後の客席。笑い声は始めのほうに多く、帰り支度の話はあとのほうに
LAUGHS = ["あはは", "あははは", "ははっ", "ふふふ", "あっはっは", "いやあ、笑った"]
TALKS = ["面白かったねえ", "詰まろうか、だってさ", "最後の、一杯飲めるのだ、よかったね", "帰りに、おそば食べてこうか",
         "寒いねえ", "お茶でも飲んでく？", "ずんだもん、取られっぱなしだったね", "あー、おなかすいた", "次は、いつかな",
         "傘、どこ置いたっけ", "押さないで、押さないで", "はいはい、出ます出ます", "楽しかったね", "また来ようね",
         "所沢の藤吉さん、だって", "おばさんを百本、だもんね", "下駄、どれだっけ", "ちょっと待ってよ"]


def post(path, params, body=None):
    url = f"{ENGINE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else b"", method="POST",
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=60).read()


def voice(text, rnd):
    """別の人に聞こえるよう、声の高さ・速さ・抑揚をばらして合成し、48kHz の float の配列で返す。"""
    style = rnd.choice(STYLES)
    q = json.loads(post("/audio_query", {"speaker": style, "text": text}))
    q.update(pitchScale=rnd.uniform(-0.12, 0.06), speedScale=rnd.uniform(1.0, 1.3),
             intonationScale=rnd.uniform(0.8, 1.3), volumeScale=1.0, outputSamplingRate=SR,
             prePhonemeLength=0.0, postPhonemeLength=0.05)
    with wave.open(io.BytesIO(post("/synthesis", {"speaker": style}, q))) as w:
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return pcm


def place(mix, sig, at, gain, pan):
    """sig を at 秒から、左右 pan（-1〜1）に振って足す。"""
    i = int(at * SR)
    n = min(len(sig), len(mix) - i)
    if n <= 0:
        return
    left, right = gain * (1 - pan) / 2 ** 0.5, gain * (1 + pan) / 2 ** 0.5
    mix[i:i + n, 0] += sig[:n] * left
    mix[i:i + n, 1] += sig[:n] * right


def fluid(song, name):
    """debayashi の Song を fluidsynth で鳴らし、48kHz・モノラルの float の配列で返す（残響つき）。"""
    mid, wav = os.path.join(OUT, name + ".mid"), os.path.join(OUT, name + ".wav")
    song.write(mid)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.7", "-r", str(SR), "-F", wav, debayashi.SF2, mid],
                   check=True, stderr=subprocess.DEVNULL)
    with wave.open(wav) as w:
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    os.remove(mid), os.remove(wav)
    pcm = pcm.reshape(-1, 2).mean(axis=1)
    return pcm / max(1e-6, float(np.abs(pcm).max()))


HAND_CLAP, APPLAUSE = 39, 126  # General MIDI：打楽器の Hand Clap と、音色の Applause


def applause(mix, rnd, start, people=10, bed=False, mute=False):
    """拍手。サウンドフォント（FluidR3）の Hand Clap で、ひとり分ずつ鳴らして重ねる。
    ひとりずつ、1 秒に 4〜6 回、少しずつずれて手をたたき、2.5〜5 秒でだんだん弱くやめる。左右と大きさも人ごとに変える。
    最初は短いノイズを並べて合成したが、「火がぼうぼう燃えているような音」（制作者）だったのでやめた。
    bed=True なら、General MIDI の Applause の音色を下に薄く敷く。
    サウンドフォントの手拍子も「遠くで爆竹が鳴ってる」（制作者）ので、拍手はやめた（mute=True）。
    mute でも乱数は同じだけ引くので、あとのおしゃべりの並びは拍手があったときと変わらない。"""
    for k in range(people):
        song = debayashi.Song(tempo=120, seed=rnd.randrange(1 << 30))  # 1 拍 0.5 秒。Song が人の揺らぎも足す
        rate, t = rnd.uniform(4, 6), start + rnd.uniform(0, 0.6)
        stop = t + rnd.uniform(2.5, 5.0)
        while t < stop:
            fade = max(0.0, 1 - (t - start) / (stop - start + 0.01)) ** 0.7
            song.note(debayashi.CH_DRUM, t * 2, HAND_CLAP, 0.1, max(20, round(110 * fade * rnd.uniform(0.75, 1.0))))
            t += 1 / rate * rnd.uniform(0.85, 1.15)
        # 「遠くで爆竹が鳴ってる」（制作者）ので、手拍子だけ 8 dB 小さく（0.06〜0.12 → 0.024〜0.048）
        gain, pan = rnd.uniform(0.024, 0.048), rnd.uniform(-0.9, 0.9)
        if not mute:
            place(mix, fluid(song, f"clap{k}"), 0.0, gain, pan)
    if bed:
        song = debayashi.Song(tempo=120, seed=rnd.randrange(1 << 30))
        song.program(0, APPLAUSE)
        song.note(0, start * 2, 60, 8.0, 90)  # 4 秒
        bed_pcm = fluid(song, "applause")
        n = len(bed_pcm)
        bed_pcm *= np.clip((n - np.arange(n)) / (1.5 * SR), 0, 1)  # 最後の 1.5 秒で消える
        place(mix, bed_pcm, 0.0, 0.05, 0.0)


def main():
    rnd = random.Random(SEED)
    close = os.path.join(OUT, "close.wav")
    with wave.open(close) as w:
        length = w.getnframes() / w.getframerate()
    mix = np.zeros((int(length * SR), 2), dtype=np.float32)
    applause(mix, rnd, start=0.0, bed=BED, mute=True)  # 拍手はやめた（笑い声とおしゃべりだけ）
    # 笑い声は最初の 4 秒に、おしゃべりは 1 秒目から、終わりの 1 秒前まで
    for text in rnd.sample(LAUGHS, len(LAUGHS)):
        place(mix, voice(text, rnd), rnd.uniform(0.0, 4.0), rnd.uniform(0.08, 0.16), rnd.uniform(-0.9, 0.9))
    for k in range(34):
        at = rnd.uniform(1.0, length - 1.0)
        far = rnd.random() < 0.6  # 遠くの声は小さく
        place(mix, voice(rnd.choice(TALKS), rnd), at, rnd.uniform(0.03, 0.07) if far else rnd.uniform(0.08, 0.14),
              rnd.uniform(-1, 1))
    # 終わりに向けて、客が出ていってだんだん静かに（最後の 3 秒で絞る）
    tail = np.clip((length - np.arange(len(mix)) / SR) / 3.0, 0, 1).astype(np.float32)
    mix *= tail[:, None]
    mix /= max(1.0, float(np.abs(mix).max()) / 0.9)
    gaya = os.path.join(OUT, "gaya.wav")
    with wave.open(gaya, "wb") as w:
        w.setnchannels(2), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(gaya)
    # 太鼓（加工する前の close.wav）に重ねてから、寄席っぽい音にする。がやはまばらで平均が低いので、
    # 最初は平均で太鼓より 8 dB 小さくしたが、「火がぼうぼう燃えているような音」（制作者）なので、さらに 8 dB 絞った
    # （割れないよう太鼓は下げておき、YOSE で全体をそろえ直す）
    out = os.path.join(OUT, "close_gaya.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", close, "-i", gaya, "-filter_complex",
                    "[0:a]volume=-4dB[d];[1:a]volume=-4dB[g];[d][g]amix=inputs=2:normalize=0:duration=first[a]", "-map", "[a]", out],
                   check=True)
    print(out)
    debayashi.yose(out)


if __name__ == "__main__":
    main()
