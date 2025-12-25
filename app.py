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
    "none": "안 줌(오늘은 패스)",
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
    if gtype == "none":
        return 0
    base = GIFT_BASE.get(gtype, 3)
    fav = MBTI_GIFT_FAV.get(mbti)
    return base + (2 if fav == gtype else 0)

# ---------------- 엔딩 ----------------
def ending_result(aff):
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

    # ✅ 팝업 제어 플래그(중요)
    st.session_state.show_dialog = False

if "started" not in st.session_state:
    reset_all()

def start_game(chars):
    st.session_state.started = True
    st.session_state.day = 1
    st.session_state.people = chars
    st.session_state.aff = {c["name"]: 0 for c in chars}
    st.session_state.log = ["--- Day 1 시작 ---"]
    st.session_state.selected = chars[0]["name"] if chars else None
    st.session_state.acted_today = set()
    st.session_state.gift_used = False
    st.session_state.show_dialog = False

def next_day():
    if st.session_state.day < MAX_DAYS:
        st.session_state.day += 1
        st.session_state.acted_today = set()
        st.session_state.gift_used = False
        st.session_state.log.append(f"--- Day {st.session_state.day} 시작 ---")
        st.session_state.show_dialog = False

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {border:2px solid #E5E5E5;border-radius:14px;padding:12px;margin-bottom:12px;background:white;}
.card-selected {border:2px solid #ff4fa3;background:#fff0f7;}
.pbar-wrap{height:10px;background:#eee;border-radius:999px;overflow:hidden;margin-top:6px;}
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
            name = (name or "").strip() or f"인물{i+1}"
            chars.append({"name": name, "mbti": mbti})

        start_btn = st.form_submit_button("게임 시작")
        reset_btn = st.form_submit_button("전체 초기화")

    if start_btn:
        start_game(chars)
        st.success("게임이 시작되었습니다! '플레이' 탭으로 이동하세요.")

    if reset_btn:
        reset_all()
        st.info("초기화 완료")

# ===== 플레이 =====
with tab2:
    if not st.session_state.started:
        st.info("먼저 시작 설정에서 게임을 시작하세요.")
        st.stop()

    st.metric("DAY", f"{st.session_state.day}/{MAX_DAYS}")
    st.divider()

    # 캐릭터 카드 + 선택 버튼
    st.subheader("👥 캐릭터 카드")
    cols = st.columns(3)

    for i, c in enumerate(st.session_state.people):
        name = c["name"]
        mbti = c["mbti"]
        score = st.session_state.aff.get(name, 0)
        pct = affinity_to_percent(score)
        rel = relation_label(score)
        selected = (st.session_state.selected == name)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="{'card-selected' if selected else 'card'}">
                  <b>{name}</b> · {mbti}
                  <div class="pbar-wrap"><div class="pbar-fill" style="width:{pct}%"></div></div>
                  <div style="margin-top:6px;">호감도 {score} · {rel}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("이 캐릭터 선택", key=f"pick_{name}"):
                st.session_state.selected = name
                st.session_state.show_dialog = False
                st.rerun()

    st.divider()

    sel = st.session_state.selected
    if not sel:
        st.warning("선택된 인물이 없습니다.")
        st.stop()

    sel_mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    # ✅ 팝업 열기 버튼(플래그만 바꿈) — 이것이 ‘원활함’을 보장
    if st.button("상호작용하기 (행동/선물)", type="primary"):
        st.session_state.show_dialog = True
        st.rerun()

    # ✅ 진짜 팝업: show_dialog 플래그가 True일 때만 그리기
    # (버튼 눌렀을 때만 잠깐 정의/호출하는 방식보다 훨씬 안정적)
    if st.session_state.show_dialog:
        @st.dialog(f"오늘 {sel}에게 무엇을 할까?")
        def interact_dialog():
            st.caption("행동: 인물당 하루 1회 / 선물: 하루 1회(단 1명)")

            acted_disabled = (sel in st.session_state.acted_today)
            gift_disabled = st.session_state.gift_used

            action = st.radio(
                "행동 선택",
                list(ACTION_LABEL.keys()),
                format_func=lambda k: ACTION_LABEL[k],
                key=f"dlg_action_{st.session_state.day}_{sel}",
                disabled=acted_disabled
            )

            gift = st.selectbox(
                "선물 선택",
                list(GIFT_LABEL.keys()),
                format_func=lambda k: GIFT_LABEL[k],
                key=f"dlg_gift_{st.session_state.day}_{sel}",
                disabled=gift_disabled
            )

            # ✅ 확인 버튼 1개로 처리(가장 안정)
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("확인(적용)"):
                    delta = 0
                    if not acted_disabled:
                        d = apply_choice(sel_mbti, action)
                        st.session_state.aff[sel] += d
                        st.session_state.acted_today.add(sel)
                        st.session_state.log.append(f"Day {st.session_state.day}: {sel}에게 {ACTION_LABEL[action]} → {d:+d}")
                        delta += d

                    if (gift != "none") and (not gift_disabled):
                        d = apply_gift(sel_mbti, gift)
                        st.session_state.aff[sel] += d
                        st.session_state.gift_used = True
                        st.session_state.log.append(f"Day {st.session_state.day}: {sel}에게 선물({GIFT_LABEL[gift]}) → {d:+d}")
                        delta += d

                    st.session_state.show_dialog = False
                    st.rerun()

            with c2:
                if st.button("닫기"):
                    st.session_state.show_dialog = False
                    st.rerun()

        interact_dialog()

    st.divider()

    # 다음 날
    if st.button("다음 날 ▶️", disabled=st.session_state.day >= MAX_DAYS):
        next_day()
        st.rerun()

    st.divider()

    # ✅ 엔딩 버튼은 14일이 지나야만 “나타남”
    if st.session_state.day >= MAX_DAYS:
        if st.button("엔딩 보기"):
            st.subheader("🎬 엔딩")
            st.write(ending_result(st.session_state.aff))
    else:
        st.caption("엔딩은 14일이 모두 지나면 확인할 수 있습니다.")

    st.divider()
    st.subheader("🧾 로그(최근 30개)")
    st.text("\n".join(st.session_state.log[-30:]))
