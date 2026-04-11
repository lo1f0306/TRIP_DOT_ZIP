# app.py
import streamlit as st

from constants import SYSTEM_PROMPT
from utils import init_app, reset_session_state, parse_buttons, render_message, get_ai_response


# 페이지 기본 설정
st.set_page_config(
    page_title="✈️ AI 여행 추천 챗봇",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# app.py 초기화
# css 적용/ 세션스테이트 초기화
init_app()


# 사이드바
with st.sidebar:
    st.markdown("---")
    st.markdown("**모델 정보**")
    st.caption("gpt-4o-mini 사용 중")
    st.markdown("---")

    if st.button("🔄 대화 초기화", use_container_width=True):
        reset_session_state()
        st.rerun()


# 헤더
st.markdown("""
<div class="chat-header">
    <h1>✈️ <span class="header-accent">AI 여행 추천</span> 챗봇</h1>
    <p>당신의 완벽한 여행지를 함께 찾아드려요 🌍</p>
</div>
""", unsafe_allow_html=True)


# 최초 인사 메시지 생성
if not st.session_state.initialized:
    with st.spinner("트립닷집이 준비 중이에요..."):
        init_payload = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": "안녕하세요! 여행 추천을 받고 싶어요."}
        ]
        greeting_raw = get_ai_response(init_payload)

    greeting_text, greeting_buttons = parse_buttons(greeting_raw)
    st.session_state.messages.append({"role": "assistant", "content": greeting_text})
    st.session_state.quick_buttons = greeting_buttons
    st.session_state.initialized   = True
    st.rerun()


# 대화 히스토리 렌더링
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])
st.markdown('</div>', unsafe_allow_html=True)


# 빠른 선택 버튼
def handle_button_click(label):
    st.session_state.pending_input = label
    st.session_state.quick_buttons = []

if st.session_state.quick_buttons:
    st.markdown('<div class="quick-reply-label">빠른 선택</div>', unsafe_allow_html=True)
    btn_count = len(st.session_state.quick_buttons)
    cols      = st.columns(btn_count)

    for idx, btn_label in enumerate(st.session_state.quick_buttons):
        with cols[idx]:
            if st.button(btn_label, key="qbtn_" + str(idx)):
                handle_button_click(btn_label)
                st.rerun()


# 유저 입력 처리 (버튼 클릭 or 텍스트 전송 공통)
def process_user_input(user_text):
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.quick_buttons = []

    # 시스템 프롬프트 + 전체 대화 히스토리를 매번 넘겨줘야 함
    # Stateless라서 자바 서버처럼 서버에 상태 안 남음 - 이게 GPT API 방식
    api_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        api_payload.append({"role": m["role"], "content": m["content"]})

    with st.spinner("트립닷집이 생각 중이에요 ✈️"):
        raw_reply = get_ai_response(api_payload)

    reply_text, reply_buttons = parse_buttons(raw_reply)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    st.session_state.quick_buttons = reply_buttons


if st.session_state.pending_input is not None:
    process_user_input(st.session_state.pending_input)
    st.session_state.pending_input = None
    st.rerun()


# 텍스트 입력창 + 전송 버튼
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
    is_send_clicked = st.button("전송 ➤", use_container_width=True)

if is_send_clicked and user_input.strip():
    process_user_input(user_input.strip())
    st.rerun()