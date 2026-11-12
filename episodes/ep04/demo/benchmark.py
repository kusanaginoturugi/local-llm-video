#!/usr/bin/env python3
"""PLaMo の翻訳をローカル API で実測する。起動済みサーバーに対し、初回とウォーム後を分ける。"""
import json
import os
import statistics
import time
import urllib.request

URL = os.environ.get("PLAMO_URL", "http://127.0.0.1:8000/v1/chat/completions")
SOURCES = [
    "The meeting has been rescheduled for next Monday. Please update the project dashboard before noon.",
    "The package arrived this morning, but one of the cables was missing from the box.",
    "You can save the file locally and continue editing even when the network is unavailable.",
    "Please check the numbers in the report before sharing it with the rest of the team.",
    "The train was delayed by heavy rain, so we decided to meet at the station cafe.",
    "If the translation sounds unnatural, select that sentence and try translating it again.",
]
BODY = {
    "model": "plamo-3-translate",
    "temperature": 0,
}


def main():
    runs = []
    for i, source in enumerate(SOURCES):
        # 拡張の Custom / 1 item per batch / structured JSON off と同じ形。
        body = {**BODY, "messages": [
            {"role": "system", "content": "[plamo-translate]\ntarget_lang=ja"},
            {"role": "user", "content": f"[0]: {source}"},
        ]}
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.load(response)
        elapsed = time.perf_counter() - start
        raw = data["choices"][0]["message"]["content"].strip()
        content = raw.removeprefix("[0]:").strip()
        timings = data.get("timings", {})
        row = {"run": i + 1, "source": source, "wall_seconds": round(elapsed, 3),
               "raw_response": raw, "translation": content,
               "output_tokens": data.get("usage", {}).get("completion_tokens"),
               "predicted_tokens_per_second": timings.get("predicted_per_second")}
        runs.append(row)
        print(f"{i + 1}: {elapsed:.3f}s | {content}", flush=True)
    result = {"warmup_runs": 1, "measured_runs": 5,
              "median_wall_seconds": round(statistics.median(r["wall_seconds"] for r in runs[1:]), 3),
              "runs": runs}
    path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"median (runs 2-6): {result['median_wall_seconds']:.3f}s", flush=True)


if __name__ == "__main__":
    main()
