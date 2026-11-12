"""第4弾の画面。話す行と録画の開始を合わせる。"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "video"))
from slidekit import big, bullets, flow, image, table, term, title


def screencam(file, label, speed=1, source_start=0):
    return ("screencam", f"demo/{file}", label, speed, source_start)


SLIDES = {
    1: title("ローカル LLM で遊ぼう", "第4弾：ページ翻訳と PLaMo 3 Translate 0.8B"),
    9: big("ブラウザのページを、手元の LLM で訳す"),
    13: image("translator-popup.png"),
    15: flow("ページ翻訳の流れ", [("ページ", "表示中の文章を拾う"),
                                  ("ブラウザ拡張", "文章を小分けにする"),
                                  ("ローカル LLM", "訳文を返す")]),
    19: table("今回の主役", ["項目", "内容"], [
        ["モデル", "PLaMo 3 Translate 0.8B"],
        ["量子化", "GGUF / Q4_K_M"],
        ["ファイル", "約 0.57 GB（573 MB）"],
    ]),
    21: image("mslearn-ja.png"),
    25: image("mslearn-en.png"),
    27: screencam("mslearn-plamo-raw.mkv", "Microsoft Learn 英語版を PLaMo で翻訳", 1, 3.0),
    28: table("同じフィールドの説明", ["表示", "訳文"], [
        ["Microsoft Learn 日本語版", "コマンドのストリングを助けて。"],
        ["英語版を PLaMo で翻訳", "コマンドのヘルプ文字列。"],
    ]),
    34: table("使ってきた翻訳モデル（GGUF Q4_K_M）", ["順番", "モデル", "ファイル容量"], [
        ["最初", "TranslateGemma 12B", "約 7.30 GB"],
        ["軽くする", "TranslateGemma 4B", "約 2.49 GB"],
        ["次に", "Hy-MT2 7B", "約 4.62 GB"],
        ["今回", "PLaMo 3 Translate 0.8B", "約 0.57 GB"],
    ]),
    40: image("../../../assets/official/pfn-figure13.png"),
    44: table("同じ記事を実画面で比較", ["モデル", "GGUF Q4_K_M"], [
        ["TranslateGemma 12B", "約 7.3 GB"],
        ["PLaMo 3 Translate 0.8B", "約 0.57 GB"],
    ]),
    45: screencam("browser-translategemma12b-glow-tab.mkv",
                  "TranslateGemma 12B（約 7.3 GB）／実録・等速"),
    48: table("次は PLaMo", ["モデル", "GGUF Q4_K_M"], [
        ["PLaMo 3 Translate 0.8B", "約 0.57 GB"],
    ]),
    49: screencam("browser-plamo-glow-tab.mkv",
                  "PLaMo 0.8B（約 0.57 GB）／実録・等速"),
    53: screencam("browser-plamo-glow-tab.mkv",
                  "PLaMo 0.8B／同じ実録を4倍スロー", 0.25, 1.5),
    58: title("自分でも動かしてみよう", "PLaMo とブラウザ拡張をつなぐ"),
    59: term(["第1弾と同じ -hf で自動ダウンロード",
              "$ llama-server -hf pfnet/plamo-3-translate-0.8b-GGUF:Q4_K_M"]),
    61: term(["llama-cpp 0.6.0 の読み込みエラー",
              "unknown tokenizer: 'plamo3'"], hl=[1]),
    63: term(["動作を確認した llama.cpp: 0.9.0-dev / commit ac931b5",
              "$ llama-server -hf pfnet/plamo-3-translate-0.8b-GGUF:Q4_K_M \\",
              "  --host 127.0.0.1 --port 8000 --jinja --no-prefill-assistant"]),
    67: image("plamo-custom-settings.png"),
    71: bullets("ページ翻訳を使う", ["翻訳ボタンでページを訳す",
                                "気になる箇所だけ訳し直す",
                                "用語集で固有名詞を指定する"]),
    73: bullets("詳しい手順と実測値", ["概要欄の解説ページに掲載",
                                     "モデルと拡張の入手先",
                                     "設定・計測条件・訳文の比較"]),
    77: title("それでは、また次回。", "ローカル LLM で遊ぼう 第4弾"),
    83: title("次回も見てね！", "音声：VOICEVOX:四国めたん／ずんだもん／春日部つむぎ"),
}
