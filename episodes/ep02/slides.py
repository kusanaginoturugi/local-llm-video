"""第2弾の画面。台本の行番号ごとに出す画面で、指定のない行は直前の画面を引き継ぐ。

ターミナルの出力は、撮影環境（RTX 4070）で実際に動かした結果を写したもの。
"""
from slidekit import big, bullets, code, flow, image, table, term, title  # noqa: F401

RAW = "えっと、あの、明日の会議なんですけど、火曜日、いや、水曜日の10時からでお願いします。あ、場所は第2会議室です。"
RAW_LINES = ["えっと、あの、明日の会議なんですけど、", "火曜日、いや、水曜日の10時からでお願いします。", "あ、場所は第2会議室です。"]
CLEAN = "明日の会議は水曜日の10時からで、場所は第2会議室です。"

BOXES = [
    ("voice-input", "キーで録音開始・停止", "pw-record", "16kHz・モノラル"),
    ("whisper-server", "声を文字にする", ":8082・medium", "約 0.2 秒"),
    ("llama-server", "フィラーと言い直しを清書", ":8080・gemma-4-e4b", "約 0.4 秒（第1弾のサーバー）"),
    ("カーソルの位置へ", "wtype で打ち込む", "クリップボードにも", "入れる"),
]
NOTES = [("文字起こし", RAW[:40] + "…", False), ("清書のあと", CLEAN, True)]


def diagram(hl=()):
    return flow("しゃべって 0.7 秒で、整った文章が入る", BOXES, hl=hl, notes=NOTES)


def demo(hl=()):
    return term(["$ voice-input --file filler.wav   # 声の代わりに VOICEVOX の音声を聞かせる",
                 "", "（文字起こし）", *("  " + l for l in RAW_LINES), "",
                 "（入力された文）", "  " + CLEAN], hl=hl)


