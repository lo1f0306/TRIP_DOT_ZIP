from llm.graph.state import TravelAgentState
from services.intent_service import classify_intent_by_rule
from services.place_search_tool import get_places_from_api
from services.scheduler_service import create_schedule

# 1. 의도 분석 노드
def route_intent_node(state: TravelAgentState):
    # state["messages"]에서 마지막 사용자 메시지를 가져옴
    user_text = state["messages"][-1].content
    result = classify_intent_by_rule(user_text)

    # State의 약속된 키(intent, route 등)에 저장
    return {
        "intent": result["intent"],
        "route": result["route"]
    }


# 2. 장소 검색 노드 (place_search_tool.py 참고)
def search_places_node(state: TravelAgentState):
    # State에 저장된 destination, styles 등을 꺼내서 함수 호출
    response = get_places_from_api(
        destination=state.get("destination", "부산"),
        styles=state.get("styles", []),
        constraints=state.get("constraints", [])
    )

    #  mapped_places를 State에 저장 -> 알맹이(places)만 꺼내서 저장
    if isinstance(response, dict) and response.get("status") == "success":
        return {"mapped_places": response["data"]["places"]}
    return {"mapped_places": []}  # 실패 시 빈 리스트


# 3. 일정 생성 노드 (scheduler_service.py 참고)
def scheduler_node(state: TravelAgentState):
    # 검색된 후보지들을 꺼내서 스케줄러에 전달
    itinerary_result = create_schedule(
        places=state["mapped_places"],
        start_time_str="09:00"
    )
    return {"itinerary": itinerary_result}