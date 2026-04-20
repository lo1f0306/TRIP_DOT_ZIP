import logging
from llm.graph.state import TravelAgentState
from llm.graph.contracts import StateKeys  # 규약 임포트
from services.intent_service import classify_intent_by_rule

logger = logging.getLogger(__name__)


def route_intent_node(state: TravelAgentState) -> dict:
    """
    사용자의 입력으로부터 의도를 분류하고
    State의 route를 결정하는 첫 번째 노드
    """
    # 1. 메시지 추출 및 안전한 텍스트 획득
    messages = state.get(StateKeys.MESSAGES, [])
    if not messages:
        logger.warning("messages가 비어 있어 기본값으로 general_chat/chat 반환")
        return {
            StateKeys.INTENT: "general_chat",
            StateKeys.CONFIDENCE: 0.0,
            StateKeys.ROUTE: "chat",
        }

    last_msg = messages[-1]

    # 메시지 객체일 경우 .content, 딕셔너리일 경우 get("content") 사용
    user_text = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", "")

    # 2. 의도 분석 실행
    intent_result = classify_intent_by_rule(user_text)

    # 3. 규약된 키값으로 결과 반환
    return {
        StateKeys.INTENT: intent_result["intent"],
        StateKeys.CONFIDENCE: intent_result.get("confidence", 0.0),
        StateKeys.ROUTE: intent_result["route"],
    }