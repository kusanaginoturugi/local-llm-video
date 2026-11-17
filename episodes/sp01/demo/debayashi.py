"""番外編の出囃子と追い出し太鼓を、MIDI に書いて fluidsynth で鳴らす。

旋律はホルスト「木星」中間部（Thaxted）の頭の 2 小節（episodes/ep03/jupiter.txt と同じ書き起こし）。
ホルスト（1934 年没）の原曲は保護期間が切れている。後の人の編曲や歌詞は使わない。
音色は General MIDI の三味線・太鼓・笛と、サウンドフォントは FluidR3（MIT、Arch の soundfont-fluid）。

  python3 debayashi.py          # → ../out/debayashi/open.wav、close.wav（太鼓だけ）、close_melody.wav（旋律つき）。MIDI も同じ場所
  SEED=3 python3 debayashi.py   # 揺らぎの乱数を変える

それぞれ、寄席で鳴っているような音に加工した *_yose.wav も作る（YOSE）。

人が弾いたように、音の出だし・強さ・長さを少しずつばらつかせ、テンポもゆっくり伸び縮みさせる（WOBBLE）。
揺れは弾きはじめがいちばん大きく、終わりに向けて小さくなって、最後はぴったり合う（Song.loose）。
"""
import math
import os
import random
import re
import struct
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out", "debayashi")
SF2 = os.environ.get("SF2", "/usr/share/soundfonts/FluidR3_GM.sf2")
TPQ = 480  # 4 分音符 1 つの tick
SEED = int(os.environ.get("SEED", "7"))  # 揺らぎの乱数の種。変えると別の「下手さ」になる

# General MIDI の音色（0 始まり）とチャンネル
SHAMISEN, FUE, TAIKO = 106, 73, 116  # 三味線、フルート（篠笛の代わり）、太鼓
CH_SHAMI, CH_DRONE, CH_FUE, CH_TAIKO, CH_DRUM = 0, 1, 2, 3, 9
WOODBLOCK = 76  # 打楽器チャンネルのハイ・ウッドブロック（拍子木の代わり）
ODAIKO, SHIME = 36, 60  # 太鼓の音色で鳴らす高さ：大太鼓は低く、締太鼓は高く

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LEN = {"16": 0.25, "8": 0.5, "8.": 0.75, "4": 1.0, "4.": 1.5, "2": 2.0}
# Thaxted の頭（ハ長調）。ep03/jupiter.txt と同じ
PHRASE = "E4:8 G4:8 A4:4 A4:8 C5:8 B4:8. G4:16 C5:8 D5:8 C5:8 B4:8 A4:8 G4:4."


def notes(text, shift=0):
    out = []
    for tok in text.split():
        name, length = tok.split(":")
        pitch = 12 * (int(name[-1]) + 1) + NOTE[name[0]] + shift
        out.append((pitch, LEN[length]))
    return out


# 人が演奏したように揺らす量（単位は拍。テンポ 120 なら 0.04 拍で 20 ミリ秒）
# チャンネルごとに、ばらつきの大きさと、いつも少し遅れる量を変える（笛はのんびり）
WOBBLE = {CH_SHAMI: (0.045, 0.01), CH_DRONE: (0.05, 0.02), CH_FUE: (0.06, 0.04),
          CH_TAIKO: (0.045, 0.0), CH_DRUM: (0.04, 0.0)}  # 太鼓も三味線並み（前座さんの素人っぽさ）


