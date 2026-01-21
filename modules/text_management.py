"""
텍스트 확정 및 관리 모듈
"""
import streamlit as st
from datetime import datetime
from modules.utils import add_entry_with_timestamp

def setup_text_management():
    """텍스트 직접 입력 인터페이스 설정"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    st.markdown('<h3 class="subheader">텍스트 직접 입력</h3>', unsafe_allow_html=True)
    st.write("회의 내용을 텍스트로 직접 입력하세요. 여러 차례 입력하면 타임스탬프와 함께 저장됩니다.")
    
    # 텍스트 입력 영역 (세션 상태에 저장)
    user_input = st.text_area(
        "회의 내용을 여기에 입력하세요:",
        value=st.session_state.direct_text,
        height=150,
        key="direct_text_input"
    )
    
    # 버튼이 클릭되면 직접 세션 상태에 저장
    if st.button("텍스트 추가", use_container_width=True):
        if user_input and user_input.strip():  # 입력된 텍스트가 있는 경우에만
            # 텍스트를 타임스탬프와 함께 저장
            add_entry_with_timestamp(user_input, "직접 입력")
            # 입력창 초기화
            st.session_state.direct_text = ""
            st.success("텍스트가 타임스탬프와 함께 추가되었습니다!")
            
    # 파일명 생성 (파일명이 아직 설정되지 않았다면)
    if not st.session_state.file_name and st.session_state.text_entries:
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.session_state.file_name = f"회의_{current_date}"
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_text_entries():
    """텍스트 항목 목록 표시"""
    if not st.session_state.text_entries:
        return
        
    st.markdown('<h3 class="subheader">입력된 텍스트 내용</h3>', unsafe_allow_html=True)
    
    # 항목 삭제 기능
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("모든 항목 삭제", use_container_width=True):
            st.session_state.text_entries = []
            st.session_state.processed_files = {}  # 처리된 파일 목록도 초기화
            st.session_state.audio_info = {}  # 오디오 정보도 초기화
            st.success("모든 텍스트 항목이 삭제되었습니다.")
            st.rerun()
    
    # 각 항목 표시
    for i, entry in enumerate(st.session_state.text_entries):
        with st.container():
            st.markdown(f'<div class="entry-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([5, 1])
            with col1:
                source_display = entry["source"]
                source_class = ""
                
                # 소스 타입에 따른 스타일링
                if "오디오 파일" in source_display:
                    source_class = "source-tag"
                elif "텍스트 파일" in source_display:
                    source_class = "source-tag"
                
                # 타임스탬프와 소스 표시
                if source_class:
                    st.markdown(f'<div class="timestamp">[{entry["timestamp"]}] <span class="{source_class}">{source_display}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="timestamp">[{entry["timestamp"]} - {source_display}]</div>', unsafe_allow_html=True)
                
                # 오디오 파일인 경우 추가 정보 표시
                if "오디오 파일" in source_display:
                    file_name = source_display.split("(")[1].split(")")[0]
                    if file_name in st.session_state.audio_info:
                        info = st.session_state.audio_info[file_name]
                        engine_name = info.get("engine", "unknown")
                        
                        # 엔진 이름을 사용자 친화적으로 표시
                        if engine_name == "clova":
                            engine_display = "네이버 클로바"
                        elif engine_name == "whisper":
                            engine_display = "OpenAI Whisper"
                        elif engine_name == "whisper (백업)":
                            engine_display = "OpenAI Whisper (백업)"
                        else:
                            engine_display = engine_name
                            
                        st.markdown(f'<div class="audio-info">파일 크기: {info["file_size"]:.2f}MB | 변환 엔진: {engine_display}</div>', unsafe_allow_html=True)
            
            with col2:
                delete_key = f"delete_{i}_{entry['timestamp'].replace(' ', '_').replace(':', '')}"
                if st.button("삭제", key=delete_key, use_container_width=True):
                    st.session_state.text_entries.pop(i)
                    st.success("항목이 삭제되었습니다.")
                    st.rerun()
            
            # 편집 가능한 텍스트 영역
            edit_key = f"entry_{i}_{entry['timestamp'].replace(' ', '_').replace(':', '')}"
            edited_text = st.text_area(
                f"항목 #{i+1}",
                value=entry["text"],
                height=100,
                key=edit_key
            )
            
            # 텍스트가 수정되었으면 업데이트
            if edited_text != entry["text"]:
                st.session_state.text_entries[i]["text"] = edited_text
            
            st.markdown('</div>', unsafe_allow_html=True)