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
# 내부 로직 키(eng) -> 화면에 보여줄 한국어(행위)
ACTION_LABEL = {
    "care": "챙겨주기",
    "emotion": "감정 공감하기",
    "logic": "조리 있게 설득하기",
    "plan": "미래 계획 제안하기",
    "fun": "재미있는 농담하기",
    "rule": "규율과 원칙에 대한 이야기",
}

# 내부 로직 키(eng) -> 화면에 보여줄 한국어(선물)
GIFT_LABEL = {
    "sweet": "달콤한 간식",
    "book": "책",
    "handmade": "손편지",
    "practical": "내구성 좋은 필기구",
    "game": "보드게임",
}

# ---------------- 룰(내부키는 그대로 유지) ----------------
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
        return "[Normal End]무사히 합숙을 끝마쳤다!"
    scores = list(aff.values())
    top_name = max(aff, key=aff.get)
    top = aff[top_name]
    avg = sum(scores) / len(scores)
    low_cnt = sum(1 for s in scores if s <= -5)

    if avg < -3:
        return "[Bad End] 어떤 캐릭터와도 더이상은 관계를 이을 수 없을 것 같다..."
    if top >= 18 and low_cnt >= max(2, len(scores)//2):
        return "[Easter Egg] 그렇게 나는 히키코모리가 되었다..."
    if top >= 25:
        return f"특별한 관계 엔딩: {top_name}"
    return "[Normal End]무사히 합숙을 끝마쳤다!"

# ---------------- 관계 상태(호감도 -> 텍스트) ----------------
def relation_label(score: int) -> str:
    if score <= -20:
        return "혐오하는 사이"
    if score <= -10:
        return "싫어하는 사이"
    if score <= -5:
        return "껄끄러운 사이"
    if score <= 4:
        return "어색한 사이"
    if score <= 16:
        return "친한 친구"
    if score <= 24:
        return "호감 상대"
    if score <= 35:
        return "설렘"
    return "특별한 관계"

def affinity_to_percent(score, min_s=-20, max_s=40):
    if score < min_s: score = min_s
    if score > max_s: score = max_s
    return int(round((score - min_s) * 100 / (max_s - min_s)))

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

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
  border: 2px solid #E5E5E5;
  border-radius: 14px;
  padding: 12px;
  margin-bottom: 12px;
  background: white;
}
.card-selected {
  border: 2px solid #ff4fa3 !important;
  background: #fff0f7 !important;
}
.card-title { font-size: 18px; font-weight: 800; margin-bottom: 2px; }
.card-sub { opacity: 0.8; margin-bottom: 8px; }
.card-meta { font-size: 13px; opacity: 0.9; margin-top: 6px; }

.pbar-wrap{
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: #f2f2f2;
  overflow: hidden;
}
.pbar-fill{
  height: 100%;
  background: #ff4fa3; /* 핑크 */
  border-radius: 999px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🏠 N인 합숙 시뮬레이션")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

with tab1:
    st.subheader("인물 생성")
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
        if st.button("게임 시작", type="primary"):
            start_game(chars)
            st.success("시작 완료! '플레이' 탭으로 이동하세요.")
    with c2:
        if st.button("전체 초기화"):
            reset_all()
            st.info("초기화 완료")

with tab2:
    if not st.session_state.started:
        st.info("먼저 '시작 설정'에서 게임을 시작하세요.")
        st.stop()

    st.metric("DAY", f"{st.session_state.day} / {MAX_DAYS}")
    st.divider()

    st.subheader("👥 캐릭터 카드")

    cols = st.columns(3)
    for idx, c in enumerate(st.session_state.people):
        name = c["name"]
        mbti = c["mbti"]
        score = st.session_state.aff.get(name, 0)
        pct = affinity_to_percent(score)
        rel = relation_label(score)
        selected = (st.session_state.selected == name)
        sel_class = "card-selected" if selected else "card"

        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="{sel_class}">
                  <div class="card-title">{name}</div>
                  <div class="card-sub">MBTI: {mbti}</div>
                  <div class="pbar-wrap"><div class="pbar-fill" style="width:{pct}%;"></div></div>
                  <div class="card-meta">호감도: <b>{score}</b> · 생각: <b>{rel}</b></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("이 캐릭터 선택", key=f"pick_{name}"):
                st.session_state.selected = name
                st.rerun()

    st.divider()

    sel = st.session_state.selected
    if not sel:
        st.warning("선택된 인물이 없습니다. '이 캐릭터 선택' 버튼으로 선택하세요.")
        st.stop()

    sel_mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    left, right = st.columns([1, 1])

    with left:
        st.subheader(f"🗣️ 어떤 행동을 할까? (대상: {sel})")
        st.caption("행동은 **인물당 하루 1회**만 가능합니다.")

        action_key = st.radio(
            "행위를 선택하세요",
            list(ACTION_LABEL.keys()),
            format_func=lambda k: ACTION_LABEL[k],
            horizontal=False
        )

        already_acted = (sel in st.session_state.acted_today)
        if st.button("행동 실행", disabled=already_acted):
            d = apply_choice(sel_mbti, action_key)
            st.session_state.aff[sel] += d
            st.session_state.acted_today.add(sel)
            st.session_state.log.append(
                f"Day {st.session_state.day}: {sel}에게 {ACTION_LABEL[action_key]} → {d:+d}"
            )
            st.success(f"{sel} 호감도 {d:+d}")
            st.rerun()

        if already_acted:
            st.info("오늘은 이 인물에게 이미 행동을 했습니다. (인물당 1회 제한)")

    with right:
        st.subheader(f"🎁 선물 (대상: {sel})")
        st.caption("선물은 **하루 1회, 단 1명에게만** 가능합니다.")

        gift_key = st.selectbox(
            "선물을 선택하세요",
            list(GIFT_LABEL.keys()),
            format_func=lambda k: GIFT_LABEL[k]
        )

        if st.button("선물 주기", disabled=st.session_state.gift_used):
            d = apply_gift(sel_mbti, gift_key)
            st.session_state.aff[sel] += d
            st.session_state.gift_used = True
            st.session_state.log.append(
                f"Day {st.session_state.day}: {sel}에게 선물({GIFT_LABEL[gift_key]}) → {d:+d}"
            )
            st.success(f"{sel} 호감도 {d:+d}")
            st.rerun()

        if st.session_state.gift_used:
            st.info("오늘은 이미 선물을 사용했습니다. (하루 1회 제한)")

    # 다음 날 버튼: 행동/선물 아래
    st.divider()
    n1, n2 = st.columns([1, 2])
    with n1:
        if st.button("다음 날 ▶️"):
            if st.session_state.day >= MAX_DAYS:
                st.warning("이미 마지막 날입니다.")
            else:
                next_day()
                st.success("다음 날로 넘어갔습니다.")
                st.rerun()
    with n2:
        st.caption("다음 날이 되면: 행동 제한/선물 제한이 초기화됩니다.")

    st.divider()
    e1, e2 = st.columns([1, 2])
    with e1:
        if st.button("엔딩 보기"):
            st.subheader("🎬 엔딩")
            st.write(ending_result(st.session_state.aff))

    with e2:
        st.subheader("🧾 로그(최근 30개)")
        st.text("\n".join(st.session_state.log[-30:]))
