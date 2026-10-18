#!/usr/bin/env python3
"""解説動画用の穏やかなループ BGM を合成する（素材を使わないので権利の心配がない）。

76 BPM、Fmaj7 → Em7 → Dm7 → Cmaj7 を 2 周する 8 小節。
音の余韻は先頭に回り込ませて、継ぎ目なくループするようにしている。
"""
import os
import wave

import numpy as np

SR = 44100
BPM = 76
BEAT = 60 / BPM
BAR = BEAT * 4
BARS = 8
N = int(SR * BAR * BARS)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "bgm", "bgm_loop.wav")

rng = np.random.default_rng(7)
mix = np.zeros((N, 2))


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    """信号を start 秒から足す。ループの終わりを越えた分は先頭に回り込ませる。"""
    i = int(start * SR) % N
    idx = (np.arange(len(sig)) + i) % N
    left, right = gain * (1 - pan) / 2, gain * (1 + pan) / 2
    np.add.at(mix[:, 0], idx, sig * left)
    np.add.at(mix[:, 1], idx, sig * right)


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


# コードの構成音（MIDI 番号）
CHORDS = [
    [53, 57, 60, 64],  # Fmaj7
    [52, 55, 59, 62],  # Em7
    [50, 53, 57, 60],  # Dm7
    [48, 52, 55, 59],  # Cmaj7
]

for bar in range(BARS):
    chord = CHORDS[bar % 4]
    t0 = bar * BAR

    # パッド: 少しずらした 2 本のサインで揺らぎを出す
    n = int(BAR * SR * 1.3)
    t = np.arange(n) / SR
    for k, m in enumerate(chord):
        f = hz(m + 12)
        tone = 0.5 * np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t + 1.3)
        add(tone * env(n, 0.6, 1.2), t0, pan=(k - 1.5) / 3, gain=0.035)

    # ベース: 1 拍目と 3 拍目
    for beat, m in ((0, chord[0] - 12), (2, chord[0] - 12 + (7 if bar % 2 else 0))):
        n = int(BEAT * 1.8 * SR)
        t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 2.2)
        add(tone * env(n, 0.01, 0.2), t0 + beat * BEAT, gain=0.16)

    # エレピ風アルペジオ: 8 分音符、2 周目は少し音を変える
    order = [0, 2, 1, 3, 2, 1, 3, 2] if bar < 4 else [0, 1, 2, 3, 2, 3, 1, 2]
    for step, ci in enumerate(order):
        m = chord[ci] + 12 + (12 if bar >= 4 and step == 6 else 0)
        n = int(BEAT * 1.5 * SR)
        t = np.arange(n) / SR
        f = hz(m)
        tone = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 3.5)
        vel = 0.9 if step % 2 == 0 else 0.65
        add(tone * env(n, 0.005, 0.15), t0 + step * BEAT / 2 + 0.012 * (step % 2),
            pan=0.35 if step % 2 else -0.25, gain=0.05 * vel)

    # やわらかいキックとハイハット
    for beat in (0, 2):
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        kick = np.sin(2 * np.pi * (45 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
        add(kick, t0 + beat * BEAT, gain=0.12)
    for half in range(8):
        n = int(0.05 * SR)
        noise = rng.standard_normal(n)
        noise = np.diff(noise, prepend=0)  # 高い音だけ残す
        hat = noise * np.exp(-np.arange(n) / SR * 90)
        add(hat, t0 + half * BEAT / 2 + BEAT / 4, pan=0.2, gain=0.012 if half % 2 else 0.02)

# 音量をそろえて保存
mix /= np.max(np.abs(mix)) / 0.8
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"{OUT}: {N / SR:.2f} 秒")
