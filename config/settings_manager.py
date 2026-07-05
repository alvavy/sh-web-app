import os
import json

SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "api_key": "",
    "selected_model": "gemini-1.5-flash",
    "available_models": [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ]
}

def load_settings():
    """settings.json 파일에서 설정을 로드합니다. 파일이 없으면 기본값을 생성하고 저장합니다."""
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
            # 모든 기본 키가 존재하는지 보장
            updated = False
            for key, val in DEFAULT_SETTINGS.items():
                if key not in settings:
                    settings[key] = val
                    updated = True
            if updated:
                save_settings(settings)
            return settings
    except Exception:
        # 파싱 실패 시 기본값으로 복구 후 저장
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    """설정을 settings.json 파일에 저장합니다."""
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False
