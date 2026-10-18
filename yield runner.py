"""
Yield Runner 飛天跑車 — Streamlit 外殼

跟「債速配」「固收七人組」同一套做法：
這支程式只負責把 game.html 顯示出來，並把 Supabase 網址、金鑰、車子模型填進去。
遊戲本體（含難度設定）在 game.html 最上面的 CFG 區塊。

資料夾裡要有三個檔案：app.py、game.html、roadster.glb
排行榜沿用 flip_scores 資料表，BOARD_ID = "yield-runner"，跟其他遊戲分開算。
PK 連線用 Supabase Realtime，不需要建新表。
"""

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

PAGE_TITLE = "Yield Runner 飛天跑車"
FRAME_HEIGHT = 720  # 遊戲畫面高度（像素）

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .block-container { padding: 0 !important; max-width: 100% !important; }
      header[data-testid="stHeader"] { display: none; }
      #MainMenu, footer { visibility: hidden; }
      iframe { border: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

HERE = Path(__file__).parent


def get_secret(key: str) -> str:
    """從 secrets 讀一個值，沒設定就回空字串（遊戲仍可單機玩）。"""
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return ""


SUPABASE_URL = get_secret("SUPABASE_URL").rstrip("/")
SUPABASE_ANON_KEY = get_secret("SUPABASE_ANON_KEY")


@st.cache_data(show_spinner=False)
def load_template() -> str:
    return (HERE / "game.html").read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_car() -> str:
    p = HERE / "roadster.glb"
    return base64.b64encode(p.read_bytes()).decode("ascii") if p.exists() else ""


try:
    html = load_template()
except FileNotFoundError:
    st.error("找不到 game.html，請確認它和 app.py 放在同一個資料夾。")
    st.stop()

car_b64 = load_car()
if not car_b64:
    st.warning("找不到 roadster.glb，先用簡易車型代替。", icon="⚠️")

html = html.replace("__SUPABASE_URL__", SUPABASE_URL)
html = html.replace("__SUPABASE_ANON_KEY__", SUPABASE_ANON_KEY)
html = html.replace("__CAR_B64__", car_b64)

if not (SUPABASE_URL and SUPABASE_ANON_KEY):
    st.warning(
        "尚未設定 Supabase：PK 連線和共用排行榜不能用（只能單人練習）。"
        "請在 App settings → Secrets 填入 SUPABASE_URL 和 SUPABASE_ANON_KEY。",
        icon="⚠️",
    )

components.html(html, height=FRAME_HEIGHT)
