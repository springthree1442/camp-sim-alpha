import streamlit as st

st.set_page_config(page_title="N인 합숙 시뮬", layout="wide")

MAX_DAYS = 14
MBTI_LIST = [
    "INTJ","ENTJ","INTP","ENTP",
    "INFJ","ENFJ","INFP","ENFP",
    "ISTJ","ESTJ","ISFJ","ESFJ",
    "ISTP","ESTP","ISFP","ESFP"
]

# ---------------- 한국어 표시 ----------------
ACTION_LABEL = {
    "care": "챙겨주기",
    "emotion": "감정 공감하기",
    "logic": "조리 있게 설득하기",
    "plan": "미래 계획 제안하기",
    "fun": "재미있는 농담하기",
    "rule": "규율과 원칙에 대해 말하기",
}

GIFT_LABEL = {
    "sweet": "달콤한 간식",
    "book": "책",
    "handmade": "손편지",
    "practical": "내구성 좋은 필기구",
    "game": "보드게임",
}

# ---------------- 룰 ----------------
MBTI_PREF = {
    "INTJ":"plan","ENTJ":"plan","INTP":"logic","ENTP":"logic",
    "INFJ":"care","ENFJ":"care","INFP":"emotion","ENFP":"emotion",
    "ISTJ":"rule","ESTJ":"rule","ISFJ":"care","ESFJ":"care",
    "ISTP":"logic","ESTP":"fun","ISFP":"emotion","ESFP":"fun",
}

CHOICE_EFFECT = {
    "plan": (+8, -2),
    "logic": (+7, -2),
    "care": (+8, -1),
    "emotion": (+7, -1),
    "fun": (+6, -2),
    "rule": (+6, -3),
}

GIFT_BASE = {"sweet":4, "book":4, "handmade":5, "practical":4, "game":3}
MBTI_GIFT_FAV = {"INTJ":"book","INFP":"handmade","ESFP":"game","ISTJ":"practical"}

def apply_choice(mbti, ctype):
    pref = MBTI_PREF.get(mbti, "care")
    good, bad = CHOICE_EFFECT.get(ctype, (+5, -2))
    return good if ctype == pref else bad

def apply_gift(mbti, gtype):
    base = GIFT_BASE.get(gtype, 3)
    fav = MBTI_GIFT_FAV.get(mbti)
    return base + (2 if fav == gtype else 0)

