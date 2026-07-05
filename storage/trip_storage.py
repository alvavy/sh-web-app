import os
import json
import re
from datetime import datetime

# 프로젝트 루트에서 saved_trips 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVED_TRIPS_DIR = os.path.join(BASE_DIR, "saved_trips")

def sanitize_filename(filename):
    """파일명으로 사용할 수 없는 특수문자를 제거합니다."""
    # 알파벳, 한글, 숫자, 언더바, 하이픈만 허용
    return re.sub(r'[\\/*?:"<>| ]', '_', filename)

def get_trip_filepath(trip_name):
    """여행 이름을 기반으로 안전한 JSON 파일 경로를 생성합니다."""
    os.makedirs(SAVED_TRIPS_DIR, exist_ok=True)
    sanitized = sanitize_filename(trip_name)
    return os.path.join(SAVED_TRIPS_DIR, f"{sanitized}.json")

def save_trip(trip_name, metadata, schedule):
    """여행 정보를 JSON 파일로 저장합니다.
    
    Args:
        trip_name (str): 여행 이름 (ID 대용)
        metadata (dict): 여행 메타데이터 (도시, 날짜, 동행자 등)
        schedule (list): 일정 목록 (JSON 배열)
    """
    os.makedirs(SAVED_TRIPS_DIR, exist_ok=True)
    file_path = get_trip_filepath(trip_name)
    
    trip_data = {
        "metadata": metadata,
        "schedule": schedule,
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(trip_data, f, ensure_ascii=False, indent=4)
        return True, file_path
    except Exception as e:
        return False, str(e)

def load_trip(trip_name):
    """저장된 여행 정보를 로드합니다."""
    file_path = get_trip_filepath(trip_name)
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def delete_trip(trip_name):
    """저장된 여행 파일을 삭제합니다."""
    file_path = get_trip_filepath(trip_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
    return False

def list_trips():
    """saved_trips 폴더 내의 모든 여행 파일 목록을 가져옵니다.
    각 파일의 메타데이터와 파일명을 리스트로 반환합니다.
    """
    os.makedirs(SAVED_TRIPS_DIR, exist_ok=True)
    trips = []
    
    try:
        for file in os.listdir(SAVED_TRIPS_DIR):
            if file.endswith(".json"):
                file_path = os.path.join(SAVED_TRIPS_DIR, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # 파일 이름에서 .json 제거한 원래 여행 이름 또는 메타데이터의 trip_name 사용
                        trip_name = data.get("metadata", {}).get("trip_name", file[:-5])
                        trips.append({
                            "filename": file,
                            "trip_name": trip_name,
                            "metadata": data.get("metadata", {}),
                            "updated_at": data.get("updated_at", "")
                        })
                except Exception:
                    # 손상된 파일은 건너뜀
                    continue
    except Exception:
        pass
        
    # 최근 수정 순으로 정렬
    trips.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return trips
