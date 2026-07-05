import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from config.settings_manager import (
    load_settings,
    save_settings,
    AVAILABLE_MODELS
)
from storage.trip_storage import save_trip, load_trip, delete_trip, list_trips
from services.gemini_service import test_connection, generate_schedule, modify_schedule

# 페이지 기본 설정
st.set_page_config(
    page_title="Travelibrary - AI 여행 플래너",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "home"
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {
        "trip_name": "",
        "country": "",
        "city": "",
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=3),
        "flight": "",
        "accommodation": "",
        "companions": "",
        "budget": "",
        "purpose": "",
        "additional_requests": ""
    }
if "current_trip" not in st.session_state:
    st.session_state.current_trip = None
if "settings" not in st.session_state:
    st.session_state.settings = load_settings()

# 로컬 설정 동기화
settings = st.session_state.settings

# 화면 전환 도우미 함수
def navigate_to(screen):
    st.session_state.current_screen = screen
    st.rerun()

# --- HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #1E88E5; font-size: 3rem; margin-bottom: 0.2rem;">Travelibrary ✈️</h1>
    <p style="color: #666; font-size: 1.1rem;">개인 맞춤형 AI 여행 일정 생성 및 관리 프로그램</p>
</div>
""", unsafe_allow_html=True)

# --- 1. 홈 화면 (Home Screen) ---
if st.session_state.current_screen == "home":
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📂 나의 여행 서재")
        trips = list_trips()
        
        if not trips:
            st.info("아직 저장된 여행 일정이 없습니다. 아래의 '여행 계획하기' 버튼을 눌러 첫 일정을 생성해 보세요!")
        else:
            for trip in trips:
                metadata = trip.get("metadata", {})
                updated_at_raw = trip.get("updated_at", "")
                try:
                    updated_at = datetime.fromisoformat(updated_at_raw).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    updated_at = updated_at_raw
                
                with st.container(border=True):
                    col_t1, col_t2 = st.columns([3, 1])
                    with col_t1:
                        st.markdown(f"### 📍 {metadata.get('trip_name', '이름 없는 여행')}")
                        st.caption(f"🌍 {metadata.get('country', '')} - {metadata.get('city', '')} | 📅 {metadata.get('start_date', '')} ~ {metadata.get('end_date', '')}")
                        st.caption(f"🕒 최종 수정: {updated_at}")
                    with col_t2:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("열기", key=f"load_{trip['trip_name']}", use_container_width=True):
                                loaded = load_trip(trip["trip_name"])
                                if loaded:
                                    st.session_state.current_trip = loaded
                                    navigate_to("schedule_view")
                                else:
                                    st.error("일정을 불러오는 데 실패했습니다.")
                        with btn_col2:
                            if st.button("삭제", key=f"del_{trip['trip_name']}", type="secondary", use_container_width=True):
                                if delete_trip(trip["trip_name"]):
                                    st.success(f"'{trip['trip_name']}' 일정을 삭제했습니다.")
                                    st.rerun()
                                else:
                                    st.error("일정 삭제에 실패했습니다.")
                                    
    with col_right:
        st.subheader("⚡ 빠른 도구")
        
        # 버튼을 이쁘게 배치
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("➕ 새로운 여행 계획하기", type="primary", use_container_width=True, size="large"):
            # 위저드 데이터 초기화
            st.session_state.wizard_data = {
                "trip_name": "",
                "country": "",
                "city": "",
                "start_date": date.today(),
                "end_date": date.today() + timedelta(days=3),
                "flight": "",
                "accommodation": "",
                "companions": "",
                "budget": "",
                "purpose": "",
                "additional_requests": ""
            }
            st.session_state.wizard_step = 1
            navigate_to("wizard")
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("⚙️ 환경설정 (Settings)", type="secondary", use_container_width=True):
            navigate_to("settings")
            
        # 가이드라인 안내 박스
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        with st.expander("ℹ️ 사용 가이드", expanded=True):
            st.markdown("""
            1. **환경설정**에서 Google AI Studio API 키를 먼저 입력하고 저장하세요.
            2. **새로운 여행 계획하기** 버튼을 클릭하여 위저드를 따라 세부 정보를 입력하세요.
            3. 생성된 일정을 **직접 수정**하거나 **AI에게 부분 수정**을 요청해 보세요.
            4. 만족스러운 일정은 **저장**하여 언제든 다시 불러올 수 있습니다.
            """)

# --- 2. 위저드 입력 화면 (Wizard Screen) ---
elif st.session_state.current_screen == "wizard":
    st.subheader("➕ 새로운 여행 일정 만들기")
    
    # Progress Bar 및 Step 표시
    step = st.session_state.wizard_step
    progress_val = int((step / 3) * 100)
    st.progress(progress_val)
    st.write(f"**Step {step} of 3**")
    
    # Step 1: 기본 정보
    if step == 1:
        st.markdown("### 🗺️ Step 1. 어디로 가시나요?")
        
        with st.form("wizard_step_1"):
            trip_name = st.text_input("여행 이름", value=st.session_state.wizard_data["trip_name"], placeholder="예: 3박 4일 도쿄 힐링 식도락 여행 (필수)")
            country = st.text_input("국가", value=st.session_state.wizard_data["country"], placeholder="예: 일본 (필수)")
            city = st.text_input("도시", value=st.session_state.wizard_data["city"], placeholder="예: 도쿄 (필수)")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                # date_input의 기본값이 datetime.date 객체인지 확인
                s_date = st.session_state.wizard_data["start_date"]
                if isinstance(s_date, str):
                    s_date = datetime.strptime(s_date, "%Y-%m-%d").date()
                start_date = st.date_input("출발일", value=s_date)
            with col_d2:
                e_date = st.session_state.wizard_data["end_date"]
                if isinstance(e_date, str):
                    e_date = datetime.strptime(e_date, "%Y-%m-%d").date()
                end_date = st.date_input("도착일", value=e_date)
                
            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.form_submit_button("취소", type="secondary", use_container_width=True):
                    navigate_to("home")
            with col_b2:
                if st.form_submit_button("다음 단계로 ➡️", type="primary", use_container_width=True):
                    if not trip_name.strip():
                        st.error("여행 이름을 입력해 주세요!")
                    elif not country.strip():
                        st.error("국가를 입력해 주세요!")
                    elif not city.strip():
                        st.error("도시를 입력해 주세요!")
                    elif start_date > end_date:
                        st.error("날짜 오류: 출발일은 도착일보다 빨라야 합니다!")
                    else:
                        st.session_state.wizard_data["trip_name"] = trip_name
                        st.session_state.wizard_data["country"] = country
                        st.session_state.wizard_data["city"] = city
                        st.session_state.wizard_data["start_date"] = start_date
                        st.session_state.wizard_data["end_date"] = end_date
                        st.session_state.wizard_step = 2
                        st.rerun()

    # Step 2: 이동 및 숙소
    elif step == 2:
        st.markdown("### 🏨 Step 2. 항공편 및 숙소 정보")
        
        with st.form("wizard_step_2"):
            flight = st.text_input("항공편 (선택)", value=st.session_state.wizard_data["flight"], placeholder="예: 대한항공 KE2101 / 오전 9시 출발")
            accommodation = st.text_input("숙소 (선택)", value=st.session_state.wizard_data["accommodation"], placeholder="예: 시부야 에이셀 호텔 도큐")
            companions = st.text_input("동행자 (선택)", value=st.session_state.wizard_data["companions"], placeholder="예: 혼자 / 가족(부모님 동행) / 친구 2명")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.form_submit_button("⬅️ 이전 단계로", use_container_width=True):
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col_b2:
                if st.form_submit_button("다음 단계로 ➡️", type="primary", use_container_width=True):
                    st.session_state.wizard_data["flight"] = flight
                    st.session_state.wizard_data["accommodation"] = accommodation
                    st.session_state.wizard_data["companions"] = companions
                    st.session_state.wizard_step = 3
                    st.rerun()

    # Step 3: 여행 목적 및 기타 요청
    elif step == 3:
        st.markdown("### 🎨 Step 3. 나만의 여행 취향 설계")
        
        with st.form("wizard_step_3"):
            budget = st.text_input("예산 (선택)", value=st.session_state.wizard_data["budget"], placeholder="예: 항공/숙소 제외 100만원")
            purpose = st.text_input("여행 목적 (선택)", value=st.session_state.wizard_data["purpose"], placeholder="예: 식도락, 힐링, 쇼핑, 역사 탐방")
            additional_requests = st.text_area("추가 요청사항 (선택)", value=st.session_state.wizard_data["additional_requests"], placeholder="예: 일정이 너무 바쁘지 않게 하루 2~3개 스폿만 추천해주세요. 현지 스시 맛집은 꼭 포함해주세요.")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.form_submit_button("⬅️ 이전 단계로", use_container_width=True):
                    st.session_state.wizard_step = 2
                    st.rerun()
            with col_b2:
                if st.form_submit_button("✨ AI 일정 생성하기", type="primary", use_container_width=True):
                    st.session_state.wizard_data["budget"] = budget
                    st.session_state.wizard_data["purpose"] = purpose
                    st.session_state.wizard_data["additional_requests"] = additional_requests
                    
                    # API Key 검증
                    api_key = settings.get("api_key", "").strip()
                    if not api_key:
                        st.error("🚨 API Key가 등록되어 있지 않습니다! 환경설정(Settings) 화면에서 API Key를 먼저 저장해 주세요.")
                        if st.form_submit_button("⚙️ 환경설정 화면으로 가기", use_container_width=True):
                            navigate_to("settings")
                    else:
                        with st.spinner("🤖 Gemini AI가 최적의 일정을 설계하는 중입니다. 10~20초 정도 걸릴 수 있습니다..."):
                            # date를 string으로 포맷팅해 전달
                            metadata_for_api = st.session_state.wizard_data.copy()
                            metadata_for_api["start_date"] = str(metadata_for_api["start_date"])
                            metadata_for_api["end_date"] = str(metadata_for_api["end_date"])
                            
                            success, result = generate_schedule(
                                metadata_for_api
                            )
                            
                            if success:
                                # 정상적으로 생성됨
                                st.session_state.current_trip = {
                                    "metadata": metadata_for_api,
                                    "schedule": result
                                }
                                navigate_to("schedule_view")
                            else:
                                # 실패 메시지
                                st.error(f"🚨 일정 생성에 실패했습니다.\n\n오류 상세: {result}")

# --- 3. 일정 관리 및 수정 화면 (Schedule View Screen) ---
elif st.session_state.current_screen == "schedule_view":
    if not st.session_state.current_trip:
        st.warning("선택된 여행 정보가 없습니다.")
        if st.button("홈으로 가기"):
            navigate_to("home")
    else:
        trip = st.session_state.current_trip
        metadata = trip.get("metadata", {})
        schedule = trip.get("schedule", [])
        
        # 상단 네비게이션 및 저장 버튼
        col_nav1, col_nav2 = st.columns([4, 1])
        with col_nav1:
            if st.button("⬅️ 나의 여행 서재로 돌아가기", type="secondary"):
                navigate_to("home")
        with col_nav2:
            if st.button("💾 이 일정 저장하기", type="primary", use_container_width=True):
                # 데이터 유실 방지를 위해 현재 세션 상태에 저장된 schedule을 파일에 덤프
                success, path_or_err = save_trip(metadata["trip_name"], metadata, schedule)
                if success:
                    st.success("🎉 일정이 성공적으로 저장되었습니다!")
                else:
                    st.error(f"🚨 저장 실패: {path_or_err}")
                    
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # 여행 정보 대시보드
        with st.container(border=True):
            st.markdown(f"## 📍 {metadata.get('trip_name', '나의 여행')}")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.markdown(f"**🌍 국가/도시:** {metadata.get('country', '')} - {metadata.get('city', '')}")
                st.markdown(f"**📅 일정:** {metadata.get('start_date', '')} ~ {metadata.get('end_date', '')}")
            with col_info2:
                st.markdown(f"**✈️ 항공편:** {metadata.get('flight', '미지정')}")
                st.markdown(f"**🏨 숙소:** {metadata.get('accommodation', '미지정')}")
            with col_info3:
                st.markdown(f"**👥 동행자:** {metadata.get('companions', '미지정')}")
                st.markdown(f"**💰 예산:** {metadata.get('budget', '미지정')}")
            
            if metadata.get("purpose") or metadata.get("additional_requests"):
                st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                st.markdown(f"**🎯 여행 목적:** {metadata.get('purpose', '-')}")
                st.markdown(f"**💬 추가 요청사항:** {metadata.get('additional_requests', '-')}")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # 일정 수정 설명
        st.markdown("### 📝 일정 상세 정보 (수정 가능)")
        st.caption("💡 팁: 아래 테이블을 더블 클릭해 직접 텍스트를 수정할 수 있습니다. 하단에서 행 추가(➕) 및 삭제(🗑️)도 가능합니다.")
        
        # Pandas DataFrame 로드 및 동적 테이블 세팅
        df = pd.DataFrame(schedule)
        
        # 만약 비어 있는 경우 빈 구조 강제 세팅
        if df.empty:
            df = pd.DataFrame(columns=["Day", "Time", "Activity", "Location", "Budget", "Memo"])
            
        column_config = {
            "Day": st.column_config.TextColumn("일차", width="small", placeholder="Day 1", required=True),
            "Time": st.column_config.SelectboxColumn("시간대", options=["오전", "점심", "오후", "저녁"], width="small", required=True),
            "Activity": st.column_config.TextColumn("활동 내용", width="large", placeholder="활동 상세 입력", required=True),
            "Location": st.column_config.TextColumn("장소/위치", width="medium", placeholder="위치"),
            "Budget": st.column_config.TextColumn("비용", width="small", placeholder="예: 무료"),
            "Memo": st.column_config.TextColumn("메모/팁", width="medium", placeholder="팁")
        }
        
        # 데이터 에디터 바인딩
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            key="trip_data_editor"
        )
        
        # 에디터 수정 사항을 즉시 세션 상태에 반영
        st.session_state.current_trip["schedule"] = edited_df.to_dict(orient="records")
        
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        
        # --- AI 추가 수정 요청 섹션 ---
        st.markdown("### 🤖 AI에게 추가 수정 요청하기")
        st.markdown("""
        현재 일정을 기반으로 AI에게 특정 부분만 자연스럽게 수정을 요구할 수 있습니다.  
        *예시: '둘째 날 오후 일정을 덜 피곤하게 휴식 위주로 바꿔줘', '맛집 하나 더 추가해줘', '비가 올 때 갈 만한 미술관으로 변경해줘'*
        """)
        
        # 폼 구조로 인풋 감싸기
        with st.form("ai_modification_form"):
            mod_request = st.text_input(
                "수정 요청 입력", 
                placeholder="현재 일정을 바탕으로 AI에게 수정 요청할 내용을 입력하세요.",
                label_visibility="collapsed"
            )
            
            btn_sub = st.form_submit_button("⚡ 일정 수정 요청하기", type="primary", use_container_width=True)
            
            if btn_sub:
                api_key = settings.get("api_key", "").strip()
                if not api_key:
                    st.error("🚨 API Key가 등록되어 있지 않습니다! 환경설정(Settings) 화면에서 API Key를 먼저 저장해 주세요.")
                elif not mod_request.strip():
                    st.warning("수정 요청 내용을 입력해 주세요!")
                else:
                    with st.spinner("🤖 Gemini AI가 일정을 수정하고 있습니다. 잠시만 기다려주세요..."):
                        # 데이터가 에디터 세션에 의해 최신화되었으므로 바로 가져다 사용
                        current_schedule = st.session_state.current_trip["schedule"]
                        
                        success, result = modify_schedule(
                            current_schedule,
                            mod_request
                        )
                        
                        if success:
                            st.session_state.current_trip["schedule"] = result
                            st.success("🎉 일정을 성공적으로 수정했습니다!")
                            st.rerun()
                        else:
                            st.error(f"🚨 일정 수정에 실패했습니다.\n\n오류 상세: {result}")

# --- 4. 환경설정 화면 (Settings Screen) ---
elif st.session_state.current_screen == "settings":
    st.subheader("⚙️ 환경설정 (Settings)")
    st.caption("Google AI Studio (Gemini)의 API 키와 사용할 인공지능 모델을 관리합니다.")
    
    with st.form("settings_form"):
        api_key_input = st.text_input(
            "Google AI Studio API Key", 
            value=settings.get("api_key", ""), 
            type="password",
            placeholder="AI Studio에서 발급받은 API Key를 입력하세요 (AIzaSy...)"
        )
        
        # 모델 선택
        model_options = AVAILABLE_MODELS
        current_model = settings.get("model", "gemini-3.5-flash")
        
        # 인덱스 계산
        try:
            default_idx = model_options.index(current_model)
        except ValueError:
            default_idx = 0
            
        selected_model_input = st.selectbox(
            "사용할 Gemini 모델", 
            options=model_options,
            index=default_idx
        )
        
        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
            btn_back = st.form_submit_button("⬅️ 홈으로", use_container_width=True)
            if btn_back:
                navigate_to("home")
        with col_b2:
            btn_save = st.form_submit_button("💾 설정 저장하기", type="primary", use_container_width=True)
            if btn_save:
                new_settings = {
                    "api_key": api_key_input.strip(),
                    "model": selected_model_input,
                    "temperature": settings.get("temperature", 0.7)
                }
                if save_settings(new_settings):
                    st.session_state.settings = new_settings
                    st.success("⚙️ 설정이 성공적으로 저장되었습니다!")
                else:
                    st.error("🚨 설정 저장에 실패했습니다.")
                    
    # 연결 테스트 섹션 (독립 버튼)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### ⚡ 연결 테스트")
        st.caption("현재 저장된 API Key와 선택된 모델로 Gemini API 서버와의 연결을 테스트합니다.")
        
        if st.button("🔌 API 연결 테스트 실행", type="secondary"):
            api_key = settings.get("api_key", "").strip()
            if not api_key:
                st.error("API Key가 존재하지 않습니다. 먼저 API Key를 저장한 후 테스트를 시도하세요.")
            else:
                with st.spinner("Gemini API 서버에 요청을 전송하고 테스트하는 중..."):
                    test_success, test_msg = test_connection()
                    if test_success:
                        st.success(test_msg)
                    else:
                        st.error(test_msg)
