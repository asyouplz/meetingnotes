import streamlit as st
from modules.upload import setup_upload_interface
from modules.text_conversion import setup_conversion_interface
from modules.text_management import setup_text_management
from modules.minutes_generator import generate_minutes, setup_minutes_interface
from modules.utils import initialize_session_state
from config.settings import APP_TITLE, APP_ICON, SIDEBAR_STATE

# 페이지 설정
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state=SIDEBAR_STATE
)

# 세션 상태 초기화
initialize_session_state()

# 커스텀 CSS 로드
with open("static/css/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 헤더
st.markdown(f'<h1 class="header">{APP_TITLE}</h1>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    from modules.utils import setup_sidebar
    setup_sidebar()

# 메인 컨텐츠
if not st.session_state.api_keys_set:
    st.warning("API 키가 설정되지 않았습니다.")
else:
    # 탭 생성 - 기능별로 분리
    tab1, tab2, tab3 = st.tabs(["TXT 파일 업로드", "텍스트 직접 입력", "오디오 파일 업로드"])
    
    # 각 탭에 해당 모듈의 인터페이스 설정
    with tab1:
        setup_upload_interface("txt")
    
    with tab2:
        setup_text_management()
    
    with tab3:
        setup_conversion_interface()
    
    # 텍스트 항목 관리 (모든 탭에서 공통)
    from modules.text_management import display_text_entries
    display_text_entries()
    
    # 회의록 생성 섹션 (공통)
    if st.session_state.text_entries:
        setup_minutes_interface()
        
# 재실행이 필요한 경우
if st.session_state.need_rerun:
    st.session_state.need_rerun = False
    st.rerun()