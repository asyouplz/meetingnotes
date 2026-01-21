"""
공통 유틸리티 함수 모듈
"""
import streamlit as st
import hashlib
import os
from datetime import datetime
from config.settings import APP_TITLE, APP_VERSION

def initialize_session_state():
    """세션 상태 변수 초기화"""
    
    # 기본 상태 변수들
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'file_name' not in st.session_state:
        st.session_state.file_name = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'api_keys_set' not in st.session_state:
        st.session_state.api_keys_set = False
    if 'input_method' not in st.session_state:
        st.session_state.input_method = 'text'
    if 'direct_text' not in st.session_state:
        st.session_state.direct_text = ""
    # 타임스탬프 항목을 저장하기 위한 새로운 세션 상태 변수    
    if 'text_entries' not in st.session_state:
        st.session_state.text_entries = []
    if 'need_rerun' not in st.session_state:
        st.session_state.need_rerun = False
    # 파일 처리 추적을 위한 변수
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    # 오디오 변환 정보
    if 'audio_info' not in st.session_state:
        st.session_state.audio_info = {}
    # 선택된 음성 변환 엔진
    if 'speech_to_text_engine' not in st.session_state:
        st.session_state.speech_to_text_engine = "clova"
    # 선택된 회의록 요약 모델
    if 'summary_model' not in st.session_state:
        st.session_state.summary_model = "claude"
    
    # API 키 설정 확인
    try:
        # 먼저 환경 변수에서 API 키 가져오기 시도
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        claude_api_key = os.environ.get("CLAUDE_API_KEY", "")
        naver_client_id = os.environ.get("NAVER_CLIENT_ID", "")
        naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET", "")
        
        # 환경 변수에 없으면 Streamlit Cloud의 secrets에서 API 키 가져오기 시도
        if not openai_api_key and not claude_api_key:
            try:
                openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
                claude_api_key = st.secrets.get("CLAUDE_API_KEY", "")
                
                # 네이버 클로바 API 키 (있을 경우)
                if not naver_client_id or not naver_client_secret:
                    naver_client_id = st.secrets.get("NAVER_CLIENT_ID", "")
                    naver_client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
            except:
                pass
                
        # 세션 상태에 저장
        st.session_state.openai_api_key = openai_api_key
        st.session_state.claude_api_key = claude_api_key
        st.session_state.naver_client_id = naver_client_id
        st.session_state.naver_client_secret = naver_client_secret
            
        # API 키가 설정되었는지 확인
        if st.session_state.openai_api_key and st.session_state.claude_api_key:
            st.session_state.api_keys_set = True
    except Exception as e:
        st.error(f"API 키 설정 중 오류 발생: {e}")
        pass

def get_file_hash(file_content):
    """파일 내용의 해시값 계산 (중복 확인용)"""
    return hashlib.md5(file_content).hexdigest()

def add_entry_with_timestamp(text, source="직접 입력"):
    """타임스탬프와 함께 항목 추가"""
    if not text.strip():  # 빈 텍스트는 추가하지 않음
        return
        
    # 현재 시간 가져오기
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 타임스탬프와 출처, 텍스트를 함께 저장
    entry = {
        "timestamp": timestamp,
        "source": source,
        "text": text
    }
    
    # 세션 상태에 저장
    st.session_state.text_entries.append(entry)
    st.session_state.need_rerun = True

def update_full_transcript():
    """전체 트랜스크립트 업데이트"""
    full_text = ""
    for entry in st.session_state.text_entries:
        full_text += f"[{entry['timestamp']} - {entry['source']}]\n{entry['text']}\n\n"
    
    return full_text

def setup_sidebar():
    """사이드바 설정"""
    st.markdown('<h3>설정</h3>', unsafe_allow_html=True)
    
    # 오디오 변환 엔진 선택
    st.markdown('#### 음성 인식 엔진 선택')
    speech_engine = st.radio(
        "오디오 파일 변환에 사용할 엔진을 선택하세요:",
        ["네이버 클로바 (Clova)", "OpenAI Whisper"],
        index=0 if st.session_state.speech_to_text_engine == "clova" else 1,
        key="speech_engine_radio"
    )
    
    # 라디오 버튼 결과에 따라 세션 상태 업데이트
    if speech_engine == "네이버 클로바 (Clova)":
        st.session_state.speech_to_text_engine = "clova"
    else:
        st.session_state.speech_to_text_engine = "whisper"
    
    # 회의록 요약 모델 선택
    st.markdown('#### 회의록 요약 모델 선택')
    summary_model = st.radio(
        "회의록 요약에 사용할 모델을 선택하세요:",
        ["Anthropic Claude", "OpenAI GPT"],
        index=0 if st.session_state.summary_model == "claude" else 1,
        key="summary_model_radio"
    )
    
    # 라디오 버튼 결과에 따라 세션 상태 업데이트
    if summary_model == "Anthropic Claude":
        st.session_state.summary_model = "claude"
    else:
        st.session_state.summary_model = "openai"
    
    # 앱 초기화 버튼
    st.markdown('---')
    if st.button("앱 완전 초기화", use_container_width=True):
        # 모든 세션 상태 변수 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # 사용 설명서
    st.markdown('---')
    st.markdown('<h3>시스템 사용 방법</h3>', unsafe_allow_html=True)
    st.markdown("""
    **A. TXT 파일로 회의록 생성:**
    1. TXT 파일을 업로드하세요 (텍스트 파일 형식)
    2. 업로드된 텍스트 내용을 확인하고 필요시 수정하세요
    3. '회의록 생성하기' 버튼을 클릭하세요
    
    **B. 텍스트로 직접 회의록 생성:**
    1. '텍스트 직접 입력' 탭을 선택하세요
    2. 회의 내용을 텍스트 영역에 입력하세요
    3. '텍스트 추가' 버튼을 클릭하여 타임스탬프와 함께 저장하세요
    4. 여러 번 텍스트를 추가할 수 있습니다
    5. '회의록 생성하기' 버튼을 클릭하세요
    
    **C. 오디오 파일로 회의록 생성:**
    1. '오디오 파일 업로드' 탭을 선택하세요
    2. 사이드바에서 원하는 음성 인식 엔진을 선택하세요
    3. 회의 녹음 파일을 업로드하세요 (MP3, WAV, M4A 등)
    4. 파일이 자동으로 텍스트로 변환됩니다
    5. 필요시 변환된 텍스트를 수정하세요
    6. '회의록 생성하기' 버튼을 클릭하세요
    """)
    
    # 푸터
    st.markdown('---')
    st.markdown(f'<p class="footer">© 2025 {APP_TITLE} v{APP_VERSION}</p>', unsafe_allow_html=True)