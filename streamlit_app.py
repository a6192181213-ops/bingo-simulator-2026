import streamlit as st
import random
import pandas as pd
import time

# --- 網頁標題與設定 ---
st.set_page_config(page_title="賓果 2026 賺錢模擬器", page_icon="🎲", layout="wide")
st.title("🎰 賓果賓果三星：賺錢模擬器")
st.caption("2026 元宵加碼期間：三星全中 $1,000 | 中 2 碼 $50")



# --- 側邊欄設定 ---
st.sidebar.header("⚙️ 全局參數設定")

# 初始化 session_state
if 'num_periods' not in st.session_state: st.session_state.num_periods = 10
if 'num_sets' not in st.session_state: st.session_state.num_sets = 1

# 套餐 A：分散投資
if st.sidebar.button("🚀 1,000元發財套餐(1倍4組10期)"):
    st.session_state.num_periods = 10
    st.session_state.num_sets = 4
    # 強制將所有可能出現的組別倍率重設為 1
    for i in range(10):
        st.session_state[f"input_mult_{i}"] = 1 # 這裡直接操作元件的 key
    st.rerun()

# 套餐 B：集中火力
if st.sidebar.button("🎯 1,000元發財套餐(1組4倍10期)"):
    st.session_state.num_periods = 10
    st.session_state.num_sets = 1
    # 強制將第一組元件的 key 設為 4
    st.session_state["input_mult_0"] = 4 
    st.rerun()

# 側邊欄滑桿 (使用 state 作為初始值)
num_periods = st.sidebar.slider("模擬期數", 1, 100, value=st.session_state.num_periods)
num_sets = st.sidebar.slider("選擇下注組數", 1, 10, value=st.session_state.num_sets)

# 同步滑桿回 state
st.session_state.num_periods = num_periods
st.session_state.num_sets = num_sets

# --- 主畫面：配置區 ---
st.header("🎯 下注組別配置")
betting_configs = []

for i in range(num_sets):
    # 號碼初始化
    if f"nums_{i}" not in st.session_state:
        st.session_state[f"nums_{i}"] = sorted(random.sample(range(1, 81), 3))
    
    # 倍率初始化（若元件 key 還沒在 state 裡，則補 1）
    if f"input_mult_{i}" not in st.session_state:
        st.session_state[f"input_mult_{i}"] = 1
        
    with st.expander(f"📍 第 {i+1} 組設定", expanded=True):
        col_n, col_m = st.columns([3, 1])
        with col_n:
            selected_nums = st.multiselect(
                f"選擇號碼 (最多3個)", range(1, 81),
                default=st.session_state[f"nums_{i}"],
                max_selections=3, key=f"select_nums_{i}"
            )
            st.session_state[f"nums_{i}"] = selected_nums
            
        with col_m:
            # 修改重點：直接使用 key 綁定 session_state，不手動傳入 value
            # 這樣按鈕修改 st.session_state[f"input_mult_{i}"] 時，畫面會直接同步
            multiplier = st.number_input(
                f"倍率", 
                min_value=1, 
                key=f"input_mult_{i}"
            )
        
        betting_configs.append({"nums": selected_nums, "mult": multiplier})

# --- 核心邏輯 ---
st.divider()
if st.button("🔥 開始賺錢", use_container_width=True):
    for idx, config in enumerate(betting_configs):
        if len(config["nums"]) != 3:
            st.error(f"❌ 第 {idx+1} 組未選滿 3 個號碼。")
            st.stop()

    BINGO_RANGE = range(1, 81)
    results = []
    total_prize = 0
    total_cost = sum(c["mult"] for c in betting_configs) * 25 * num_periods

    for p in range(1, num_periods + 1):
        winning_draw = sorted(random.sample(BINGO_RANGE, 20))
        period_prize = 0
        hits_log = []
        
        for idx, config in enumerate(betting_configs):
            hits = set(config["nums"]).intersection(set(winning_draw))
            n = len(hits)
            m = config["mult"]
            
            p_win = 0
            if n == 3: 
                p_win = 1000 * m
            elif n == 2: 
                p_win = 50 * m 
            
            period_prize += p_win
            if n >= 2: 
                hits_log.append(f"組{idx+1}中{n}碼")

        total_prize += period_prize
        results.append({
            "期數": p,
            "開獎號碼": ", ".join(map(str, winning_draw)),
            "中獎摘要": " / ".join(hits_log) if hits_log else "無",
            "本期獎金": int(period_prize)
        })

    # --- 統計面板 ---
    df = pd.DataFrame(results)
    net = total_prize - total_cost
    
    st.subheader("📊 模擬結果分析")
    m1, m2, m3 = st.columns(3)
    m1.metric("總投入成本", f"${total_cost:,}")
    m2.metric("總回報獎金", f"${total_prize:,}", delta=int(net))
    
    roi = (net / total_cost * 100) if total_cost > 0 else 0
    m3.metric("投資報酬率 (ROI)", f"{roi:.1f}%")

    st.dataframe(df.set_index("期數"), use_container_width=True)
    
    if net > 0:
        st.success(f"💰💰💰 恭喜獲利！賺了 ${net:,} 💰💰💰")
        # 播放中獎音效：Money Sound Effect
        st.audio(f"win.mp3?t={time.time()}", format="audio/mp3", autoplay=True)
    else:
        st.warning(f"虧麻了 $-{abs(net):,}。")
        st.success(f"哪有小孩天天哭 哪有賭徒天天輸 ！!")
        # 播放虧錢音效：Oh No - Sound Effect
        st.audio(f"lose.mp3?t={time.time()}", format="audio/mp3", autoplay=True)
