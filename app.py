import streamlit as st

st.set_page_config(page_title="N인 합숙 시뮬", layout="wide")

MAX_DAYS = 14
MBTI_LIST = [
    "INTJ","ENTJ","INTP","ENTP",
    "INFJ","ENFJ","INFP","ENFP",
    "ISTJ","ESTJ","ISFJ","ESFJ",
    "ISTP","ESTP","ISFP","ESFP"
]

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
    return CHOICE_EFFECT[ctype][0] if MBTI_PREF.get(mbti) == ctype else CHOICE_EFFECT[ctype][1]

def apply_gift(mbti, gtype):
    return GIFT_BASE[gtype] + (2 if MBTI_GIFT_FAV.get(mbti) == gtype else 0)

def ending_result(aff):
    if max(aff.values()) >= 25:
        return "특별한 관계 엔딩"
    return "노말 엔딩"

def reset_all():
    st.session_state.started = False
    st.session_state.day = 1
    st.session_state.people = []
    st.session_state.aff = {}
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
    st.session_state.selected = chars[0]["name"]
    st.session_state.acted_today = set()
    st.session_state.gift_used = False

def next_day():
    st.session_state.day += 1
    st.session_state.acted_today = set()
    st.session_state.gift_used = False

st.title("🏠 N인 합숙 시뮬레이션")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

with tab1:
    n = st.number_input("인물 수", 1, 12, 4)
    with st.form("setup"):
        chars = []
        for i in range(n):
            name = st.text_input(f"이름 {i+1}", value=f"인물{i+1}")
            mbti = st.selectbox(f"MBTI {i+1}", MBTI_LIST, key=f"mbti{i}")
            chars.append({"name": name, "mbti": mbti})
        if st.form_submit_button("게임 시작"):
            start_game(chars)

with tab2:
    if not st.session_state.started:
        st.info("게임을 시작하세요")
        st.stop()

    st.write(f"DAY {st.session_state.day}/{MAX_DAYS}")

    for c in st.session_state.people:
        if st.button(f"{c['name']} 선택"):
            st.session_state.selected = c["name"]

    sel = st.session_state.selected
    mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    # ✅ 실제 팝업 (st.dialog)
    if st.button("상호작용하기"):
        @st.dialog(f"{sel}에게 행동/선물")
        def interact():
            action = st.radio("행동", list(ACTION_LABEL.keys()), format_func=lambda k: ACTION_LABEL[k])
            gift = st.selectbox("선물", list(GIFT_LABEL.keys()), format_func=lambda k: GIFT_LABEL[k])

            if st.button("행동 실행", disabled=sel in st.session_state.acted_today):
                st.session_state.aff[sel] += apply_choice(mbti, action)
                st.session_state.acted_today.add(sel)
                st.rerun()

            if st.button("선물 주기", disabled=st.session_state.gift_used):
                st.session_state.aff[sel] += apply_gift(mbti, gift)
                st.session_state.gift_used = True
                st.rerun()

        interact()

    if st.button("다음 날"):
        next_day()
        st.rerun()

    if st.session_state.day >= MAX_DAYS:
        if st.button("엔딩 보기"):
            st.write(ending_result(st.session_state.aff))
