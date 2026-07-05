import sys
import os
# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_service import extract_json_array
from storage.trip_storage import save_trip, load_trip, delete_trip, list_trips

def test_json_extraction():
    print("Testing JSON extraction...")
    text_with_markdown = """
    여기 요청하신 일정입니다:
    ```json
    [
      {
        "Day": "Day 1",
        "Time": "오전",
        "Activity": "호텔 체크인",
        "Location": "도쿄",
        "Budget": "무료",
        "Memo": "여권을 꼭 챙기세요"
      }
    ]
    ```
    즐거운 여행 되세요!
    """
    
    success, data = extract_json_array(text_with_markdown)
    assert success == True, f"Failed to extract JSON with markdown: {data}"
    assert len(data) == 1
    assert data[0]["Day"] == "Day 1"
    
    text_without_markdown = """
    [
      {
        "Day": "Day 2",
        "Time": "점심",
        "Activity": "스시 먹기",
        "Location": "긴자",
        "Budget": "3000엔",
        "Memo": "웨이팅이 있을 수 있음"
      }
    ]
    """
    success2, data2 = extract_json_array(text_without_markdown)
    assert success2 == True, f"Failed to extract JSON without markdown: {data2}"
    assert len(data2) == 1
    assert data2[0]["Location"] == "긴자"
    print("JSON extraction tests passed!")

def test_storage_logic():
    print("Testing storage logic...")
    trip_name = "테스트용 임시 여행"
    metadata = {
        "trip_name": trip_name,
        "country": "한국",
        "city": "부산",
        "start_date": "2026-07-05",
        "end_date": "2026-07-07",
    }
    schedule = [
        {"Day": "Day 1", "Time": "오전", "Activity": "해운대 해수욕장", "Location": "해운대", "Budget": "무료", "Memo": "바다 감상"}
    ]
    
    # Save
    success, path = save_trip(trip_name, metadata, schedule)
    assert success == True, f"Save failed: {path}"
    assert os.path.exists(path), "File does not exist after save"
    
    # Load
    loaded = load_trip(trip_name)
    assert loaded is not None, "Load failed"
    assert loaded["metadata"]["city"] == "부산"
    assert len(loaded["schedule"]) == 1
    
    # List
    all_trips = list_trips()
    assert any(t["trip_name"] == trip_name for t in all_trips), "Trip not found in list"
    
    # Delete
    deleted = delete_trip(trip_name)
    assert deleted == True, "Delete failed"
    assert not os.path.exists(path), "File still exists after delete"
    print("Storage logic tests passed!")

if __name__ == "__main__":
    test_json_extraction()
    test_storage_logic()
    print("All tests successfully completed!")