# ---------------- 엔딩 ----------------
def ending_result(aff):
    if not aff:
        return "[Normal End] 무사히 합숙을 끝마쳤다."
    scores = list(aff.values())
    top_name = max(aff, key=aff.get)
    top = aff[top_name]
    avg = sum(scores) / len(scores)
    low_cnt = sum(1 for s in scores if s <= -5)

    if avg < -3:
        return "[Bad End] 누구와도 가까워지지 못했다…"
    if top >= 18 and low_cnt >= max(2, len(scores)//2):
        return "[Easter Egg] 그렇게 나는 히키코모리가 되었다…"
    if top >= 25:
        return f"[Special End] {top_name}과 특별한 관계가 되었다."
    return "[Normal End] 무사히 합숙을 끝마쳤다."

# ---------------- 관계 상태 ----------------
def relation_label(score):
    if score <= -20: return "혐오"
    if score <= -10: return "싫어함"
    if score <= -5:  return "불편함"
    if score <= 4:   return "어색함"
    if score <= 16:  return "친함"
    if score <= 24:  return "호감"
    if score <= 35:  return "설렘"
    return "특별한 관계"

def affinity_to_percent(score, min_s=-20, max_s=40):
    score = max(min(score, max_s), min_s)
    return int((score - min_s) * 100 / (max_s - min_s))

# ---------------- 상태 ----------------
def reset_all():
    st.session_state.started = False
    st.session_state.day = 1
    st.session_state.people = []
    st.session_state.aff = {}
    st.session_state.log = []
    st.session_state.selected = None
    st.session_state.acted_today = set()
    st.session_state.gift_used = False

if "started" not in st.session_state:
    reset_all()

def start_game(chars):
    st.session_state.started = True
    st.session_state.day = 1
    st.session_state.people = chars
    st.session_state.aff = {c["name"]: 0 for c in chars}
    st.session_state.log = ["--- Day 1 시작 ---"]
    st.session_state.selected = chars[0]["name"]
    st.session_state.acted_today = set()
    st.session_state.gift_used = False

def next_day():
    st.session_state.day += 1
    st.session_state.acted_today = set()
    st.session_state.gift_used = False
    st.session_state.log.append(f"--- Day {st.session_state.day} 시작 ---")

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {border:2px solid #E5E5E5;border-radius:14px;padding:12px;margin-bottom:12px;}
.card-selected {border:2px solid #ff4fa3;background:#fff0f7;}
.pbar-wrap{height:10px;background:#eee;border-radius:999px;}
.pbar-fill{height:100%;background:#ff4fa3;border-radius:999px;}
div.stButton>button, div.stFormSubmitButton>button {color:#111 !important;}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🏠 N인 합숙 시뮬레이션")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

# ===== 시작 설정 =====
with tab1:
    st.subheader("인물 생성")

    n = st.number_input("추가할 인물 수(1~12)", 1, 12, 4, 1)

    with st.form("setup_form"):
        chars = []
        for i in range(int(n)):
            c1, c2 = st.columns([2, 1])
            with c1:
                name = st.text_input(f"이름 {i+1}", value=f"인물{i+1}", key=f"name{i}")
            with c2:
                mbti = st.selectbox(f"MBTI {i+1}", MBTI_LIST, index=6, key=f"mbti{i}")
            chars.append({"name": name, "mbti": mbti})

        start_btn = st.form_submit_button("게임 시작")
        reset_btn = st.form_submit_button("전체 초기화")

    if start_btn:
        start_game(chars)
        st.success("게임이 시작되었습니다!")

    if reset_btn:
        reset_all()
        st.info("초기화 완료")

# ===== 플레이 =====
with tab2:
    if not st.session_state.started:
        st.info("시작 설정에서 게임을 시작하세요.")
        st.stop()

    st.metric("DAY", f"{st.session_state.day}/{MAX_DAYS}")
    st.divider()

    cols = st.columns(3)
    for i, c in enumerate(st.session_state.people):
        name = c["name"]
        score = st.session_state.aff[name]
        pct = affinity_to_percent(score)
        rel = relation_label(score)
        selected = (st.session_state.selected == name)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="{'card-selected' if selected else 'card'}">
                <b>{name}</b><br>
                <div class="pbar-wrap"><div class="pbar-fill" style="width:{pct}%"></div></div>
                호감도 {score} · {rel}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("이 캐릭터 선택", key=f"pick{name}"):
                st.session_state.selected = name
                st.rerun()

    st.divider()

    sel = st.session_state.selected
    mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    c1, c2 = st.columns(2)

    with c1:
        action = st.radio(
            "행동 선택",
            list(ACTION_LABEL.keys()),
            format_func=lambda k: ACTION_LABEL[k]
        )
        if st.button("행동 실행", disabled=sel in st.session_state.acted_today):
            d = apply_choice(mbti, action)
            st.session_state.aff[sel] += d
            st.session_state.acted_today.add(sel)
            st.session_state.log.append(f"{sel}에게 {ACTION_LABEL[action]} → {d:+d}")
            st.rerun()

    with c2:
        gift = st.selectbox(
            "선물 선택",
            list(GIFT_LABEL.keys()),
            format_func=lambda k: GIFT_LABEL[k]
        )
        if st.button("선물 주기", disabled=st.session_state.gift_used):
            d = apply_gift(mbti, gift)
            st.session_state.aff[sel] += d
            st.session_state.gift_used = True
            st.session_state.log.append(f"{sel}에게 {GIFT_LABEL[gift]} → {d:+d}")
            st.rerun()

    st.divider()
    if st.button("다음 날 ▶️", disabled=st.session_state.day >= MAX_DAYS):
        next_day()
        st.rerun()

    st.divider()
    if st.button("엔딩 보기"):
        st.write(ending_result(st.session_state.aff))

    st.text("\n".join(st.session_state.log[-30:]))