class Song:
    def __init__(self, tempo, seed=SEED):
        self.tempo = tempo
        self.raw = []  # 揺らす前の音 (ch, 拍, 高さ, 長さ, 強さ)
        self.ev = []  # (tick, 順番, バイト列)
        self.rnd = random.Random(seed)
        # テンポのゆっくりした伸び縮み（2 つの波を重ねて、合わせて最大 ±0.15 拍ずれる）
        self.waves = [(self.rnd.uniform(6, 10), self.rnd.uniform(0, 6.3), 0.09),
                      (self.rnd.uniform(2.5, 4), self.rnd.uniform(0, 6.3), 0.05)]

    def drift(self, beat):
        return sum(a * (math.sin(beat / p + ph) - math.sin(ph)) for p, ph, a in self.waves)

    def note(self, ch, beat, pitch, length, vel):
        self.raw.append((ch, beat, pitch, length, vel))

    @staticmethod
    def loose(progress):
        """曲のどこまで来たか（0〜1）→ 揺らす量の倍率。弾きはじめはばらばらで、終わりに向けてぴったり合っていく。"""
        return max(0.05, 1 - progress) ** 0.7

    def humanize(self):
        """揺らした音を MIDI のイベントにする。曲の長さが分かってから揺らすので、書き出す直前に呼ぶ。"""
        total = max(b for _, b, *_ in self.raw) or 1
        for ch, beat, pitch, length, vel in self.raw:
            k = self.loose(beat / total)
            sd, late = WOBBLE.get(ch, (0.03, 0.0))
            beat = max(0.0, beat + k * (self.drift(beat) + late + self.rnd.gauss(0, sd)))
            length *= self.rnd.uniform(0.8, 1.1)
            jitter = (0.5 + 0.5 * k) * self.rnd.gauss(0, 9)
            vel = 127 if vel >= 127 else max(1, min(126, round(vel + jitter)))  # 127 は「いちばん強く」なので揺らさない
            on, off = round(beat * TPQ), round((beat + length) * TPQ)
            self.ev.append((on, 1, bytes([0x90 | ch, pitch, vel])))
            self.ev.append((off, 0, bytes([0x80 | ch, pitch, 0])))

    def program(self, ch, prog):
        self.ev.append((0, 0, bytes([0xC0 | ch, prog])))

    def write(self, path):
        self.humanize()
        def vlq(n):
            b = [n & 0x7F]
            while n > 0x7F:
                n >>= 7
                b.insert(0, (n & 0x7F) | 0x80)
            return bytes(b)
        us = round(60_000_000 / self.tempo)
        track, last = bytearray(b"\x00\xff\x51\x03" + us.to_bytes(3, "big")), 0
        for tick, _, data in sorted(self.ev, key=lambda e: (e[0], e[1])):
            track += vlq(tick - last) + data
            last = tick
        track += b"\x00\xff\x2f\x00"
        with open(path, "wb") as f:
            f.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, TPQ))
            f.write(b"MTrk" + struct.pack(">I", len(track)) + track)


def shamisen_phrase(s, beat, shift=0, vel=100, fue=False):
    """旋律を三味線で弾く。撥で弾くので音は短めに切り、拍の裏に低い開放弦（ド）を「テン」と入れる。"""
    b = beat
    for pitch, length in notes(PHRASE, shift):
        s.note(CH_SHAMI, b, pitch, min(length, 0.45), vel)
        if fue:
            s.note(CH_FUE, b, pitch + 12, length * 0.95, 70)
        b += length
    for k in range(int((b - beat) * 2)):
        if k % 2:
            s.note(CH_DRONE, beat + k * 0.5, 48 + shift, 0.2, 55)
    return b


def tenteke(s, beat, beats, vel=80):
    """締太鼓の「テンツク」：8 分で刻み、拍の頭を強く。大太鼓は 2 拍ごとに「ドン」。"""
    for k in range(int(beats * 2)):
        s.note(CH_TAIKO, beat + k * 0.5, SHIME, 0.2, vel if k % 2 == 0 else vel - 25)
    for k in range(0, int(beats), 2):
        s.note(CH_TAIKO, beat + k, ODAIKO, 0.8, vel + 20)


def setup(s):
    s.program(CH_SHAMI, SHAMISEN)
    s.program(CH_DRONE, SHAMISEN)
    s.program(CH_FUE, FUE)
    s.program(CH_TAIKO, TAIKO)


def opening():
    """出囃子：拍子木 → 太鼓の入り → 旋律 3 回（2 回目から笛が重なる）→ 三味線の「チャン」と大太鼓で止める。"""
    s = Song(tempo=118)
    setup(s)
    s.note(CH_DRUM, 0, WOODBLOCK, 0.3, 120)
    s.note(CH_DRUM, 1.5, WOODBLOCK, 0.3, 120)
    for k, v in enumerate((70, 80, 90, 100, 110, 120)):  # 太鼓のころがし
        s.note(CH_TAIKO, 3 + k * 0.25, SHIME, 0.15, v)
    s.note(CH_TAIKO, 4.5, ODAIKO, 1.0, 120)
    b = 5.5
    for rep in range(3):
        start = b
        b = shamisen_phrase(s, b, vel=105, fue=rep > 0)
        tenteke(s, start, b - start, vel=75 + rep * 8)
    for p in (48, 55, 60):  # ド・ソ・ド（二上りの開放弦）を一度に
        s.note(CH_SHAMI, b, p, 1.5, 120)
    s.note(CH_TAIKO, b, ODAIKO, 1.5, 127)
    return s


