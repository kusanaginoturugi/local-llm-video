"""どの回を作るかを決め、その回のファイルの場所を返す。

回ごとのファイルは episodes/ep01/ のように 1 つのフォルダにまとめる。
作る回は環境変数 EPISODE（例 EPISODE=ep01）で選ぶ。指定がなければいちばん新しい回。
"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
EPISODES = os.path.join(ROOT, "episodes")
NAME = os.environ.get("EPISODE") or sorted(d for d in os.listdir(EPISODES) if d.startswith("ep"))[-1]
DIR = os.path.join(EPISODES, NAME)
SLIDE_DIR = os.path.join(DIR, "slides")     # 構成図とスクリーンショット
VOICE_OUT = os.path.join(DIR, "out", "voice")  # 合成した音声とタイムライン
VIDEO_OUT = os.path.join(DIR, "out", "video")  # 動画・概要欄・字幕・サムネイル

if not os.path.isdir(DIR):
    raise SystemExit(f"回のフォルダがありません: {DIR}")


def path(name):
    """その回のフォルダの中のファイル（script.tsv など）。"""
    return os.path.join(DIR, name)


def module(name):
    """その回の slides.py や meta.py を読み込む。"""
    spec = importlib.util.spec_from_file_location(f"{NAME}_{name}", path(name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
