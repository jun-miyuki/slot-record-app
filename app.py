import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

FILENAME = "slot_records.csv"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "users": ["default_user"],
    "machines": ["ハナハナホウオウ〜天翔〜"],
    "shops": {
        "サンシャイン豊見城店": {"換金率": 17.85, "買値": 21.74, "台数": 60}
    }
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False, indent=2)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
def load_data():
    df = pd.read_csv(FILENAME)
    expected_cols = ["ユーザー", "日付", "店舗", "機種", "台番号", "回転数", "BIG回数", "REG回数", "BB確率", "RB確率", "合算", "差枚差分", "収支", "メモ"]
    return df[expected_cols] if set(expected_cols).issubset(df.columns) else pd.DataFrame(columns=expected_cols)
    # 記録処理を続行

def save_record(record):
    df = load_data()
    df = pd.concat([pd.DataFrame([record]), df], ignore_index=True)
    df.to_csv(FILENAME, index=False)
    return df

def calculate_rates(games, bb, rb):
    if games == 0:
        return None, None, None
    bb_rate = games / bb if bb else None
    rb_rate = games / rb if rb else None
    total_rate = games / (bb + rb) if bb + rb else None
    return bb_rate, rb_rate, total_rate

settings = load_settings()

st.set_page_config(page_title="スロット実践記録アプリ", layout="centered")

if 'show_setting' not in st.session_state:
    st.session_state['show_setting'] = False

st.button("🔧 設定画面を表示", on_click=lambda: st.session_state.update({'show_setting': True}))

if st.session_state.get('show_setting'):
    st.title("🔧 設定編集画面")
else:
    st.markdown("<h4 style='text-align:center;'>スロット実践記録アプリ</h4>", unsafe_allow_html=True)

    st.markdown("## ◆基本データ")
    col1, col2 = st.columns(2)
    with col1:
        machine = st.selectbox("使用機種", settings["machines"])
    with col2:
        shop = st.selectbox("店舗", list(settings["shops"].keys()))

    col1, col2 = st.columns(2)
    with col1:
        user = st.selectbox("ユーザー名", settings["users"])
    with col2:
        date = st.date_input("日付", value=datetime.today())
        time = datetime.now().strftime("%H:%M:%S")
        st.text(f"現在時刻: {time}")

    st.markdown("## 🔷 実践前データ")
    number = st.text_input("台番号")
    col1, col2 = st.columns(2)
    with col1:
        all_games = st.number_input("回転数（前）", min_value=0, value=0)
    with col2:
        all_diff = st.number_input("差枚数（前）", value=0)
    col1, col2 = st.columns(2)
    with col1:
        all_bb = st.number_input("BIG回数（前）", min_value=0, value=0)
    with col2:
        all_rb = st.number_input("REG回数（前）", min_value=0, value=0)

    st.markdown("## 🔶 実践中データ")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎰 BIG中")
        bsuika = st.number_input("スイカ数", min_value=0, value=0)
    with col2:
        st.markdown("#### 🎯 REG中")
        bita_suika = st.number_input("ビタ押しスイカ数", min_value=0, value=0)
        st.markdown("#### 🌈 サイドランプ")
        rb_cold = st.number_input("❄️ 寒色", min_value=0, value=0)
        rb_warm = st.number_input("🔥 暖色", min_value=0, value=0)
        rb_rainbow = st.number_input("🌈 虹", min_value=0, value=0)

    st.markdown("#### トップパネル")
    col1, col2 = st.columns(2)
    with col1:
        bb_top_blue = st.number_input("🔵 青 (BIG中)", min_value=0)
        bb_top_yellow = st.number_input("🟡 黄 (BIG中)", min_value=0)
        bb_top_green = st.number_input("🟢 緑 (BIG中)", min_value=0)
        bb_top_red = st.number_input("🔴 赤 (BIG中)", min_value=0)
        bb_top_rainbow = st.number_input("🌈 虹 (BIG中)", min_value=0)
    with col2:
        rb_top_blue = st.number_input("🔵 青 (REG中)", min_value=0)
        rb_top_yellow = st.number_input("🟡 黄 (REG中)", min_value=0)
        rb_top_green = st.number_input("🟢 緑 (REG中)", min_value=0)
        rb_top_red = st.number_input("🔴 赤 (REG中)", min_value=0)
        rb_top_rainbow = st.number_input("🌈 虹 (REG中)", min_value=0)

    memo = st.text_area("メモ", height=150)

    st.markdown("## 終了時")
    col1, col2 = st.columns(2)
    with col1:
        seat_games = st.number_input("回転数", min_value=0)
        seat_bb = st.number_input("BIG回数", min_value=0)
    with col2:
        seat_diff = st.number_input("差枚数", value=0)
        seat_rb = st.number_input("REG回数", min_value=0)

    if st.button("✨ 計算する"):
        total_games = all_games + seat_games
        total_bb = all_bb + seat_bb
        total_rb = all_rb + seat_rb
        diff = seat_diff - all_diff
        profit = diff * settings["shops"][shop]["換金率"]
        bb_rate, rb_rate, total_rate = calculate_rates(total_games, total_bb, total_rb)
        if None in (bb_rate, rb_rate, total_rate):
            st.warning("計算に必要なデータが不足しています")
        else:
            st.session_state['calc_summary'] = {
                "BB確率": f"{bb_rate:.1f}",
                "RB確率": f"{rb_rate:.1f}",
                "合算": f"{total_rate:.1f}",
                "差枚差分": diff,
                "収支": f"約 {profit:.0f}円",
                "回転数": seat_games,
                "BIG回数": seat_bb,
                "REG回数": seat_rb
            }
            with st.expander("📊 入力データと計算結果の確認"):
                for k, v in st.session_state['calc_summary'].items():
                    st.write(f"{k}: {v}")

    col1, col2 = st.columns(2)
    with col1:

        if st.button("💾 記録する"):
            if not number or seat_games == 0 or seat_bb == 0 or seat_rb == 0:
                st.warning("台番号、終了時回転数、BIG回数、REG回数は必須です")
            elif "calc_summary" not in st.session_state:
                st.warning("先に計算を実行してください")
            else:
                record = {
                    "ユーザー": user,
                    "日付": date.strftime("%Y-%m-%d"),
                    "店舗": shop,
                    "機種": machine,
                    "台番号": number,
                    "回転数": seat_games,
                    "BIG回数": seat_bb,
                    "REG回数": seat_rb,
                    "BB確率": st.session_state.get('calc_summary', {}).get("BB確率"),
                    "RB確率": st.session_state.get('calc_summary', {}).get("RB確率"),
                    "合算": st.session_state.get('calc_summary', {}).get("合算"),
                    "差枚差分": st.session_state.get('calc_summary', {}).get("差枚差分"),
                    "収支": st.session_state.get('calc_summary', {}).get("収支"),
                    "メモ": memo
                }
                save_record(record)
                st.success("記録を保存しました")
                with st.expander("📊 記録内容の確認"):
                    for k, v in record.items():
                        st.write(f"{k}: {v}")

    with col2:
        if st.button("🗑️ 最新の記録を削除"):
            df = load_data()
            if not df.empty:
                df = df[:-1]
                df.to_csv(FILENAME, index=False)
                st.success("最新の記録を削除しました")
            else:
                st.warning("削除する記録がありません")

    st.markdown("## 📋 記録一覧")
    df = load_data()
    if not df.empty:
        df_display = df[df["ユーザー"] == user] if user else df.copy()
        st.dataframe(df_display.head(10)) 
