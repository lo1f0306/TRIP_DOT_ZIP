import logging
from typing import Literal, TypedDict, Optional, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
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

#====================[내용 추가]================================

# 1. 사용자 정의 타입 반영
IntentType = Literal[
    "general_chat",
    "travel_recommendation",
    "place_search",
    "schedule_generation",
    "weather_query",
    "modify_request",
]

ConstraintType = Literal[
    "채식",
    "실내위주",
    "조용한",
    "반려 동물",
    "아이",
    "아이와 함께"
]

class IntentResult(TypedDict):
    intent: IntentType
    confidence: float
    route: str
    reason: str

# 2. LLM 구조화 출력용 Pydantic 모델
class IntentAnalysis(BaseModel):
    intent: IntentType = Field(description="사용자의 의도 분류")
    confidence: float = Field(description="분류 확신도 (0.0~1.0)")
    reason: str = Field(description="분류 근거")
    destination: Optional[str] = Field(description="사용자가 가고 싶은 여행지(도시)의 이름")
    constraints: List[ConstraintType] = Field(default_factory=list, description="제시된 목록(채식, 실내위주 등) 내에서 사용자의 요구사항을 선택하세요.")
    # "travel_date": state.get(StateKeys.TRAVEL_DATE),

class intent_node():

    def __init__(self, llm: ChatOpenAI):
        # 2. 프롬프트 설계: 시스템 메시지에 역할을 부여하고 대화 기록(MessagesPlaceholder)을 넣습니다.
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                당신은 여행 에이전트의 핵심 지능인 '의도 분석 및 정보 추출기'입니다.
                사용자의 입력을 분석하여 의도를 분류하고, 대화 속에서 여행 관련 정보를 정밀하게 추출하세요.

                [1. 의도 분류 가이드]
                - travel_recommendation: 새로운 여행지 추천을 원하거나, 여행 계획을 시작할 때
                - schedule_generation: 구체적인 날짜, 기간을 언급하며 일정을 짜달라고 할 때
                - place_search: 특정 맛집, 카페, 명소 등 장소 정보만 찾을 때
                - modify_request: "그거 말고", "아니", "바꿔줘" 등 기존 계획의 수정/거절/변경을 원할 때
                - weather_query: 날씨 정보를 물어볼 때
                - general_chat: 인사, 감사, 여행과 무관한 일상 대화

                [2. 정보 추출 규칙]
                - destination: 언급된 도시나 지역명을 추출하세요 (예: '서울 강남', '제주도'). 구체적이지 않으면 null로 둡니다.
                - constraints: 사용자의 요구사항을 아래의 정의된 카테고리로만 매핑하여 리스트로 만드세요.
                * '채식': 비건, 고기 제외, 채식주의 관련 언급 시
                * '실내위주': 비오는 날, 더운 날, 박물관/미술관 선호, 실내 활동 언급 시
                * '조용한': 힐링, 사람 적은 곳, 한적한, 고즈넉한 언급 시
                * '반려동물 동반': 강아지, 고양이, 펫 관련 언급 시
                * '아이와 함께': 예스키즈존, 유모차, 어린이 중심 활동 언급 시
                * '가성비': 저렴한, 싼, 예산 아끼는 언급 시

                [3. 주의 사항]
                - 사용자가 명시적으로 말하지 않은 정보는 추측하여 채우지 말고 null 또는 빈 리스트로 두세요.
                - 이전 대화 맥락(history)을 확인하여, 사용자가 "거기 날씨는?"이라고 한다면 '거기'가 지칭하는 목적지를 destination에 채우세요.
             """),
                MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # 3. 구조화된 출력을 사용하는 체인 생성
        self.chain = self.prompt | llm.with_structured_output(IntentAnalysis)

    def __call__(self, state: TravelAgentState) -> dict:
        print(f'[DEBUG] intent_node __call__: {state}')
        
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
        # intent_result = classify_intent_by_rule(user_text)
        
        # # 규칙 기반 결과가 확실할 때 바로 반환
        # print(f"[DEBUG] Intent node __call__ 규칙결과가 확실할 때 바로 반환 {intent_result["intent"]=}")
        # if intent_result.get("confidence", 0.0) >= 0.9:
        #     return {
        #         StateKeys.INTENT: intent_result["intent"],
        #         StateKeys.CONFIDENCE: intent_result.get("confidence", 0.0),
        #         StateKeys.ROUTE: intent_result["route"],
        #     }

        logger.info("[LLM Path] Invoking OpenAI for intent analysis...")
        print("[DEBUG] [DEBUG] Intent node __call__ LLM 의도 분석")
        # LLM 분석
        llm_result = self.chain.invoke({
            "history": messages[:-1],
            "input": user_text
        })

        # Route 매핑 테이블 # 이거 근데 왤케 이렇게 불편하게 하는지 모르겠음.
        route_map = {
            "modify_request": "modify",
            "weather_query": "weather",
            "schedule_generation": "schedule",
            "place_search": "place",
            "travel_recommendation": "travel",
            "general_chat": "chat"
        }

        return {
            StateKeys.INTENT: llm_result.intent,
            StateKeys.CONFIDENCE: llm_result.confidence,
            StateKeys.ROUTE: route_map.get(llm_result.intent, "chat"),
            # Extract의 정보
            StateKeys.DESTINATION: llm_result.destination,
            StateKeys.CONSTRAINTS: llm_result.constraints,
        }

        # 3. 규약된 키값으로 결과 반환
        # return {
        #     StateKeys.INTENT: intent_result["intent"],
        #     StateKeys.CONFIDENCE: intent_result.get("confidence", 0.0),
        #     StateKeys.ROUTE: intent_result["route"],
        # }       
