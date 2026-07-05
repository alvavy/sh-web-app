# AGENTS.md

# Travelibrary

Travelibrary는 개인이 사용하는 AI 기반 여행 일정 관리 프로그램이다.

목표는 복잡한 여행 플랫폼이 아니라,
"여행 생성 → AI 일정 작성 → 수정 → 저장 → 다시 불러오기"
까지 편하게 사용할 수 있는 프로그램을 만드는 것이다.

---

# 개발 원칙

항상 유지보수가 쉬운 구조를 우선한다.

코드를 짧게 작성하는 것보다
읽기 쉽고 수정하기 쉬운 구조를 선호한다.

새로운 기능을 추가할 때는
기존 구조를 최대한 유지한다.

---

# 기술 스택

- Python
- Streamlit
- Google Gemini API (Google AI Studio)
- JSON 저장

---

# 폴더 구조

프로젝트는 다음과 같은 구조를 권장한다.

app.py

ui/

services/

storage/

models/

config/

prompts/

saved_trips/

assets/

필요한 파일이나 폴더는 개발 과정에서 자유롭게 생성해도 된다.

---

# UI 원칙

UI는 Streamlit 기반으로 작성한다.

사용자는 코드를 수정하지 않고 대부분의 기능을 사용할 수 있어야 한다.

입력은 Wizard 형태로 진행한다.

생성된 일정은 수정 가능한 테이블(Data Editor) 형태로 제공한다.

---

# 여행 생성 흐름

1. 여행 정보 입력

2. Gemini 호출

3. 일정 생성

4. 사용자가 일정 수정

5. 저장

6. 다시 불러오기

이 흐름을 가장 중요하게 생각한다.

---

# Wizard 입력

입력은 단계별로 진행한다.

예)

여행 이름

국가

도시

출발일

도착일

항공편

숙소

동행자

예산

여행 목적

추가 요청사항

Session State를 사용하여
입력값이 유지되도록 한다.

---

# Gemini

Google AI Studio의 Gemini API를 사용한다.

Python 공식 SDK를 사용한다.

API Key는 코드에 직접 작성하지 않는다.

설정 화면(Settings)에서 사용자가 직접 입력하고 저장할 수 있도록 구현한다.

settings.json 파일이 없으면 자동 생성한다.

설정 화면에서는

- API Key 입력
- 연결 테스트
- 사용할 모델 선택

정도만 구현하면 된다.

---

# Prompt

Prompt는 코드에 직접 작성하지 않는다.

prompts/default_prompt.md 파일을 생성하여 사용한다.

OpenCode가 기본 Prompt를 작성해도 된다.

---

# 저장 방식

여행 하나당 JSON 파일 하나로 저장한다.

saved_trips/

폴더를 사용한다.

예)

Japan_2027.json

---

# 일정 수정

생성된 일정은

Streamlit Data Editor

또는

동등한 수정 가능한 UI

로 표시한다.

사용자는

직접 수정

행 추가

행 삭제

가 가능해야 한다.

---

# AI 수정

일정을 생성한 이후

"AI에게 수정 요청"

기능을 제공한다.

예)

"둘째 날은 덜 걷게 해줘"

"맛집 하나 추가해줘"

"비 오는 일정으로 수정해줘"

등의 요청을 Gemini에게 전달하여
현재 일정을 수정한다.

처음부터 다시 생성하지 않는다.

---

# 코드 구조

UI와 비즈니스 로직을 분리한다.

Gemini 호출은 services 안에서만 수행한다.

JSON 저장은 storage 안에서만 수행한다.

---

# 오류 처리

다음을 사용자에게 안내한다.

- API Key 없음
- Gemini 호출 실패
- 저장 실패
- 날짜 오류
- 필수 입력 누락

---

# 문서

OpenCode는 필요한 경우

README.md

default_prompt.md

등의 문서를 자유롭게 생성해도 된다.

---

# 개발 방향

항상

"무료 Gemini API와 무료 OpenCode 환경에서도 무리 없이 동작하는가?"

를 기준으로 판단한다.

불필요하게 거대한 구조보다

작지만 완성도 높은 프로그램을 목표로 한다.