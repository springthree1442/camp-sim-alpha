import streamlit as st

st.set_page_config(page_title="N인 합숙 시뮬 (베타)", layout="wide")

MAX_DAYS = 14
MBTI_LIST = [
    "INTJ","ENTJ","INTP","ENTP",
    "INFJ","ENFJ","INFP","ENFP",
    "ISTJ","ESTJ","ISFJ","ESFJ",
    "ISTP","ESTP","ISFP","ESFP"
]

# ---------------- 룰(베타1: 알파 룰 유지) ----------------
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

def ending_result(aff):
    if not aff:
        return "노말엔딩"
    scores = list(aff.values())
    top_name = max(aff, key=aff.get)
    top = aff[top_name]
    avg = sum(scores) / len(scores)
    low_cnt = sum(1 for s in scores if s <= -5)

    if avg < -3:
        return "고립엔딩"
    if top >= 18 and low_cnt >= max(2, len(scores)//2):
        return "분열엔딩"
    if top >= 25:
        return f"특별한 관계 엔딩: {top_name}"
    return "노말엔딩"

# ---------------- 상태 ----------------
def reset_all():
    st.session_state.started = False
    st.session_state.day = 1
    st.session_state.people = []     # [{"name","mbti"}], 사용자 제외 캐릭터만 저장
    st.session_state.aff = {}        # {name: score}
    st.session_state.log = []
    st.session_state.selected = None
    st.session_state.acted_today = set()   # 오늘 행동한 인물들
    st.session_state.gift_used = False     # 오늘 선물 사용 여부

if "started" not in st.session_state:
    reset_all()

def start_game(characters):
    st.session_state.started = True
    st.session_state.day = 1
    st.session_state.people = characters
    st.session_state.aff = {c["name"]: 0 for c in characters}
    st.session_state.log = ["--- Day 1 시작 ---"]
    st.session_state.selected = characters[0]["name"] if characters else None
    st.session_state.acted_today = set()
    st.session_state.gift_used = False

def next_day():
    if st.session_state.day < MAX_DAYS:
        st.session_state.day += 1
        st.session_state.acted_today = set()
        st.session_state.gift_used = False
        st.session_state.log.append(f"--- Day {st.session_state.day} 시작 ---")

# 호감도 바 표시용(범위 매핑)
def affinity_to_progress(score, min_s=-20, max_s=40):
    # score를 0~1로 변환
    if score < min_s: score = min_s
    if score > max_s: score = max_s
    return (score - min_s) / (max_s - min_s)

# ---------------- UI ----------------
st.title("🏠 N인 합숙 시뮬레이션 (베타)")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

# ====== 1) 시작 설정 ======
with tab1:
    st.subheader("인물 생성 (MBTI는 드롭다운 선택)")
    n = st.number_input("추가할 인물 수(1~12)", 1, 12, 4, 1)

    chars = []
    for i in range(int(n)):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input(f"이름 {i+1}", value=f"인물{i+1}")
        with col2:
            mbti = st.selectbox(f"MBTI {i+1}", MBTI_LIST, index=6, key=f"mbti_{i}")
        name = (name or "").strip() or f"인물{i+1}"
        chars.append({"name": name, "mbti": mbti})

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("게임 시작(베타)", type="primary"):
            start_game(chars)
            st.success("시작 완료! '플레이' 탭으로 이동하세요.")
    with c2:
        if st.button("전체 초기화"):
            reset_all()
            st.info("초기화 완료")

# ====== 2) 플레이 ======
with tab2:
    if not st.session_state.started:
        st.info("먼저 '시작 설정'에서 게임을 시작하세요.")
        st.stop()

    # 상단 상태
    top_left, top_right = st.columns([1, 1])
    with top_left:
        st.metric("DAY", f"{st.session_state.day} / {MAX_DAYS}")
    with top_right:
        if st.button("다음 날"):
            if st.session_state.day >= MAX_DAYS:
                st.warning("이미 마지막 날입니다.")
            else:
                next_day()
                st.success("다음 날로 넘어갔습니다.")

    st.divider()

    # -------- 캐릭터 카드 영역 (클릭으로 선택) --------
    st.subheader("👥 캐릭터 카드 (카드를 눌러 선택)")

    # 카드 그리드(3열)
    cols = st.columns(3)
    for idx, c in enumerate(st.session_state.people):
        name = c["name"]
        mbti = c["mbti"]
        score = st.session_state.aff.get(name, 0)
        progress = affinity_to_progress(score)

        with cols[idx % 3]:
            selected = (st.session_state.selected == name)

            # 카드 스타일(선택 표시)
            st.markdown(
                f"""
                <div style="
                    border: 2px solid {'#4CAF50' if selected else '#DDD'};
                    border-radius: 12px;
                    padding: 12px;
                    margin-bottom: 12px;
                    background: {'#F3FFF3' if selected else '#FFFFFF'};
                ">
                    <div style="font-size:18px; font-weight:700;">{name}</div>
                    <div style="opacity:0.8;">MBTI: {mbti}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.progress(progress)
            st.caption(f"호감도: {score}")

            # “카드 클릭”은 버튼으로 구현 (Streamlit 한계)
            if st.button("이 인물 선택", key=f"sel_{name}"):
                st.session_state.selected = name

    st.divider()

    # -------- 행동/선물 패널 --------
    sel = st.session_state.selected
    if not sel:
        st.warning("선택된 인물이 없습니다. 위 카드에서 인물을 선택하세요.")
        st.stop()

    sel_mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    left, right = st.columns([1, 1])

    with left:
        st.subheader("🗣️ 오늘 행동")
        st.caption("행동은 **인물당 하루 1회**만 가능합니다.")
        choice = st.radio("행동 타입", ["care", "emotion", "logic", "plan", "fun", "rule"], horizontal=True)

        already_acted = (sel in st.session_state.acted_today)
        if st.button("행동 실행", disabled=already_acted):
            d = apply_choice(sel_mbti, choice)
            st.session_state.aff[sel] += d
            st.session_state.acted_today.add(sel)
            st.session_state.log.append(f"Day {st.session_state.day}: {sel}에게 '{choice}' → {d:+d}")
            st.success(f"{sel} 호감도 {d:+d} (즉시 반영됨)")
            st.rerun()

        if already_acted:
            st.info("오늘은 이 인물에게 이미 행동을 했습니다. (인물당 1회 제한)")

    with right:
        st.subheader("🎁 선물")
        st.caption("선물은 **하루 1회, 단 1명에게만** 가능합니다.")
        gift = st.selectbox("선물 타입", ["sweet", "book", "handmade", "practical", "game"])

        if st.button("선물 주기", disabled=st.session_state.gift_used):
            d = apply_gift(sel_mbti, gift)
            st.session_state.aff[sel] += d
            st.session_state.gift_used = True
            st.session_state.log.append(f"Day {st.session_state.day}: {sel}에게 선물({gift}) → {d:+d}")
            st.success(f"{sel} 호감도 {d:+d} (즉시 반영됨)")
            st.rerun()

        if st.session_state.gift_used:
            st.info("오늘은 이미 선물을 사용했습니다. (하루 1회 제한)")

    st.divider()

    # -------- 엔딩/로그 --------
    e1, e2 = st.columns([1, 2])
    with e1:
        if st.button("엔딩 보기"):
            st.subheader("🎬 엔딩")
            st.write(ending_result(st.session_state.aff))

    with e2:
        st.subheader("🧾 로그(최근 30개)")
        st.text("\n".join(st.session_state.log[-30:]))
