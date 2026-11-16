"""Live2D のめたんとずんだもんを、台本の時間どおりに動かして 1 コマずつ描く（第7弾から）。

render.py が子プロセスとして立ち上げる。直接は使わない。
必要なもの: リポジトリ直下の .venv-live2d（live2d-py、glfw、PyOpenGL、numpy、Pillow）、
assets/live2d/ に置いた公式ショップの Live2D モデル（坂本アヒル式）。

  .venv-live2d/bin/python video/live2d_frames.py PLAN.json

PLAN.json（render.py が書く）:
  {"fps": 30, "start": 最初に出すコマ, "count": 出すコマ数,
   "lines": [{"slug": "metan", "start": 秒, "end": 秒, "wav": パス, "react": ["exp_sad", "mtnFace_sad"]}, ...]}

標準出力に、最初の 1 行で各キャラの絵の大きさ（JSON）、続けてコマごとに CHARS の順で RGBA のバイト列を書く。
色は α を掛けていない（ふつうの RGBA）ので、そのまま PIL で貼れる。
しゃべっていないキャラも、呼吸とまばたきで少し動く。"""
import json
import math
import os
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
SS = 2  # 2 倍の大きさで描いて縮める（ふちのギザギザを消す）

# キャラごとのモデルと、画面に出す範囲。範囲はモデルのキャンバスの px（上が 0）。
# 横幅は「高さ × 出す大きさの縦横比」で決まり、cx を中心に切る
CHARS = {
    "metan": {"model": "assets/live2d/metan/shikoku_metan.model3.json",
              "cx": 557, "top": 540, "bottom": 1352, "size": (440, 470), "flip": True},  # 髪の幅 約 735px が列に収まる。
    # めたんの絵は体ごと画面の左を向いているので、左右を反転して右（ずんだもんの側）を向かせる
    "zundamon": {"model": "assets/live2d/zundamon/zundamon.model3.json",
                 "cx": 540, "top": 500, "bottom": 1312, "size": (440, 470)},  # めたんと同じ倍率。耳が立っても切れない
}
# 使ってよい表情とモーション。衣装替え（pose_costume_*）は台本で指定しても使わない
DENY = ("pose_costume",)


def model_vocab(slug):
    """モデルの表情とモーションの名前（render.py の確かめにも使う）。"""
    path = os.path.join(ROOT, CHARS[slug]["model"])
    with open(path) as f:
        refs = json.load(f)["FileReferences"]
    exps = {e["Name"] for e in refs.get("Expressions", []) if not e["Name"].startswith(DENY)}
    motions = {os.path.basename(m["File"]).split(".")[0]
               for group in refs.get("Motions", {}).values() for m in group}
    return exps, motions


def mouth_curve(wav_path, start, n_frames):
    """wav の音量から、コマごとの口の開き（0〜1）を作る。行の頭は start 秒。"""
    import numpy as np
    with wave.open(wav_path) as wf:
        sr, ch = wf.getframerate(), wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape(-1, ch)[:, 0] / 32768
    hop = sr / FPS
    first = round(start * FPS)
    vals = {}
    loud = []
    for k in range(int(len(pcm) / hop) + 1):
        seg = pcm[int(k * hop):int((k + 1) * hop)]
        r = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        vals[first + k] = r
        loud.append(r)
    loud = [r for r in loud if r > 0.01]
    ref = float(np.percentile(loud, 90)) if loud else 1.0
    return {i: min(1.0, r / ref) for i, r in vals.items() if 0 <= i < n_frames}


def motion_params(model_path):
    """モデルのモーションが動かすパラメータの ID。"""
    ids = set()
    for group in json.load(open(model_path))["FileReferences"].get("Motions", {}).values():
        for mm in group:
            with open(os.path.join(os.path.dirname(model_path), mm["File"])) as f:
                ids |= {c["Id"] for c in json.load(f)["Curves"] if c["Target"] == "Parameter"}
    return ids


RESET = 12  # モーションを止めてから、ふだんの顔と姿勢に戻すまでのコマ数（0.4 秒）


