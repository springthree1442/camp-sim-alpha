import streamlit as st

st.set_page_config(page_title="N인 합숙 시뮬", layout="wide")

MAX_DAYS = 14
MBTI_LIST = [
    "INTJ","ENTJ","INTP","ENTP",
    "INFJ","ENFJ","INFP","ENFP",
    "ISTJ","ESTJ","ISFJ","ESFJ",
    "ISTP","ESTP","ISFP","ESFP"
]

# ---------------- 행동/선물 ----------------
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

SPECIAL_END_TEXT = {
    "ISTJ": "이 말 하기까지 오래 고민했어. 가볍게 하는 말은 아니고… 나 너 좋아해.",
    "ISFJ": "혹시 부담되면 말해줘. 그래도… 네 생각을 자주 하게 돼서, 그냥 말하고 싶었어.",
    "INTJ": "감정적으로 정리해 봤는데, 이건 일시적인 호감은 아닌 것 같아. 좋아해.",
    "INFJ": "네가 웃을 때마다 마음이 조용해져. 이 감정, 숨기고 싶지 않았어.",
    "ISTP": "이런 말 잘 안 하는데… 같이 있으면 편하고 좋아. 그래서 널 좋아해.",
    "ISFP": "그냥… 네 생각하면 마음이 따뜻해져. 그게 좋아하는 거겠지.",
    "INTP": "이 감정이 뭔지 한참 분석해봤는데, 결론은 하나네. 좋아해.",
    "INFP": "말로 다 못 설명하겠지만… 너는 내 하루를 바꾸는 사람이야.",
    "ESTJ": "돌려 말 안 할게. 나는 네가 좋고, 진지하게 만나보고 싶어.",
    "ESFJ": "네가 웃으면 나도 따라 웃게 돼. 그게 좋아하는 마음인 것 같아.",
    "ENTJ": "시간 낭비는 싫어서 솔직하게 말할게. 너한테 관심 있고, 더 알고 싶어.",
    "ENFJ": "네가 얼마나 좋은 사람인지 계속 느끼고 있어. 그래서 내 마음도 전하고 싶었어.",
    "ESTP": "지금 말 안 하면 후회할 것 같아서. 나, 너 좋아해.",
    "ESFP": "너랑 있으면 하루가 재밌어져! 그래서… 좋아해..!",
    "ENTP": "이건 실험 결과인데—네 옆에 있으면 기분이 확실히 좋아져. ...좋아해.",
    "ENFP": "이상하게, 네 얘기만 나오면 괜히 웃게 돼. 그게 사랑일지도.",
}

def relation_label(score):
    if score <= -30: return "혐오"
    if score <= -20: return "무시"
    if score <= -10: return "싫어함"
    if score <= -1:  return "불편함"
    if score <= 5:   return "어색함"
    if score <= 15:  return "친함"
    if score <= 35:  return "매우 친함"
    if score <= 60:  return "약간 호감"
    if score <= 85:  return "호감"
    if score <= 159: return "설렘"
    return "특별한 관계"

