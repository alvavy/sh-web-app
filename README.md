# Travelibrary (✈️ AI 여행 일정 플래너)

Travelibrary는 개인이 사용하는 AI 기반 맞춤형 여행 일정 관리 프로그램입니다.  
복잡한 플랫폼 구조가 아닌 **"여행 계획 → AI 일정 작성 → 사용자 수정 → AI 추가 수정 요청 → 저장 → 다시 불러오기"**에 최적화된 직관적인 구조를 제공합니다.

---

## 🛠️ 기술 스택

- **Frontend / UI:** Streamlit
- **AI Integration:** Google Gemini API (google-generativeai SDK)
- **Data Storage:** JSON Local Storage (saved_trips/)

---

## 📂 폴더 구조

```text
Travelibrary/
│
├── app.py                     # Streamlit 메인 애플리케이션
├── requirements.txt           # 프로젝트 의존성 라이브러리
├── README.md                  # 애플리케이션 가이드 및 설명서
│
├── config/
│   ├── settings_manager.py    # 설정 파일(settings.json) 로드 및 저장 관리자
│   └── settings.json          # 사용자 API 키 및 모델 설정 (자동 생성)
│
├── prompts/
│   └── default_prompt.md      # Gemini AI에게 지시할 기본 일정 생성/수정 프롬프트
│
├── services/
│   └── gemini_service.py      # Google Gemini API 통신 및 JSON 결과 파싱 서비스
│
├── storage/
│   └── trip_storage.py        # 여행 계획 로컬 JSON 파일화 및 관리 서비스
│
├── saved_trips/               # 사용자가 저장한 여행 일정이 보관되는 폴더 (자동 생성)
│
└── tests/
    └── test_logic.py          # 데이터 파싱 및 파일 입출력 자가 검증용 테스트 코드
```

---

## 🚀 실행 및 사용 방법

### 1. 패키지 설치
프로젝트에 필요한 핵심 패키지(`streamlit`, `google-generativeai` 등)를 먼저 설치합니다.
```bash
pip install -r requirements.txt
```

### 2. Streamlit 앱 구동
터미널에서 아래 명령어를 실행하여 애플리케이션을 구동합니다.
```bash
streamlit run app.py
```

### 3. 초기 API 설정
1. 앱이 실행되면 우측 상단이나 빠른 도구에 있는 **⚙️ 환경설정 (Settings)** 버튼을 클릭합니다.
2. [Google AI Studio](https://aistudio.google.com/)에서 발급받은 본인의 **Gemini API Key**를 입력합니다.
3. 사용할 인공지능 모델(예: `gemini-1.5-flash`)을 선택한 후 **설정 저장하기**를 클릭합니다.
4. **API 연결 테스트 실행** 버튼을 눌러 성공 문구가 뜨는지 확인합니다.

### 4. 여행 일정 생성 및 관리하기
1. **➕ 새로운 여행 계획하기** 버튼을 눌러 위저드(Wizard)를 시작합니다.
2. 3단계에 거쳐 가볍게 정보를 입력한 후 **AI 일정 생성하기**를 누릅니다.
3. 생성된 일정을 마우스 더블 클릭으로 **직접 편집**하거나, 하단의 **행 추가(➕) / 삭제(🗑️)** 기능을 사용하세요.
4. "둘째 날은 덜 걷게 해줘" 혹은 "맛집 하나 더 추가해줘" 등의 상세 피드백을 적고 **AI에게 추가 수정 요청** 버튼을 누르면 AI가 기존 일정을 토대로 부분 수정해 줍니다.
5. 만족스러운 일정이 완성되면 상단의 **이 일정 저장하기** 버튼을 클릭하여 저장하세요.
6. 저장된 일정은 홈 화면인 **나의 여행 서재**에서 언제든 다시 불러오거나 편리하게 삭제할 수 있습니다.