def main():
    # 標準出力はコマ専用にする。live2d-py の起動の表示や SDK のログ（C の printf も）は stderr に回す
    out = os.fdopen(os.dup(1), "wb")
    os.dup2(2, 1)
    sys.stdout = sys.stderr
    import glfw
    import live2d
    import numpy as np
    from OpenGL import GL

    with open(sys.argv[1]) as f:
        plan = json.load(f)
    start, count = plan["start"], plan["count"]
    end_frame = start + count
    slugs = list(CHARS)

    # 口の開き（しゃべっている行だけ）と、行ごとの表情・モーション
    mouth = {s: {} for s in slugs}
    events = {s: [] for s in slugs}
    for ln in plan["lines"]:
        s = ln["slug"]
        mouth[s].update(mouth_curve(ln["wav"], ln["start"], end_frame))
        events[s].append((round(ln["start"] * FPS), round((ln["end"] + 0.3) * FPS), ln.get("react") or []))

    live2d.enableLog(False)
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    glfw.make_context_current(glfw.create_window(64, 64, "live2d", None, None))
    live2d.init()
    live2d.glInit()

    chars = {}
    for s in slugs:
        c = CHARS[s]
        m = live2d.Model()
        m.LoadModelJson(os.path.join(ROOT, c["model"]))
        cw, ch = m.GetCanvasSizePixel()
        ow, oh = c["size"]
        scale = oh * SS / (c["bottom"] - c["top"])       # キャンバス 1px → 描く px
        fw, fh = round(cw * scale), round(ch * scale)
        fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)
        tex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, fw, fh, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, tex, 0)
        m.Resize(fw, fh)
        m.SetAutoBlink(False)  # まばたきのパラメータが登録されていないので、下で自分で閉じる
        # 切り出す範囲（OpenGL は下が 0）
        rw, rh = ow * SS, oh * SS
        x0 = round(c["cx"] * scale - rw / 2)
        y0 = fh - round(c["bottom"] * scale)
        # 縮めた絵を受ける小さいフレームバッファ（2x2 の平均は GPU の blit でやる）
        small = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, small)
        stex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, stex)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8, ow, oh, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, stex, 0)
        motions = {os.path.basename(mm["File"]).split(".")[0]: i for i, mm in enumerate(m.GetMotions()[""])}
        reset_ids = sorted(motion_params(os.path.join(ROOT, c["model"])) & set(m.GetParamIds()))
        defaults = {i: m.GetParamDefaultById(i) for i in reset_ids}
        exps, _ = model_vocab(s)
        chars[s] = dict(model=m, fbo=fbo, small=small, fw=fw, fh=fh, rect=(x0, y0, rw, rh), size=(ow, oh),
                        motions=motions, exps=exps, rng=np.random.default_rng(len(s)), blink=1.5, exp=None, mv=0.0, reset=-1, defaults=defaults)

    out.write((json.dumps({s: chars[s]["size"] for s in slugs}) + "\n").encode())
    out.flush()

    for i in range(end_frame):
        t = i / FPS
        draw = i >= start
        for s in slugs:
            c = chars[s]
            m = c["model"]
            # 行の頭で、その行の表情とモーションを入れる。行が終わったら表情を戻す
            # 行の終わりの余韻（0.3 秒）が次の行にかかったら、あとから始まった行を使う
            want = None
            for a, b, react in events[s]:
                if a <= i < b:
                    want = tuple(react)
                    if i == a:
                        for name in react:
                            if name in c["motions"]:
                                if c["reset"] + RESET > i:
                                    # 前の行のモーションがまだ戻りきっていない。残りを消してから始める
                                    m.StopAllMotions()
                                    m.ResetAllParameters()
                                    m.SaveParameters()
                                m.StartMotion("", c["motions"][name], 3)
                                c["reset"] = b   # 行が終わったら止める
            # このモデルのモーションはループするうえ、止めても最後の値が残る。
            # 行が終わったら止めて、RESET コマかけて初期値に寄せ、最後に保存されている値ごと初期値にする
            if i == c["reset"]:
                m.StopAllMotions()
            elif i == c["reset"] + RESET:
                m.ResetAllParameters()
                m.SaveParameters()
            exp = next((n for n in (want or ()) if n in c["exps"]), None)
            if exp != c["exp"]:
                if exp:
                    m.SetExpression(exp)
                else:
                    m.ResetExpression()
                c["exp"] = exp
            m.Update(1 / FPS)
            if c["reset"] <= i < c["reset"] + RESET:
                w = (i - c["reset"] + 1) / RESET
                for pid, v in c["defaults"].items():
                    m.SetParamById(pid, v, w)
            # 口：開くのは速く、閉じるのはゆっくり
            target = mouth[s].get(i, 0.0)
            c["mv"] = target if target > c["mv"] else c["mv"] * 0.55 + target * 0.45
            m.SetParamById("ParamMouthOpenY", c["mv"])
            # まばたき：0.15 秒で閉じて開く。間は 2.5〜5 秒でばらす（キャラごとに決まった乱数）
            if t >= c["blink"]:
                k = (t - c["blink"]) / 0.15
                if k >= 1:
                    c["blink"] = t + c["rng"].uniform(2.5, 5.0)
                else:
                    w = math.sin(math.pi * k)
                    m.SetParamById("ParamEyeLOpen", 0, w)
                    m.SetParamById("ParamEyeROpen", 0, w)
            if not draw:
                continue
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, c["fbo"])
            GL.glViewport(0, 0, c["fw"], c["fh"])
            live2d.clearBuffer(0, 0, 0, 0)
            m.Draw()
            x0, y0, rw, rh = c["rect"]
            ow, oh = c["size"]
            # 2 倍で描いたのを、α を掛けたまま GPU で 1/2 に縮めてから読む
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, c["fbo"])
            GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, c["small"])
            GL.glBlitFramebuffer(x0, y0, x0 + rw, y0 + rh, 0, 0, ow, oh, GL.GL_COLOR_BUFFER_BIT, GL.GL_LINEAR)
            GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, c["small"])
            px = GL.glReadPixels(0, 0, ow, oh, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
            a = np.frombuffer(px, dtype=np.uint8).reshape(oh, ow, 4)[::-1].astype(np.uint16)
            if CHARS[s].get("flip"):
                a = a[:, ::-1]
            # Live2D の色は α を掛けた値なので、PIL で貼れるように戻す
            alpha = a[..., 3:4]
            a[..., :3] = np.minimum(a[..., :3] * 255 // np.maximum(alpha, 1), 255)
            out.write(a.astype(np.uint8).tobytes())
        if draw:
            out.flush()
    out.close()
    live2d.dispose()
    glfw.terminate()


if __name__ == "__main__":
    main()
