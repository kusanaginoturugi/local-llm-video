#!/bin/sh
# 第5弾で使った NDLOCR-Lite の環境を作る（本家の README の手順 + GPU 版の onnxruntime）。
# 使い方: sh setup.sh  → ndlocr-lite/ と .venv/
# 動かすときは ndlocr-lite/src で ../../.venv/bin/python ocr.py …（CPU なら --device を付けない）
set -eu
cd "$(dirname "$0")"
[ -d ndlocr-lite ] || git clone https://github.com/ndl-lab/ndlocr-lite
git -C ndlocr-lite checkout -q a25d456   # v1.4.0（2026-11-11）
[ -d .venv ] || uv venv -p 3.12 .venv
uv pip install -p .venv/bin/python -r ndlocr-lite/requirements.txt
# GPU を使うときだけ：CPU 版を GPU 版に入れ替える（CUDA と cuDNN も pip で入る）
if [ "${GPU:-1}" = 1 ]; then
  uv pip uninstall -p .venv/bin/python onnxruntime
  uv pip install -p .venv/bin/python 'onnxruntime-gpu[cuda,cudnn]==1.31.1'
fi
.venv/bin/python -c 'import onnxruntime as o; print(o.__version__, o.get_available_providers())'
