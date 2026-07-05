import os
import re
import json
import google.generativeai as genai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "default_prompt.md")

def load_default_prompt():
    """prompts/default_prompt.md 파일의 내용을 읽어옵니다. 없으면 기본 문자열을 반환합니다."""
    if os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    
    # 예외 상황용 하드코딩 대체재
    return """
# AI 여행 일정 생성 지침
- 출력은 반드시 JSON 배열만 반환해야 합니다. (```json ... ```)
- 컬럼 구조: Day, Time, Activity, Location, Budget, Memo
"""

def extract_json_array(text):
    """Gemini 응답 텍스트에서 JSON 배열을 안전하게 추출하여 파싱합니다."""
    # markdown의 ```json ... ``` 또는 ``` ... ``` 추출 시도
    json_pattern = re.compile(r'```(?:json)?\s*(\[.*?\])\s*```', re.DOTALL)
    match = json_pattern.search(text)
    
    if match:
        json_str = match.group(1).strip()
    else:
        # 코드블록이 없으면 처음 '['부터 마지막 ']'까지 추출 시도
        first_bracket = text.find('[')
        last_bracket = text.rfind(']')
        if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
            json_str = text[first_bracket:last_bracket+1].strip()
        else:
            json_str = text.strip()
            
    try:
        data = json.loads(json_str)
        if isinstance(data, list):
            return True, data
        else:
            return False, "추출된 JSON 데이터가 리스트(배열) 형식이 아닙니다."
    except json.JSONDecodeError as e:
        return False, f"JSON 파싱에 실패했습니다: {str(e)}\n추출 데이터: {json_str[:200]}"

def test_connection(api_key, model_name="gemini-1.5-flash"):
    """Google Gemini API 연결 상태를 테스트합니다."""
    if not api_key:
        return False, "API Key가 설정되어 있지 않습니다."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        # 매우 단순한 쿼리로 응답 테스트
        response = model.generate_content("Hello. Reply with 'OK' only.")
        if response and response.text:
            return True, "연결에 성공했습니다!"
        return False, "응답이 비어 있습니다."
    except Exception as e:
        return False, f"연결 테스트 실패: {str(e)}"

def generate_schedule(metadata, api_key, model_name="gemini-1.5-flash"):
    """사용자가 입력한 정보를 바탕으로 Gemini API를 호출하여 새로운 일정을 생성합니다."""
    if not api_key:
        return False, "API Key가 누락되었습니다. 설정 화면에서 API Key를 입력해주세요."
        
    prompt_template = load_default_prompt()
    
    # 템플릿에 데이터 포맷팅
    formatted_prompt = prompt_template.replace("{trip_name}", metadata.get("trip_name", "")) \
                                      .replace("{country}", metadata.get("country", "")) \
                                      .replace("{city}", metadata.get("city", "")) \
                                      .replace("{start_date}", str(metadata.get("start_date", ""))) \
                                      .replace("{end_date}", str(metadata.get("end_date", ""))) \
                                      .replace("{flight}", metadata.get("flight", "")) \
                                      .replace("{accommodation}", metadata.get("accommodation", "")) \
                                      .replace("{companions}", metadata.get("companions", "")) \
                                      .replace("{budget}", metadata.get("budget", "")) \
                                      .replace("{purpose}", metadata.get("purpose", "")) \
                                      .replace("{additional_requests}", metadata.get("additional_requests", ""))
    
    # 새로운 일정 생성 요청 프롬프트
    full_prompt = f"{formatted_prompt}\n\n위 입력 정보와 요구사항에 맞추어 최적의 여행 일정을 Day 1부터 일차별로 작성하여 지침에 명시된 JSON 배열(Markdown json 블록 형태)로 출력해 주세요."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.3}
        )
        
        if not response or not response.text:
            return False, "Gemini API 호출 결과 응답을 받지 못했습니다."
            
        success, parsed_data = extract_json_array(response.text)
        if success:
            return True, parsed_data
        else:
            return False, f"응답 데이터 형식 오류: {parsed_data}"
            
    except Exception as e:
        return False, f"Gemini API 호출 오류: {str(e)}"

def modify_schedule(existing_schedule, modification_request, api_key, model_name="gemini-1.5-flash"):
    """기존 일정과 사용자의 요구사항을 바탕으로 Gemini API를 호출하여 일정을 부분 수정합니다."""
    if not api_key:
        return False, "API Key가 누락되었습니다."
        
    prompt_template = load_default_prompt()
    
    existing_schedule_str = json.dumps(existing_schedule, ensure_ascii=False, indent=2)
    
    full_prompt = f"""
{prompt_template}

=========================================
[현재 저장된 기존 일정 (JSON)]
{existing_schedule_str}
=========================================

[사용자 수정 요청 사항]
"{modification_request}"
=========================================

위 가이드라인과 규칙을 바탕으로, 기존 일정을 사용자의 수정 요청 사항에 맞춰 자연스럽게 변경해 주세요.
반드시 기존 일자의 틀을 무너뜨리지 마세요. 예를 들어 "2일차를 편안하게"라는 요청이라면, 2일차(`Day 2` 행들)의 활동만 덜 걷는 힐링 코스로 교체하고 나머지 날짜들은 가능한 한 그대로 유지해야 합니다.
**최종 수정된 전체 일정**을 반드시 동일한 형태의 JSON 배열(Markdown json 블록 형태)로 다른 텍스트 설명 없이 오직 JSON 데이터만 출력해 주세요.
"""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content(
            full_prompt,
            generation_config={"temperature": 0.2}
        )
        
        if not response or not response.text:
            return False, "Gemini API 호출 결과 응답을 받지 못했습니다."
            
        success, parsed_data = extract_json_array(response.text)
        if success:
            return True, parsed_data
        else:
            return False, f"응답 데이터 형식 오류: {parsed_data}"
            
    except Exception as e:
        return False, f"Gemini API 호출 오류: {str(e)}"
