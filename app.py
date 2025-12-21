import streamlit as st

st.set_page_config(page_title="N인 합숙 시뮬 알파", layout="wide")

MAX_DAYS = 14

# ---------------- 유틸 ----------------
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

# ---------------- 상태 ----------------
if "started" not in st.session_state:
    st.session_state.started = False

if "day" not in st.session_state:
    st.session_state.day = 1

if "people" not in st.session_state:
    st.session_state.people = []   # [{"name":..., "mbti":...}, ...]

if "aff" not in st.session_state:
    st.session_state.aff = {}      # {name: score}

if "gift_used" not in st.session_state:
    st.session_state.gift_used = False

if "log" not in st.session_state:
    st.session_state.log = []

# ---------------- UI ----------------
st.title("🏠 N인 합숙 시뮬레이션 (알파)")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

with tab1:
    st.subheader("인물 추가 (사용자 포함)")
    n = st.number_input("추가할 인물 수(1~12)", 1, 12, 4, 1)

    names = []
    mbtis = []
    c1, c2 = st.columns(2)
    for i in range(int(n)):
        with c1:
            names.append(st.text_input(f"이름 {i+1}", value=f"인물{i+1}"))
        with c2:
            mbtis.append(st.text_input(f"MBTI {i+1} (예: INFP)", value="INFP"))

    if st.button("게임 시작(초기화)", type="primary"):
        people = [{"name": "나(사용자)", "mbti": "USER"}]
        aff = {}
        for nm, mb in zip(names, mbtis):
            nm = (nm or "").strip() or "이름없음"
            mb = ((mb or "").strip().upper() or "INFP")
            people.append({"name": nm, "mbti": mb})
            aff[nm] = 0

        st.session_state.started = True
        st.session_state.day = 1
        st.session_state.people = people
        st.session_state.aff = aff
        st.session_state.gift_used = False
        st.session_state.log = ["--- Day 1 시작 ---"]
        st.success("시작 완료! '플레이' 탭으로 이동하세요.")

with tab2:
    if not st.session_state.started:
        st.info("먼저 '시작 설정'에서 게임을 시작하세요.")
        st.stop()

    left, right = st.columns([1, 1])

    with left:
        st.metric("DAY", f"{st.session_state.day} / {MAX_DAYS}")
        st.write("### 호감도 (사용자 → 인물)")
        st.table(st.session_state.aff)

    with right:
        st.write("### 오늘 행동")
        target = st.selectbox("대상 인물", list(st.session_state.aff.keys()))
        choice = st.radio("행동 타입", ["care", "emotion", "logic", "plan", "fun", "rule"], horizontal=True)

        if st.button("행동 실행"):
            mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == target)
            d = apply_choice(mbti, choice)
            st.session_state.aff[target] += d
            st.session_state.log.append(f"Day {st.session_state.day}: {target}에게 '{choice}' → {d:+d}")
            st.success(f"{target} 호감도 {d:+d}")

        st.write("---")
        st.write("### 선물 (하루 1회)")
        gift = st.selectbox("선물 타입", ["sweet", "book", "handmade", "practical", "game"])

        if st.button("선물 주기", disabled=st.session_state.gift_used):
            mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == target)
            d = apply_gift(mbti, gift)
            st.session_state.aff[target] += d
            st.session_state.gift_used = True
            st.session_state.log.append(f"Day {st.session_state.day}: {target}에게 선물({gift}) → {d:+d}")
            st.success(f"선물 성공! {target} 호감도 {d:+d}")

    st.write("---")
    b1, b2, b3 = st.columns([1, 1, 2])

    with b1:
        if st.button("다음 날"):
            if st.session_state.day >= MAX_DAYS:
                st.warning("이미 마지막 날입니다.")
            else:
                st.session_state.day += 1
                st.session_state.gift_used = False
                st.session_state.log.append(f"--- Day {st.session_state.day} 시작 ---")

    with b2:
        if st.button("엔딩 보기"):
            st.subheader("🎬 엔딩")
            st.write(ending_result(st.session_state.aff))

    with b3:
        st.write("### 로그(최근 25개)")
        st.text("\n".join(st.session_state.log[-25:]))
