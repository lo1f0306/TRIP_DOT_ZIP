import streamlit as st
from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(f"DEBUG: OPENAI_API_KEY is {OPENAI_API_KEY}")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="✈️ AI 여행 추천 챗봇",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

/* Root variables */
:root {
    --sky: #0ea5e9;
    --sky-dark: #0369a1;
    --sand: #f5f0e8;
    --ocean: #164e63;
    --coral: #f97316;
    --white: #ffffff;
    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-500: #64748b;
    --gray-700: #334155;
    --shadow: 0 4px 24px rgba(14, 165, 233, 0.12);
    --shadow-lg: 0 8px 40px rgba(14, 165, 233, 0.18);
}

/* Global reset */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #f0f7ff;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* App container */
.main .block-container {
    max-width: 860px;
    padding: 2rem 1.5rem 4rem;
    margin: 0 auto;
}

/* ── Header ── */
.chat-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 1.5rem;
}
.chat-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: var(--ocean);
    margin: 0;
    line-height: 1.2;
}
.chat-header p {
    font-size: 1.05rem;
    color: var(--gray-500);
    margin-top: 0.5rem;
}
.header-accent {
    display: inline-block;
    background: linear-gradient(135deg, var(--sky), var(--coral));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Chat bubbles ── */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.bubble-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 0.6rem;
}
.bubble-wrapper.user { flex-direction: row-reverse; }

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.avatar.bot  { background: linear-gradient(135deg, var(--sky), var(--ocean)); }
.avatar.user { background: linear-gradient(135deg, var(--coral), #fb923c); }

.bubble {
    max-width: 72%;
    padding: 0.85rem 1.1rem;
    border-radius: 1.2rem;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.bubble.bot {
    background: var(--white);
    color: var(--gray-700);
    border-bottom-left-radius: 4px;
}
.bubble.user {
    background: linear-gradient(135deg, var(--sky), var(--sky-dark));
    color: white;
    border-bottom-right-radius: 4px;
}

/* ── Quick-reply buttons ── */
.quick-reply-label {
    font-size: 0.82rem;
    color: var(--gray-500);
    margin: 0.8rem 0 0.4rem 3rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.stButton > button {
    border: 2px solid var(--sky) !important;
    background: white !important;
    color: var(--sky-dark) !important;
    border-radius: 999px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 6px rgba(14,165,233,0.10) !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: var(--sky) !important;
    color: white !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.25) !important;
}

/* Input area */
.stTextInput > div > div > input {
    border: 2px solid var(--gray-200) !important;
    border-radius: 999px !important;
    padding: 0.65rem 1.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    background: white !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--sky) !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.12) !important;
}

/* Send button special style */
div[data-testid="column"]:last-child .stButton > button {
    background: linear-gradient(135deg, var(--sky), var(--sky-dark)) !important;
    color: white !important;
    border: none !important;
    font-size: 1rem !important;
    padding: 0.5rem 1.3rem !important;
}
div[data-testid="column"]:last-child .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* Divider */
hr { border-color: var(--gray-100); margin: 1rem 0; }

/* Sidebar/reset */
.sidebar-btn > button {
    width: 100% !important;
    border-radius: 8px !important;
}

/* Typing indicator */
.typing-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--sky);
    animation: bounce 1.2s infinite;
    margin: 0 2px;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-6px); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)


# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 친절하고 전문적인 AI 여행 추천 챗봇입니다. 이름은 '트래블리(Travelly)'입니다.

역할:
- 사용자의 취향과 조건에 맞는 여행지를 추천해줍니다.
- 추천 시 구체적인 명소, 음식, 활동, 예산, 최적 시즌 정보를 포함합니다.
- 대화를 자연스럽게 이어가며 추가 정보를 수집합니다.
- 구체적인 장소를 추천할 때, 좌표 정보를 포함합니다.

대화 방식:
- 친근하고 따뜻한 톤으로 대화합니다.
- 질문 시 사용자가 선택할 수 있는 옵션을 제시할 때는 [BUTTONS:옵션1|옵션2|옵션3] 형식으로 표시합니다.
- 여행지 추천 시에는 이모지를 활용해 시각적으로 보기 좋게 구성합니다.

버튼 형식 규칙:
- 반드시 [BUTTONS:옵션1|옵션2|옵션3|옵션4] 형식을 정확히 지켜주세요.
- 버튼 개수는 2~5개가 적당합니다.
- 버튼 텍스트는 간결하게 (10자 이내) 작성합니다.

