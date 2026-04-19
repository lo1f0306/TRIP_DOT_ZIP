

class StateKeys:
    """
    State에서 공통으로 사용하는 Key들을 정의합니다.
    모든 노드는 이 상수를 참조하여 데이터를 읽고 써야 합니다.
    """
    MESSAGES = "messages"
    INTENT = "intent"
    CONFIDENCE = "confidence"
    ROUTE = "route"
    FINAL_RESPONSE = "final_response"

    # 장소 검색 영역
    DESTINATION = "destination"
    STYLES = "styles"
    CONSTRAINTS = "constraints"
    MAPPED_PLACES = "mapped_places"

    # 일정/날씨 영역
    ITINERARY = "itinerary"
    WEATHER_DATA = "weather_data"