def boom(s, beat):
    """最後の大きな「ドン」。大太鼓に、1 オクターブ下の太鼓とバスドラムを重ねて、長く響かせる。"""
    s.note(CH_TAIKO, beat, ODAIKO, 3.0, 127)
    s.note(CH_TAIKO, beat, ODAIKO - 12, 3.0, 127)
    s.note(CH_DRUM, beat, 35, 1.0, 127)


def closing(melody=False):
    """追い出し太鼓：「デテケ、デテケ」をだんだん強く → 旋律を一節 → 大太鼓で締め。

    寄席の追い出し（打ち出し）は、本来は太鼓だけ。既定（melody=False）では旋律を入れず、
    「デテケ、デテケ」のあと「テンテン、バラバラ、テンバラバラ」、ひと呼吸おいて大太鼓を大きく「ドン」。
    """
    s = Song(tempo=126)
    setup(s)
    b = 0.0
    for k in range(20):  # デ・テ・ケ（大太鼓 1 つと締太鼓 2 つ）を 20 回。4 回に 1 回は締太鼓を「テケテケ」と細かく
        v = 58 + k * 2 if not melody else 62 + k * 3  # 太鼓だけの版は、最後のドンが立つように抑えめ
        s.note(CH_TAIKO, b, ODAIKO, 0.4, v + 10)
        if k % 4 == 3:
            for j in range(4):
                s.note(CH_TAIKO, b + j * 0.25, SHIME, 0.15, v - 5 + (j % 2) * 8)
        else:
            s.note(CH_TAIKO, b + 0.5, SHIME, 0.2, v)
            s.note(CH_TAIKO, b + 0.75, SHIME, 0.2, v - 10)
        b += 1
    if not melody:
        # テン・テン・バラバラ ｜ テン・バラバラ ｜ ドン
        for t, n in ((0, 1), (0.5, 1), (1, 4), (2, 1), (2.5, 4)):
            for j in range(n):
                s.note(CH_TAIKO, b + t + j * 0.125 * (2 if n == 1 else 1), SHIME, 0.12, 95 - j * 6)
        boom(s, b + 4.0)
        return s
    end = shamisen_phrase(s, b, vel=110, fue=True)
    tenteke(s, b, end - b, vel=95)
    for p in (48, 55, 60):
        s.note(CH_SHAMI, end, p, 2.0, 120)
    s.note(CH_TAIKO, end, ODAIKO, 2.0, 127)
    s.note(CH_DRUM, end + 2, WOODBLOCK, 0.3, 120)
    return s


# 寄席で鳴っているような、しょぼいけど味のある音にする（制作者：効果音集の出囃子は「きれいすぎてダメ」）。
# 左右をほぼ真ん中に寄せ、低いところと高いところを削り（小屋のスピーカー）、狭い部屋の跳ね返りと、客席のかすかなざわめき（ピンクノイズ）を足す
YOSE = ("[0:a]pan=stereo|c0=0.75*c0+0.25*c1|c1=0.25*c0+0.75*c1,highpass=f=160,lowpass=f=4500,"
        "aecho=0.8:0.6:19|37:0.25|0.15,acompressor=threshold=0.25:ratio=3:attack=5:release=120[m];"
        "anoisesrc=color=pink:amplitude=0.004:sample_rate=48000,highpass=f=200,lowpass=f=3000[n];"
        "[m][n]amix=inputs=2:duration=first:normalize=0[out]")


def peak_db(wav):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(re.search(r"max_volume: (-?[\d.]+) dB", r.stderr).group(1))


def yose(wav):
    """加工すると音が小さくなるので、いちばん大きいところを元の音と同じ高さにそろえる。"""
    out = wav[:-4] + "_yose.wav"
    tmp = out + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-filter_complex", YOSE, "-map", "[out]", tmp],
                   check=True)
    gain = peak_db(wav) - peak_db(tmp)
    # 後ろの残響の無音（2 秒あまり）は切る。動画では、次の行との間を direction.tsv の gap で決める
    trim = "areverse,silenceremove=start_periods=1:start_threshold=-55dB,areverse"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", f"volume={gain}dB,{trim}", out], check=True)
    os.remove(tmp)
    print(out)


def render(song, name):
    mid, wav = os.path.join(OUT, name + ".mid"), os.path.join(OUT, name + ".wav")
    song.write(mid)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.7", "-r", "48000", "-F", wav, SF2, mid],
                   check=True, stderr=subprocess.DEVNULL)
    print(wav)
    yose(wav)


def main():
    os.makedirs(OUT, exist_ok=True)
    render(opening(), "open")
    render(closing(), "close")
    render(closing(melody=True), "close_melody")


if __name__ == "__main__":
    main()