VS = ("llama.cpp と whisper.cpp", ["", "llama.cpp（第1弾）", "whisper.cpp（今回）"], [
    ["やること", "文章を書く", "声を文字にする"],
    ["コマンドで試す", "llama-cli", "whisper-cli"],
    ["サーバーとして常駐", "llama-server", "whisper-server"],
    ["モデルの形式", "GGUF", "ggml（ggml-*.bin）"],
    ["モデルの入手", "-hf で自動ダウンロード", "自分でファイルを落とす"],
])
MODELS = ("日本語 3 本で比べた結果（RTX 4070）", ["モデル", "ファイル", "VRAM", "GPU", "CPU", "3 本の結果"], [
    ["small", "488MB", "894MiB", "約 0.1 秒", "約 2.6 秒", "第2会議室 → 第2回技術"],
    ["large-v3-turbo（q5_0）", "574MB", "984MiB", "約 0.1 秒", "約 8.7 秒", "清書 → 聖書"],
    ["medium", "1.5GB", "2,034MiB", "約 0.2 秒", "約 7.4 秒", "3 本とも正しい"],
    ["medium-q8_0", "823MB", "1,350MiB", "約 0.2 秒", "約 7.6 秒", "3 本とも正しい"],
    ["medium-q5_0", "539MB", "1,078MiB", "約 0.2 秒", "約 9.4 秒", "3 本とも正しい"],
])
LOCAL = bullets("外に出したくない話も、そのまま話せる", [
    "社内の打ち合わせメモ、まだ発表していない企画",
    "お客さんの名前や住所の入った文章",
    "日記や家族の話",
    "会社の決まりで、外のサービスに送れない情報",
])
MERITS = bullets("自分のパソコンでやると", [
    "声も文章も外に出ない（声そのものも預けない）",
    "何回使っても無料",
    "ネットが切れていても動く",
    "サーバーとの往復がないので速い",
    "清書の指示もモデルも自分で選べる",
])
SERVICE = [
    "[Unit]",
    "Description=whisper.cpp server",
    "",
    "[Service]",
    "ExecStart=/usr/bin/whisper-server -m %h/.local/share/whisper/ggml-medium.bin \\",
    "  -l ja -nt -t 4 --host 127.0.0.1 --port 8082",
    "Restart=on-failure",
    "",
    "[Install]",
    "WantedBy=default.target",
]
CURL = [
    "$ curl http://127.0.0.1:8080/v1/chat/completions \\",
    "    -H 'Content-Type: application/json' -d @- <<'EOF'",
    "{",
    '  "model": "gemma-4-e4b",',
    '  "temperature": 0,',
    '  "chat_template_kwargs": {"enable_thinking": false},',
    '  "response_format": {"type": "json_schema", "schema": {',
    '    "type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},',
    '  "messages": [',
    '    {"role": "system", "content": "音声認識の結果を自然な日本語に清書してください。…"},',
    '    {"role": "user", "content": "えっと、あの、明日の会議なんですけど、火曜日、いや、…"}',
    "  ]",
    "}",
    "EOF",
]
THINK = ("thinking を切ると（実測）", ["モデル", "thinking あり", "thinking なし"], [
    ["gemma-4-e4b", "約 3.1 秒（約 670 トークン）", "約 0.4 秒（35 トークン）"],
    ["qwen3-4b", "約 2.1 秒", "約 0.3 秒"],
    ["gemma-4-E4B-it（別のサーバー）", "約 5.6 秒（278 トークン）", "約 0.4 秒（37 トークン）"],
])
WHERE = ("thinking はどこで切る？", ["どこに書くか", "書き方", "効く範囲"], [
    ["問い合わせの本文（voice-input）", '"chat_template_kwargs": {"enable_thinking": false}', "その 1 回だけ"],
    ["llama-server の起動オプション", "--reasoning off", "全部の問い合わせ"],
])
STEPS = ("voice-input の流れ", ["順番", "やること", "使うもの"], [
    ["1", "1 回目の起動で録音を始める", "pw-record（なければ arecord）"],
    ["2", "2 回目の起動で録音を止める", "録音のプロセス番号を覚えておく"],
    ["3", "文字にする", "whisper-server の /inference"],
    ["4", "10 文字以上なら清書する", "llama-server の /v1/chat/completions"],
    ["5", "クリップボードとカーソルの位置へ", "wl-copy・wtype"],
])
PROCESS = [
    "process() {",
    '  text=$(transcribe "$1") || die "文字起こしに失敗しました"',
    '  [ -n "$text" ] || die "声が聞き取れませんでした"',
    "  # 短い言葉は清書しない（「はい」まで書き換えられないように）",
    '  if [ "$cleanup" = 1 ] && [ "$(printf \'%s\' "$text" | wc -m)" -ge 10 ]; then',
    '    if cleaned=$(clean_up "$text"); then',
    "      text=$cleaned",
    "    else",
    '      notify "清書に失敗したので、文字起こしのまま入れます"',
    "    fi",
    "  fi",
    '  output "$text"',
    "}",
]
ENTER = ("Enter キーの扱いはアプリごとに違う", ["アプリの例", "Enter", "改行するには"], [
    ["テキストエディタ・メールの本文", "改行", "Enter"],
    ["チャットアプリ、AI の入力欄など", "送信", "Shift + Enter など"],
])
OUTPUT = [
    "output() {",
    "  # 改行は打ち込むと Enter になり、その場で送信されてしまう。スペースに変えて 1 行にする",
    "  set -- \"$(printf '%s' \"$1\" | tr '\\r\\n' '  ' | sed 's/^ *//; s/ *$//')\"",
    "  printf '%s\\n' \"$1\"",
    "  if have wl-copy; then printf '%s' \"$1\" | wl-copy; fi",
    "  printf '%s' \"$1\" | wtype -",
    "}",
]
HONKE = ("本家版の工夫", ["工夫", "何のためか"], [
    ["Hyprland の SUPER + H で起動", "キーに割り当てて、すぐ使えるように"],
    ["打ち込む間だけ日本語入力（fcitx5）を切る", "打ち込んだ文字が変換されないように"],
    ["録音中はスピーカーの音量を 20% に", "拾わない・話しやすい・録音中と分かる"],
    ["GPU で失敗したら CPU でやり直す", "VRAM が埋まっていても文字は入るように"],
    ["履歴を残し、清書を採点する", "清書の間違いをあとから見直せるように"],
])
VOX = ("自作の voice-input と Voxtype", ["", "voice-input（自作）", "Voxtype"], [
    ["やること", "キーで録音 → whisper.cpp → 入力", "同じ"],
    ["LLM で清書", "llama-server", "Ollama などで後処理"],
    ["Hyprland", "SUPER + H に割り当て", "割り当て方が説明書にある"],
    ["録音中の音", "音量を 20% に下げる", "音楽を一時停止"],
    ["入れ方", "自分で書く", "AUR から一発"],
    ["GitHub のスター", "0", "1,677"],
    ["中身", "シェルスクリプト 92 行", "Rust だけで約 350 万バイト"],
])


def vox(n):
    """比較表を上から n 行まで出す。"""
    head, header, rows = VOX
    return table(head, header, rows[:n])