예시:
좋아하는 여행 스타일이 어떻게 되세요? [BUTTONS:휴양/리조트|문화/역사|자연/트레킹|음식 투어|쇼핑]

첫 인사:
안녕하세요! 저는 당신의 완벽한 여행을 도와드릴 트래블리예요 ✈️
어떤 여행을 꿈꾸시나요? 함께 최고의 여행지를 찾아봐요!

[BUTTONS:국내 여행|해외 여행|아직 모르겠어요]"""


# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_buttons(text: str):
    """Extract [BUTTONS:...] from assistant message, return (clean_text, buttons)."""
    import re
    pattern = r'\[BUTTONS:(.*?)\]'
    match = re.search(pattern, text)
    if match:
        clean = re.sub(pattern, '', text).strip()
        buttons = [b.strip() for b in match.group(1).split('|') if b.strip()]
        return clean, buttons
    return text, []


def render_message(role: str, content: str):
    avatar = "🤖" if role == "assistant" else "🧑"
    bubble_class = "bot" if role == "assistant" else "user"
    wrapper_class = "user" if role == "user" else ""
    st.markdown(f"""
    <div class="bubble-wrapper {wrapper_class}">
        <div class="avatar {bubble_class}">{avatar}</div>
        <div class="bubble {bubble_class}">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def get_ai_response(messages: list, api_key: str=OPENAI_API_KEY) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.8,
        max_tokens=800,
    )
    return response.choices[0].message.content


# ── Session State Init ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []       # {role, content}
if "quick_buttons" not in st.session_state:
    st.session_state.quick_buttons = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    st.markdown("---")
    st.markdown("**모델 정보**")
    st.caption("gpt-4o-mini 사용 중")
    st.markdown("---")
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_buttons = []
        st.session_state.initialized = False
        st.session_state.pending_input = None
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h1>✈️ <span class="header-accent">AI 여행 추천</span> 챗봇</h1>
    <p>당신의 완벽한 여행지를 함께 찾아드려요 🌍</p>
</div>
""", unsafe_allow_html=True)


# ── Init greeting ─────────────────────────────────────────────────────────────
# if not api_key:
#     st.info("👈 사이드바에서 OpenAI API Key를 입력해주세요.", icon="🔑")
#     st.stop()

if not st.session_state.initialized:
    with st.spinner("트래블리가 준비 중이에요..."):
        init_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        greeting = get_ai_response(
            init_messages + [{"role": "user", "content": "안녕하세요! 여행 추천을 받고 싶어요."}],
            api_key
        )
    clean, buttons = parse_buttons(greeting)
    st.session_state.messages.append({"role": "assistant", "content": clean})
    st.session_state.quick_buttons = buttons
    st.session_state.initialized = True
    st.rerun()


# ── Chat history ──────────────────────────────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])
st.markdown('</div>', unsafe_allow_html=True)


# ── Quick-reply buttons ───────────────────────────────────────────────────────
def handle_button(label: str):
    st.session_state.pending_input = label
    st.session_state.quick_buttons = []

if st.session_state.quick_buttons:
    st.markdown('<div class="quick-reply-label">빠른 선택</div>', unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.quick_buttons))
    for i, btn_label in enumerate(st.session_state.quick_buttons):
        with cols[i]:
            if st.button(btn_label, key=f"qbtn_{i}"):
                handle_button(btn_label)
                st.rerun()


# ── Process pending input (from button or text) ───────────────────────────────
def process_user_input(user_text: str):
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.quick_buttons = []

    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.spinner("트래블리가 생각 중이에요 ✈️"):
        reply = get_ai_response(api_messages, api_key)

    clean, buttons = parse_buttons(reply)
    st.session_state.messages.append({"role": "assistant", "content": clean})
    st.session_state.quick_buttons = buttons


if st.session_state.pending_input:
    process_user_input(st.session_state.pending_input)
    st.session_state.pending_input = None
    st.rerun()


# ── Text input ────────────────────────────────────────────────────────────────
st.markdown("---")
col_input, col_send = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        label="",
        placeholder="여행에 대해 무엇이든 물어보세요...",
        label_visibility="collapsed",
        key="user_text_input",
    )
with col_send:
    send_clicked = st.button("전송 ➤", use_container_width=True)

if send_clicked and user_input.strip():
    process_user_input(user_input.strip())
    st.rerun()