def ending_result(aff):
    if not aff:
        return ["[Normal End] 무사히 합숙을 끝마쳤다."]

    scores = list(aff.values())
    avg = sum(scores) / len(scores)
    low_cnt = sum(1 for s in scores if s <= -5)

    if avg < -3:
        return ["[Bad End] 누구와도 가까워지지 못했다…"]

    if low_cnt >= max(2, len(scores)//2):
        return ["[Easter Egg] 그렇게 나는 히키코모리가 되었다…"]

    special_people = [
        name for name, score in aff.items()
        if relation_label(score) == "특별한 관계"
    ]

    if special_people:
        results = []
        for name in special_people:
            mbti = next((p["mbti"] for p in st.session_state.people if p["name"] == name), "INFP")
            msg = SPECIAL_END_TEXT.get(mbti, "그 여름, 우리는 특별해졌다.")
            results.append(f"[Special End] {name} — {msg}")
        return results

    return ["[Normal End] 무사히 합숙을 끝마쳤다."]

def affinity_to_percent(score, min_s=-20, max_s=40):
    score = max(min(score, max_s), min_s)
    return int((score - min_s) * 100 / (max_s - min_s))

def bar_color(score: int) -> str:
    if score == 0:
        return "#BDBDBD"   # gray
    if score < 0:
        return "#3B82F6"   # blue
    return "#ff4fa3"       # pink

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
    st.session_state.selected = chars[0]["name"] if chars else None
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
.card {border:2px solid #E5E5E5;border-radius:14px;padding:12px;margin-bottom:12px;background:white;}
.card-selected {border:2px solid #22c55e;background:#ecfdf5;}
.pbar-wrap{height:10px;background:#eee;border-radius:999px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:999px;}
div.stButton>button, div.stFormSubmitButton>button {color:#111 !important;}
.notice {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #E5E5E5;
  background: #fafafa;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🏠 N인 합숙 시뮬레이션")

tab1, tab2 = st.tabs(["1) 시작 설정", "2) 플레이"])

# ===== 시작 설정 =====
with tab1:
    st.subheader("인물 생성")
    n = st.number_input("추가할 인물 수(1~12)", 1, 12, 2, 1)

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
        st.info("시작 설정에서 게임을 시작하세요.")
        st.stop()

    st.metric("DAY", f"{st.session_state.day}/{MAX_DAYS}")

    st.markdown(
        "<div class='notice'>🎁 <b>선물은 하루에 1번, 단 1명에게만</b> 줄 수 있어요.</div>",
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("👥 캐릭터 카드")
    cols = st.columns(3)
    for i, c in enumerate(st.session_state.people):
        name = c["name"]
        score = st.session_state.aff.get(name, 0)
        pct = affinity_to_percent(score)
        rel = relation_label(score)
        selected = (st.session_state.selected == name)
        fill_color = bar_color(score)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="{'card-selected' if selected else 'card'}">
                  <b>{name}</b> · {c["mbti"]}<br>
                  <div class="pbar-wrap">
                    <div class="pbar-fill" style="width:{pct}%; background:{fill_color};"></div>
                  </div>
                  호감도 {score} · {rel}
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
        st.warning("선택된 인물이 없습니다.")
        st.stop()

    sel_mbti = next(p["mbti"] for p in st.session_state.people if p["name"] == sel)

    st.subheader(f"🎯 선택된 인물: {sel}")

    with st.popover("말 걸기 (행동/선물)"):
        st.caption("행동: 인물당 하루 1회 / 선물: 하루 1회(1명에게만)")

        st.markdown("### 🗣️ 어떤 말을 해볼까?")
        action = st.radio(
            "행위를 선택하세요",
            list(ACTION_LABEL.keys()),
            format_func=lambda k: ACTION_LABEL[k],
            key="action_pick",
        )
        acted_disabled = (sel in st.session_state.acted_today)

        if st.button("행동 실행", disabled=acted_disabled, key="do_action"):
            d = apply_choice(sel_mbti, action)
            st.session_state.aff[sel] += d
            st.session_state.acted_today.add(sel)
            st.session_state.log.append(
                f"Day {st.session_state.day}: {sel}에게 {ACTION_LABEL[action]} → {d:+d}"
            )
            st.success(f"호감도 {d:+d}")
            st.rerun()

        st.markdown("### 🎁 선물(1일 1인 1회 제한)")
        gift = st.selectbox(
            "선물을 선택하세요",
            list(GIFT_LABEL.keys()),
            format_func=lambda k: GIFT_LABEL[k],   
            key="gift_pick"
        )
        gift_disabled = st.session_state.gift_used

        if st.button("선물 주기", disabled=gift_disabled, key="do_gift"):
            d = apply_gift(sel_mbti, gift)
            st.session_state.aff[sel] += d
            st.session_state.gift_used = True
            st.session_state.log.append(
                f"Day {st.session_state.day}: {sel}에게 선물({GIFT_LABEL[gift]}) → {d:+d}"
            )
            st.success(f"호감도 {d:+d}")
            st.rerun()

    st.divider()

    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("다음 날 ▶️", disabled=st.session_state.day >= MAX_DAYS):
            next_day()
            st.rerun()
    with c2:
        st.caption("다음 날이 되면 행동/선물 제한이 초기화됩니다.")

    st.divider()

    if st.session_state.day >= MAX_DAYS:
        if st.button("엔딩 보기"):
            st.subheader("🎬 엔딩")
            results = ending_result(st.session_state.aff)
            for r in results:
                st.write(r)
    else:
        st.caption("엔딩은 Day 14가 되면 확인할 수 있습니다.")

    st.divider()
    st.subheader("🧾 로그(최근 30개)")
    st.text("\n".join(st.session_state.log[-30:]))
