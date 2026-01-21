"""
파일 업로드 처리 모듈
"""
import streamlit as st
from modules.utils import get_file_hash, add_entry_with_timestamp

def setup_upload_interface(file_type="txt"):
    """
    파일 업로드 인터페이스 설정
    
    Parameters:
    file_type (str): 업로드할 파일 타입 ("txt" 또는 "audio")
    """
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    if file_type == "txt":
        st.markdown('<h3 class="subheader">TXT 파일 업로드</h3>', unsafe_allow_html=True)
        
        # 통합된 파일 업로더 - Streamlit 기본 UI 사용
        uploaded_file = st.file_uploader("회의 내용이 담긴 TXT 파일을 업로드하세요", type=["txt"], key="txt_uploader")
        
        # 파일이 업로드되면 자동으로 처리
        if uploaded_file:
            process_text_file(uploaded_file)
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_text_file(uploaded_file):
    """
    업로드된 텍스트 파일 처리
    
    Parameters:
    uploaded_file: Streamlit 업로드된 파일 객체
    """
    # 파일 내용 읽기
    file_content = uploaded_file.read()
    
    # 파일 해시값 계산
    file_hash = get_file_hash(file_content)
    
    # 이미 처리한 파일인지 확인 (중복 방지)
    if file_hash not in st.session_state.processed_files:
        st.session_state.file_name = uploaded_file.name
        
        try:
            # TXT 파일 내용을 읽어서 저장
            text = file_content.decode("utf-8")
            # 파일 업로드 시 새로운 항목으로 추가
            if text:
                add_entry_with_timestamp(text, f"텍스트 파일 ({uploaded_file.name})")
                # 처리된 파일 해시값 저장 (중복 방지)
                st.session_state.processed_files[file_hash] = uploaded_file.name
                st.success(f"파일이 업로드되었습니다: {uploaded_file.name}")
            st.session_state.input_method = 'txt'
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")