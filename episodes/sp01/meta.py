"""番外編の概要欄とサムネイル（下書き。公開の前に見直す）。"""

REPO = "https://github.com/kusanaginoturugi/local-llm-video"
SOKKI = "https://dl.ndl.go.jp/pid/891273"

THUMBNAIL = {
    "number": "番外",
    "color": (230, 190, 120),
    "title": "めたんとずんだもんの",
    "title2": "落語『二人癖』",
    "pill": ("明治の", "速記から"),
    "metan": "met_s214",
    "zundamon": "zunmon_3022",
}


def description(chapters):
    return "\n".join([
        "『ローカル LLM で遊ぼう』番外編。めたんとずんだもんとつむぎで、落語『二人癖』をやります。",
        "何を見ても「飲める」と言うずんだもんと、何があっても「つまらない」と言うめたん。口癖をやめる約束をして、罰金を賭けて言わせ合います。",
        "台本は、明治 41 年の速記本（三代目 柳家小さん 口演）を、国立国会図書館デジタルコレクションで読んで書き起こしました。",
        "手元の LLM に現代語訳もさせてみましたが、「詰まろうか」を「詰まるか」にされたので、台本は原本から書き直しました。",
        "",
        "■ 目次",
        *chapters,
        "",
        "■ 原作",
        "柳家小さん（3代目）口演『二人癖』（『小さん落語会』三芳屋書店・松陽堂書店、明治 41 年、37〜64 ページ。保護期間満了）",
        f"国立国会図書館デジタルコレクション: {SOKKI}",
        "まくら（小噺）は使わず、口癖の話に替えました。噺の筋とせりふの順番は原作どおりで、言葉は今の話し言葉に直しています。",
        "",
        "■ 出囃子と追い出し太鼓",
        "出囃子は、ホルスト『惑星』より「木星」の中間部の旋律を、三味線・太鼓・笛に打ち込みました（サウンドフォント FluidR3）。",
        "追い出しは太鼓だけです。",
        "",
        "■ リンク",
        f"台本・翻刻・演出のメモ: {REPO}/tree/main/episodes/sp01",
        "",
        "■ これまでの回",
        "第1弾：llama-server を立ち上げよう https://youtu.be/3Sk9T1VqNsg",
        "第2弾：音声入力で Hello, Computer? https://youtu.be/k-ploGYRc_Q",
        "第3弾：声で会話するローカル AI",
        "第4弾：0.8B で爆速ページ翻訳 https://youtu.be/TUADm3MbcKE",
        "第5弾：スキャンした本を検索できる PDF に",
        "第6弾：Kindle の英語の本を、手元の LLM で訳して読む",
        "",
        "■ 制作",
        "台本・翻刻・お囃子・動画の組み立て: Claude Code（Claude Opus 5.5）",
        "",
        "■ クレジット",
        "音声: VOICEVOX:四国めたん / VOICEVOX:ずんだもん / VOICEVOX:春日部つむぎ",
        "Live2D モデル: 四国めたん・ずんだもん（坂本アヒル式）東北ずん子・ずんだもんプロジェクト公式ショップ",
        "Live2D モデル: 春日部つむぎ（坂本アヒル式）KASUKABEproject（イラスト 坂本アヒル／モデリング 株式会社Live2D・nizima ACTION!!）",
        "https://kasukabe294.booth.pm/items/8818575",
        "BGM: 魔王魂『アコースティック51』 https://maou.audio/bgm_acoustic51/ （CC BY 4.0）",
        "背景写真: SankalpSasnur『RGB desktop computer setup with keyboard and monitor』（CC0）",
        "https://commons.wikimedia.org/wiki/File:RGB_desktop_computer_setup_with_keyboard_and_monitor.jpg",
        "",
        "#落語 #ずんだもん #四国めたん #春日部つむぎ #VOICEVOX #ローカルLLM",
    ])