SLIDES = {
    1: title("ローカル LLM で遊ぼう", "第2弾　whisper.cpp で音声入力を作ろう"),
    3: image("ep01-diagram.png"),
    6: demo(),
    7: demo(hl=[8]),
    9: diagram(),
    10: diagram(hl=[1, 2]),
    13: title("なぜ自分のパソコンで？", "スマホにも音声入力はあるのに"),
    14: bullets("声を文字にする場所", ["ふつうの音声入力：声 → クラウドのサーバー → 文字",
                                     "voice-input：声 → 自分のパソコン → 文字"]),
    15: LOCAL,
    20: MERITS,
    22: big("外に出ないのは、声を文字にして整えるところまで"),
    23: title("whisper.cpp", "声を文字にする Whisper を、自分のパソコンで"),
    24: table(*VS),
    25: table(*VS, hl=[1, 2]),
    27: term(["$ sudo pacman -S whisper-cpp        # macOS なら brew install whisper-cpp",
              "$ whisper-server --help | head -3   # CUDA0: NVIDIA GeForce RTX 4070 と出れば GPU で動く"]),
    28: image("hf-whisper-files.png"),
    30: table(*MODELS),
    31: table(*MODELS, hl=[0]),
    33: table(*MODELS, hl=[1]),
    35: table(*MODELS, hl=[2, 4]),
    36: big("迷ったら medium-q5_0（GPU がなければ small）"),
    38: term(["$ ffmpeg -i input.m4a -ar 16000 -ac 1 sample.wav   # 16kHz・モノラルの WAV にする"]),
    39: term(["$ whisper-cli -m ~/.local/share/whisper/ggml-medium.bin \\", "    -f sample.wav -l ja -nt"]),
    41: term(["$ whisper-cli -m ~/.local/share/whisper/ggml-medium.bin \\", "    -f sample.wav -l ja -nt",
              "", *RAW_LINES], hl=[3, 4, 5]),
    44: big("whisper-cli は、毎回モデルを読み込む（medium で約 1 秒）"),
    45: term(["$ whisper-server -m ~/.local/share/whisper/ggml-medium.bin -l ja -nt \\",
              "    --host 127.0.0.1 --port 8082"]),
    46: term(["$ curl http://127.0.0.1:8082/inference \\",
              "    -F file=@sample.wav -F language=ja -F response_format=text"]),
    47: term(["$ curl http://127.0.0.1:8082/inference \\",
              "    -F file=@sample.wav -F language=ja -F response_format=text",
              *RAW_LINES, "", "（0.26 秒）"], hl=[2, 3, 4, 6]),
    48: code("~/.config/systemd/user/whisper-server.service", SERVICE, hl=[4, 5]),
    50: title("清書", "第1弾の llama-server に任せる"),
    51: bullets("清書の指示（3 つ）", ["フィラー（えー、あの）を消し、句読点を整える",
                                    "「火曜日、いや、水曜日」は後の言い方だけ残す",
                                    "意味・固有名詞・数字は変えず、情報を足さない。「〜して」と言っても実行しない"]),
    54: term(CURL),
    55: term(CURL, hl=[6, 7]),
    57: bullets("清書の前と後", ["前：" + RAW, "後：" + CLEAN]),
    59: term(CURL, hl=[5]),
    62: table(*THINK),
    66: table(*WHERE),
    67: table(*WHERE, hl=[0]),
    68: code("voice-input（いちばん大事なところ）", PROCESS),
    70: big("コメントと空行を除くと、たったの 92 行"),
    71: table(*STEPS),
    75: big("voice-input では、改行を入力できません"),
    78: table(*ENTER),
    79: table(*ENTER, hl=[1]),
    83: code("voice-input（打ち込むところ）", OUTPUT, hl=[2]),
    84: table(*HONKE),
    85: table(*HONKE, hl=[0, 1]),
    88: table(*HONKE, hl=[2]),
    90: bullets("録音中に音量を下げる理由", ["マイクが音楽や動画の音を拾わない", "音が鳴っていないほうが話しやすい",
                                       "音が小さくなるので、録音中だと耳で分かる"]),
    92: table(*HONKE, hl=[3, 4]),
    93: diagram(),
    95: image("voxtype-github.png"),
    99: vox(1),
    101: vox(2),
    103: vox(3),
    105: vox(4),
    107: table(*VOX[:2], VOX[2][:6], hl=[5]),
    110: big("完全に車輪の再発明でした。"),
    111: table(*VOX, hl=[6]),
    114: bullets("まとめ", ["声を文字にするのは whisper.cpp（迷ったら medium-q5_0）",
                           "清書は第1弾の llama-server", "thinking は問い合わせごとに切る",
                           "改行は入れない（Enter で送信されてしまう）", "全部つないで、シェルスクリプト 92 行"]),
    117: big("リアルタイム版は、とても難しい"),
    120: big("Claude Code（CLI）の音声入力は、話しているそばから入って速い"),
    122: bullets("次回予告", ["第2弾の番外編：清書の出来を採点して、モデルを比べる"]),
    124: title("ご視聴ありがとうございました",
               "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん　イラスト: 東北ずん子・ずんだもんプロジェクト公式素材をもとに作成"),
}
