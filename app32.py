import streamlit as st
import random
import time
from datetime import datetime

st.set_page_config(page_title="michikusa", layout="centered")

# ---------------------------
# session init
# ---------------------------
def init_session():
    defaults = {
        "show_tutorial": True,
        "page": "input",
        "input_who": "",
        "input_when": "",
        "input_where": "",
        "input_what": "",
        "particle": "で",
        "detour_level": 1,
        "diary": [],
        "favorites": [],
        "generated_batch": [],
        "gacha": [],
        "gacha10": [],
        "last_saved_page": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

import os, json

if os.path.exists("diary.json"):
    with open("diary.json", "r", encoding="utf-8") as f:
        st.session_state.diary = json.load(f)


# ---------------------------
# 軽めの CSS
# ---------------------------
theme = st.get_option("theme.base")  # light / dark

if theme == "dark":
    bg_color = "#0E1117"
    text_color = "#EEE"
    info_bg = "#1E1E1E"
    info_border = "#333"
    card_bg = "#1C1C1C"
    card_border = "#444"
    muted_text = "#AAA"
else:
    bg_color = "#ffffff"
    text_color = "#111"
    info_bg = "#f8fafc"
    info_border = "#eef2ff"
    card_bg = "#ffffff"
    card_border = "#eee"
    muted_text = "#666"

st.markdown(f"""
<style>
body {{
    background: {bg_color};
    color: {text_color};
}}

h1, h2, h3, h4 {{
    color: {text_color};
}}

.info-box {{
    background: {info_bg};
    border: 1px solid {info_border};
    padding: 12px;
    border-radius: 10px;
    font-size: 0.95rem;
}}

.stTextInput>div>div>input {{
    font-size: 1.02rem;
    padding: 8px 10px;
    color: {text_color};
    background: {bg_color};
    border: 1px solid {info_border};
}}

.stButton>button {{
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
}}

.result-box {{
    background: {card_bg};
    border: 1px solid {card_border};
    padding: 12px;
    border-radius: 10px;
    margin-top: 8px;
    color: {text_color};
}}

.final {{
    font-weight: 800;
    font-size: 1.18rem;
    text-align: center;
    margin-top: 12px;
    color: {text_color};
}}

.small-note {{
    color: {muted_text};
    font-size: 0.9rem;
    margin-top: 6px;
}}

.card {{
    background: {card_bg};
    border: 1px solid {card_border};
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 8px;
    color: {text_color};
}}

.stRadio label {{
    color: {text_color} !important;
}}


</style>
""", unsafe_allow_html=True)



# ---------------------------
# vocabulary (kept simple here; you can expand)
# ---------------------------
WHEN_LIST = [
    "今","さっき","今日","ちょっと前","そのとき","ちょうど","一瞬","少し前","気づいたら","なんとなく",
    "今さっき","ほんの今","つい今","ついさっき","さっきのこと","さっきまで","少しさっき","数秒前","数分前","直前",
    "その直後","その少し前","その瞬間","気づいたとき","思い出したとき","ふと","ふいに","ぼんやりしてたら","なにも考えずに","何気なく",
    "タイミングよく","タイミング悪く","中途半端なとき","区切りのないとき","待っている間","立ち止まった瞬間","歩き出した瞬間","止まった瞬間","振り返ったとき","目を離した瞬間",
    "一呼吸おいて","一拍おいて","間を置いて","無意識のうちに","知らないうちに","いつの間にか","気の抜けた瞬間","集中が切れたとき","考え事をしてたとき","ぼーっとしてたとき",
    "急いでいたとき","急いでいないとき","余裕があったとき","余裕がなかったとき","待たされていたとき","待っていなかったとき","立っていたとき","歩いていたとき","止まっていたとき","曲がった直後",
    "曲がる前","通りかかったとき","通り過ぎたあと","戻ったとき","近づいたとき","離れたとき","視線を上げたとき","視線を落としたとき","時計を見たとき","見なかったとき"
]

WHERE_LIST = [
    "コンビニ","駅前","道の真ん中",
    "玄関","リビング","トイレの前","カフェ","レジ横","エレベーター",
    "職場","教室","バス停","公園","駐輪場","スーパー","廊下","交差点",
    "部屋の隅","鏡の前","階段","駐車場","ベッドの上","ソファ","コンロの前",
    "キッチン","洗濯機の横","道路脇","図書館","校門の前","バイト先",
    "ロッカー前","レジ前","ホームセンター","ドラッグストア","駅のホーム",
    "コンビニの入り口","自販機の前","スマホを取り出した場所","信号待ち","カーテンの近く"
]

WHO_LIST = [
    "信号","ドア","列","空気","タイミング","流れ","反応","気配","音","影",
    "自動ドア","エレベーター","風","鳩","時計","照明","表示","画面","ランプ","音声",
    "ボタン","センサー","機械","装置","システム","案内","表示板","モニター","掲示","文字",
    "人","誰か","前の人","後ろの人","隣の人","通りすがりの人","集団","列全体","周囲","空間",
    "場の空気","雰囲気","沈黙","ざわめき","静けさ","視線","目線","足取り","歩幅",
    "影の動き","反射","ガラス","床","天井","壁","振動","この世の全て","気流","温度",
    "音楽","BGM","アナウンス","チャイム","警告音","クリック音","作動音","無音","間","沈黙",
    "時間","スイッチ","一瞬の間","パソコン","チェキ","余白","境目","切り替わり","変化","かたつむり"
]

WHAT_LIST = [
    "直後にバナナの皮で滑った","急に靴ひもがほどけた","ドアに軽くおでこをぶつけた",
    "自動ドアに一回無視された","エレベーターのボタンを全部押してしまった",
    "何もないところでつまずいた","ポケットから小銭を全部落とした","ズボンの裾を踏んだ",
    "スマホを持ってるのに探し始めた","改札で一回引っかかった","ICカードが裏返っていた",
    "傘を開こうとして失敗した","飲み物のフタが固すぎた","急いでるのに赤信号が続いた",
    "なぜか靴下がずれていた","エスカレーターで立ち位置を間違えた","話しかけた相手が別人だった",
    "店員に話しかけたつもりが届かなかった","椅子に座ろうとして浅かった",
    "ちょっとだけコーヒーをこぼした","見過ごされた","通り過ぎた","通り過ぎられた",
    "引っかかった","船漕いでた","止まりかけた","止まりきらなかった","進みかけた",
    "やり直しになった","なかったことになった","余計な一動作が入った","一動作足りなかった","一瞬だけ止まった",
    "笑っていいのか分からなくなった","別の話題に切り替えられた","なかったことにされた","真ん中だけ抜けた","端だけズレた",
    "入れ替わった","順番を飛ばした","順番を守りすぎた","空白ができた","間が空いた",
    "間が詰まった","間違ってはいなかった","正しかったけど遅かった","正しかったけど早すぎた","理由は分からなかった",
    "説明はなかった","特に意味はなかった","偶然っぽかった","わざとじゃなさそうだった","前から決まっていたみたいだった",
    "自販機のボタンを一回多く押した",
    "誰も踏んでない床でちょっと滑った","風で帽子がずれた","紙が一枚めくれただけ","ハンカチが落ちたけど誰も拾わなかった",
    "荷物の角がちょっと当たった","自分の影とぶつかった気がした","ドアノブに手がかかったけど開かなかった",
    "信号が青になった瞬間に止まってた","歩くタイミングを間違えた","前の人の後ろに立ちすぎた","少しだけ列の順番がズレた"
]

ENDINGS = [
    "今日は、空気がちょっとだけ濁ってただけだよ。",
    "たぶん世界が少し寝ぼけてただけだから、あなたのせいじゃないよ。",
    "今日の運勢、三年前に使った消しゴムが決めたらしいから気にしなくてOK。",
    "道があなたに優しくない日って、たまにあるよね。",
    "小さなズレは、明日のおもしろポイントらしいよ。",
    "今日のあなた、ちょっと風に振り回されてただけだと思う。",
    "無理に元気出さなくて大丈夫。靴だって迷う日があるしね。",
    "気配がざわつく日は、早く帰ってお茶して正解だよ。",
    "今日すれ違った人たち、みんなボタンを掛け違えてたらしいよ。",
    "世界がほんの少し揺れてただけ。あなたはいつもどおり。",
    "ドリンクのフタすらうまくいかない日は、何しても可愛いよ。",
    "今日はページのめくり方があなたに厳しかっただけ。",
    "思ったより大変だったね。イスもたぶん応援してたよ。",
    "風の機嫌が悪くて、あなたの髪だけ狙われてたらしい。",
    "今日の疲れは、明日のあなたに返してあげるって世界が言ってた。",
    "あなたの今日の不調、たぶん天気が勝手に決めたんだと思う。",
    "うまくいかない日は、ドアもだいたい固いんだよね。",
    "少しズレてたのは世界のほう。あなたはよくやったよ。",
    "今日のあなた、静かにがんばってて好きだよ。",
    "ちょっとだけ、気持ちが追いつかない時間だったね。",
    "無理しないでいいよ。ペンですら休みたがってた日だし。",
    "今日のモヤは、世界があなたに“ゆっくりしていいよ”って言ってる合図。",
    "あれこれ考えなくても大丈夫。歩幅が戻れば全部うまくいくよ。",
    "気づいてないかもだけど、今日もちゃんとあなた可愛いよ。",
    "大丈夫、今日のあなた柔らかくてすごく良かったよ。",
    "今日は、空がちょっとだけあなたを見守り損ねてただけ。",
    "変な日だったね。でもそれ、あなたのせいじゃないよ。",
    "疲れたら、景色に頼っていいんだよ。たぶん助けてくれるから。",
    "今日のモヤ、明日の光に変換される予定だよ。",
    "お疲れさま。まあそんな日もあるよね。"
]


# ---------------------------
# helpers
# ---------------------------
import json

def save_diary():
    with open("diary.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.diary, f, ensure_ascii=False)

def mix_value(user_value, list_values, keep_ratio=0.2):
    """低めの保持率 -> 基本的にリスト語を使う（ランダム性高め）"""
    if user_value and random.random() < keep_ratio:
        return user_value
    return random.choice(list_values)

def choose_targets(level):
    base = ["when", "where", "who", "what"]
    if level == 1:
        return ["what"]
    elif level == 2:
        return random.sample(base, 2)
    else:
        return base

def build_sentence(when, who, where, what, particle):
    pieces = []
    if when:
        pieces.append(f"{when}、")
    pieces.append(f"{who}が")
    if where:
        pieces.append(f"{where}{particle}")
    if what:
        pieces.append(f"{what}")
    sentence = " ".join(pieces)
    if not sentence.endswith("。"):
        sentence += "。"
    return sentence

def generate_sentence():
    targets = choose_targets(st.session_state.detour_level)

    used_when = mix_value(None, WHEN_LIST, 0.0) if "when" in targets else st.session_state.input_when
    used_where = mix_value(None, WHERE_LIST, 0.0) if "where" in targets else st.session_state.input_where
    used_who = mix_value(None, WHO_LIST, 0.0) if "who" in targets else st.session_state.input_who
    used_what = mix_value(None, WHAT_LIST, 0.0) if "what" in targets else st.session_state.input_what

    return build_sentence(
        used_when,
        used_who,
        used_where,
        used_what,
        st.session_state.particle
    )

import os

def safe_image(path, width=None):
    if os.path.exists(path):
        st.image(path, width=width)


# ---------------------------
# Tutorial page (separate)
# ---------------------------
def tutorial_page():
    st.markdown("<h1 style='text-align:center;'>出来事変換機</h1>", unsafe_allow_html=True)
    st.markdown("モヤモヤの意味付けを一時停止する装置", unsafe_allow_html=True)
    st.markdown("""
                <div class="info-box">日常にある「小さな違和感」をちょっとだけズラすよ。🌀 → 💡<br>
                最近モヤっとしたことを入れてみてね</div>""", unsafe_allow_html=True)
    st.write("")
    img_url = "https://e1w22105-sketch.github.io/stream-demo9/moyamoya_example.png"
    st.image(img_url, caption="例", width=300)
    if st.button("▶ はじめる", use_container_width=True):
        st.session_state.show_tutorial = False
        st.session_state.page = "input"
        st.rerun()
    st.stop()

# ---------------------------
# Input page
# ---------------------------
def page_input():
    st.title("出来事変換機")
    st.markdown('<div class="info-box">モヤモヤの意味付けを一時停止する装置</div>', unsafe_allow_html=True)
    st.write("")

    # ページ切替ボタン
    cols = st.columns([1,1,1])
    if cols[0].button("入力"):
        st.session_state.page = "input"
        st.rerun()
    if cols[1].button("日記"):
        st.session_state.page = "diary"
        st.rerun()
    if cols[2].button("みちくさについて"):
        st.session_state.page = "about"
        st.rerun()

    st.markdown("#### 使い方")
    st.markdown(" 1 思いついたとこだけ入れてみてね")
    st.markdown(" 2 変換してみる／10連ガチャを押してみよう！何がでるかな？")
    st.markdown(" 3 日記に残すと、変換記録が見れるよ")
    st.markdown("---")

    st.markdown("")  # spacing

    # 左右カラム作成（画像用:0.5、入力用:3、画像用:0.5）
    left, center, right = st.columns([0.5, 3, 0.5])

    # 左側に画像を散らす
    with left:
        for i in range(5):
            st.image(f"assets/illust_{i+1:02d}.png", width=random.randint(60,100))

    # 真ん中に入力欄
    with center:
        st.session_state.input_who = st.text_input("居たもの", value=st.session_state.input_who, placeholder="（すれ違った人／猫／歩きスマホ…など）")
        st.markdown('<div>が</div>', unsafe_allow_html=True)
        st.session_state.input_when = st.text_input("そのとき", value=st.session_state.input_when, placeholder="（さっき／昨日／出発前…など）")
        st.session_state.input_where = st.text_input("その場所", value=st.session_state.input_where, placeholder="（駅前／カフェ／道端…など）")
        st.radio(
            "助詞を選択",
            ["で", "に", "も"],
            index=0,
            key="particle"
        )
        st.session_state.input_what = st.text_input("起きたこと", value=st.session_state.input_what, placeholder="（座っていた／遮ってきた…など）")

        st.markdown("##### ずらしレベル")
        st.session_state.detour_level = st.slider(
            "弱 ← → 強",
            1, 3,
            st.session_state.detour_level
        )
        st.markdown(
            "<div class='small-note'>数字が大きくするほど、架空の物語が出来上がります</div>",
            unsafe_allow_html=True
        )

        st.write("")
        with st.columns([1])[0]:
            if st.button("変換してみる"):
                do_transform(times=1)

        

    # 右側に画像を散らす
    with right:
        for i in range(5,10):
            st.image(f"assets/illust_{i+1:02d}.png", width=random.randint(60,100))



# ---------------------------
# transform function
# ---------------------------
def do_transform(times=1):
    st.markdown("""
                <style>
                .waiting-text {
                font-size: 20px;
                color: #FF6600;
                font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.spinner(""):
        st.markdown('<div class="waiting-text">言葉を探しています…</div>', unsafe_allow_html=True)
        time.sleep(2.0)

    batch = []
    for _ in range(times):
        
        targets = choose_targets(st.session_state.detour_level)
        
        used_when = (
            mix_value(None, WHEN_LIST, 0.0)
            if "when" in targets
            else st.session_state.input_when
            )
        
        used_where = (
            mix_value(None, WHERE_LIST, 0.0)
            if "where" in targets
            else st.session_state.input_where
            )
        
        used_who = (
            mix_value(None, WHO_LIST, 0.0)
            if "who" in targets
            else st.session_state.input_who
            )
        
        
        used_what = (
            mix_value(None, WHAT_LIST, 0.0)
            if "what" in targets
            else st.session_state.input_what
            )

        sentence = build_sentence(used_when, used_who, used_where, used_what, st.session_state.particle)
        parts = [used_when, f"{used_who}が", f"{used_where}{st.session_state.particle}" if used_where else "", used_what]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        batch.append({"sentence": sentence, "parts": parts, "time": now})

    st.session_state.generated_batch = batch
    # save to diary
    if st.session_state.last_saved_page != "result":
        for b in reversed(batch):
            st.session_state.diary.insert(0, {"text": b["sentence"], "time": b["time"]})
        save_diary()
        st.session_state.last_saved_page = "result"

    st.session_state.page = "result"
    st.rerun()

# ---------------------------
# 結果ページ（1回／複数分割表示） — ボタンはここに復活
# ---------------------------
def page_result():
    st.markdown(
        """
        <script>
        window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("変換結果")
    batch = st.session_state.get("generated_batch", [])
    if not batch:
        st.info("結果がありません。もう一度入力してみてください。")
        if st.button("戻る"):
            st.session_state.page = "input"
            st.rerun()
        return

    # ---------------------------
    # プレースホルダーを用意
    # ---------------------------
    final_placeholders = [st.empty() for _ in batch]
    part_placeholders = []
    for item in batch:
        part_placeholders.append([st.empty() for _ in item["parts"]])

    # ---------------------------
    # 順番にポンポン表示
    # ---------------------------
    for idx, item in enumerate(batch):
        # まずメインの文章
        final_placeholders[idx].markdown(f"<div class='final'>{item['sentence']}</div>", unsafe_allow_html=True)
        time.sleep(0.25)

        # 各パーツを順番に表示
        labels = ["そのとき", "その場所", "居たもの", "起きたこと"]
        for i, (label, part) in enumerate(zip(labels, item["parts"])):
            display_part = part if part else "—"
            part_placeholders[idx][i].markdown(
                f"<div class='result-box'>{label} → {display_part}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.5)

        st.markdown("")  # spacing

        # per-item controls
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            if st.button("☆ お気に入り", key=f"fav_{idx}"):
                if item["sentence"] not in st.session_state.favorites:
                    st.session_state.favorites.append(item["sentence"])
                st.success("お気に入りに追加しました")
        with c2:
            if st.button("もっと見てみる（10連ガチャ）", key=f"tenbtn_{idx}"):
                st.session_state.page = "gacha10"
                gacha10_results = []
                for _ in range(10):
                    gacha10_results.append({
                        "sentence": generate_sentence(),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                st.session_state.gacha10 = gacha10_results
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if st.session_state.last_saved_page != "gacha10":
                    for item in reversed(gacha10_results):
                        st.session_state.diary.insert(0, {"text": item["sentence"], "time": now})
                    save_diary()
                    st.session_state.last_saved_page = "gacha10"
                st.rerun()
        with c3:
            if st.button("日記を見る", key=f"diarybtn_{idx}"):
                st.session_state.page = "diary"
                st.rerun()

        st.markdown("---")

    # bottom action buttons
    b1, b2, b3 = st.columns([1,1,1])
    with b1:
        if st.button("もう一度"):
            do_transform(times=1)
    with b2:
        if st.button("戻る"):
            st.session_state.page = "input"
            st.rerun()
    with b3:
        if st.button("おしまい"):
            st.session_state.page = "letter"
            st.rerun()

# ---------------------------
# 10連ページ
# --------------------------
def page_gacha10():
    st.markdown(
        """
        <script>
        window.scrollTo(0, 0);
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("🔟 10連ずらし")
    results = st.session_state.gacha10

    if not results:
        st.info("まだ10連の結果がありません。")
        if st.button("戻る"):
            st.session_state.page = "input"
            st.rerun()
        return

    # 順番に表示するためのプレースホルダー
    placeholders = [st.empty() for _ in results]

    for i, r in enumerate(results):
        # 番号と文章を順次表示
        placeholders[i].markdown(f"### {i+1}")
        placeholders[i].markdown(f"<div class='result-box'>{r['sentence']}</div>", unsafe_allow_html=True)
        time.sleep(0.5)  # 少し間を置く

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("戻る"):
            st.session_state.page = "input"
            st.rerun()
    with c2:
        if st.button("もう一度"):
            st.session_state.gacha10 = [
                {"sentence": generate_sentence(), "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                for _ in range(10)
            ]
            st.rerun()
    with c3:
        if st.button("日記を見る"):
            st.session_state.page = "diary"
            st.rerun()
    with c4:
        if st.button("おしまい"):
            st.session_state.page = "letter"
            st.rerun()


# ---------------------------
# Letter (おしまい) page
# ---------------------------
def page_letter():
    st.title("おしまい")
    ending = random.choice(ENDINGS)
    st.markdown(f"<div class='info-box'>{ending}</div>", unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("ホーム"):
            st.session_state.page = "input"
            st.rerun()
    with c2:
        if st.button("日記を見る"):
            st.session_state.page = "diary"
            st.rerun()

# ---------------------------
# Diary page
# ---------------------------
def page_diary():
    st.title("📚 みちくさ日記")
    # tabs: favorites / all
    tab = st.radio("", ("お気に入り", "全て"), index=0 if st.session_state.favorites else 1, horizontal=True)
    st.markdown('<div class="small-note">（この端末のセッション内に保存されています）</div>', unsafe_allow_html=True)
    st.write("")

    if tab == "お気に入り":
        if not st.session_state.favorites:
            st.info("お気に入りがまだありません。結果で☆を押すとここに入ります。")
        else:
            for f in st.session_state.favorites:
                st.markdown(f"<div class='card'>{f}</div>", unsafe_allow_html=True)
    else:
        if not st.session_state.diary:
            st.info("まだ記録がありません。")
        else:
            for e in st.session_state.diary:
                st.markdown(f"<div class='card'><b>{e['time']}</b><br>{e['text']}</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("トップに戻る"):
        st.session_state.page = "input"
        st.rerun()
    if st.button("日記を全部消す"):
        st.session_state.diary = []
        st.session_state.favorites = []
        st.success("日記とお気に入りを削除しました。")
        time.sleep(0.4)
        st.rerun()

# ---------------------------
# Aboutページ（みちくさについて）
# ---------------------------
def page_about():
    st.title("みちくさについて")
    st.markdown("""
                <div class='info-box'>
                みちくさは、日常でふと生まれるモヤっとした出来事を,<br>
                少しだけ違う角度から見てみるツールです。<br>
                入力したことに対して、ちょっとズレた返事が返ってきます。<br>

                励ましでも、アドバイスでも、正解でもありません。<br>
                たぶん役に立たないし、まじめでもないし、予想通りでもないと思います。<br>
                でも、そのズレで「そんな見え方もあるのかも」って一瞬だけ思えたら、それで十分です。<br>

                気持ちを切り替えなくていいし、前向きになる必要もありません。<br>
                考えが詰まったときや、なんとなく気分を変えたいときに、<br>
                少し寄り道する感覚で使ってもらえたら嬉しいです。
                </div>
                """, unsafe_allow_html=True)
    st.write("")
    if st.button("戻る"):
        st.session_state.page = "input"
        st.rerun()


# ---------------------------
# ルーティング
# ---------------------------
if st.session_state.show_tutorial:
    tutorial_page()
else:
    if st.session_state.page == "input":
        page_input()
    elif st.session_state.page == "result":
        page_result()
    elif st.session_state.page == "gacha10":
        page_gacha10()
    elif st.session_state.page == "diary":
        page_diary()
    elif st.session_state.page == "letter":
        page_letter()
    elif st.session_state.page == "about":
        page_about()