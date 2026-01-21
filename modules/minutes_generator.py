"""
회의록 생성 모듈
"""
import os
import time
import streamlit as st
import openai
import anthropic
from datetime import datetime
from modules.utils import update_full_transcript
from config.settings import (
    CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE,
    OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    MINUTES_SYSTEM_PROMPT
)

def setup_minutes_interface():
    """회의록 생성 인터페이스 설정"""
    st.markdown('<h3 class="subheader">회의록 생성</h3>', unsafe_allow_html=True)
    
    # 선택된 모델 표시
    model_name = "Anthropic Claude" if st.session_state.summary_model == "claude" else "OpenAI GPT"
    st.info(f"현재 선택된 회의록 요약 모델: {model_name} (사이드바에서 변경 가능)")
    
    if st.button("회의록 생성하기", use_container_width=True, key="generate_minutes"):
        generate_minutes()
    
    # 결과 표시 및 다운로드
    if st.session_state.processing_complete and st.session_state.summary:
        display_minutes_results()

def generate_minutes():
    """회의록 생성 처리"""
    try:
        with st.spinner("회의록을 생성 중..."):
            # 진행 상태 표시
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            # 전체 텍스트 생성
            full_transcript = update_full_transcript()
            
            progress_text.text("AI 모델 초기화 중...")
            progress_bar.progress(10)
            
            # API 클라이언트 초기화
            # 각 API 클라이언트를 미리 초기화하여 오류 발생 시에도 사용할 수 있도록 함
            claude_client = None
            try:
                claude_client = anthropic.Anthropic(
                    api_key=st.session_state.claude_api_key,
                )
            except Exception as e:
                st.warning(f"Claude API 클라이언트 초기화 오류: {str(e)}")
            
            progress_text.text("AI 모델 호출 중...")
            progress_bar.progress(30)
            
            # 선택된 모델에 따라 다른 API 호출
            if st.session_state.summary_model == "claude":
                progress_text.text("Claude API로 회의록 생성 중...")
                try:
                    # Claude가 기본적으로 선택된 경우
                    if claude_client is None:
                        raise Exception("Claude API 클라이언트가 초기화되지 않았습니다.")
                        
                    # Claude API 호출
                    message = claude_client.messages.create(
                        model=CLAUDE_MODEL,
                        max_tokens=CLAUDE_MAX_TOKENS,
                        temperature=CLAUDE_TEMPERATURE,
                        system=MINUTES_SYSTEM_PROMPT,
                        messages=[
                            {
                                "role": "user",
                                "content": f"다음 회의 내용을 요약해주세요: {full_transcript}"
                            }
                        ]
                    )
                    
                    progress_bar.progress(70)
                    progress_text.text("회의록 생성 완료...")
                    
                    st.session_state.summary = message.content[0].text
                    st.success("Claude로 회의록이 생성되었습니다!")
                    
                except Exception as claude_error:
                    st.error(f"Claude API 연결 오류: {str(claude_error)}")
                    st.info("인터넷 연결을 확인하거나 나중에 다시 시도해보세요.")
                    st.code(str(claude_error))
                    
                    # 오류 발생 시 OpenAI로 대체 시도
                    st.info("Claude API 오류 발생, OpenAI GPT로 대체합니다...")
                    
                    try:
                        response = openai.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": MINUTES_SYSTEM_PROMPT},
                                {"role": "user", "content": f"다음 회의 내용을 요약해주세요: {full_transcript}"}
                            ],
                            max_completion_tokens=OPENAI_MAX_TOKENS
                        )
                        
                        st.session_state.summary = response.choices[0].message.content
                        st.success("OpenAI GPT로 회의록이 생성되었습니다! (백업)")
                    except Exception as openai_error:
                        st.error(f"OpenAI API 오류: {str(openai_error)}")
                        st.code(str(openai_error))
                        progress_bar.empty()
                        progress_text.empty()
                        st.stop()  # 처리 중단
            
            elif st.session_state.summary_model == "openai":
                progress_text.text("OpenAI API로 회의록 생성 중...")
                try:
                    # OpenAI API 호출
                    response = openai.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[
                            {"role": "system", "content": MINUTES_SYSTEM_PROMPT},
                            {"role": "user", "content": f"다음 회의 내용을 요약해주세요: {full_transcript}"}
                        ],
                        max_completion_tokens=OPENAI_MAX_TOKENS
                    )
                    
                    progress_bar.progress(70)
                    progress_text.text("회의록 생성 완료...")
                    
                    st.session_state.summary = response.choices[0].message.content
                    st.success("OpenAI GPT로 회의록이 생성되었습니다!")
                    
                except Exception as openai_error:
                    st.error(f"OpenAI API 오류: {str(openai_error)}")
                    st.info("인터넷 연결을 확인하거나 나중에 다시 시도해보세요.")
                    st.code(str(openai_error))
                    
                    # 오류 발생 시 Claude로 대체 시도
                    st.info("OpenAI API 오류 발생, Claude로 대체합니다...")
                    
                    try:
                        # Claude 클라이언트가 초기화되지 않았으면 다시 초기화
                        if claude_client is None:
                            claude_client = anthropic.Anthropic(
                                api_key=st.session_state.claude_api_key,
                            )
                            
                        # Claude API 호출
                        message = claude_client.messages.create(
                            model=CLAUDE_MODEL,
                            max_tokens=CLAUDE_MAX_TOKENS,
                            temperature=CLAUDE_TEMPERATURE,
                            system=MINUTES_SYSTEM_PROMPT,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"다음 회의 내용을 요약해주세요: {full_transcript}"
                                }
                            ]
                        )
                        
                        st.session_state.summary = message.content[0].text
                        st.success("Claude로 회의록이 생성되었습니다! (백업)")
                    except Exception as claude_error:
                        st.error(f"Claude API 오류: {str(claude_error)}")
                        st.code(str(claude_error))
                        progress_bar.empty()
                        progress_text.empty()
                        st.stop()  # 처리 중단
            
            # 결과 파일 저장 (요약이 생성된 경우에만)
            if st.session_state.summary:
                save_minutes_to_file(full_transcript)
                
                progress_bar.progress(100)
                progress_text.text("완료!")
                time.sleep(0.5)
                progress_text.empty()
                progress_bar.empty()
            
                st.success("회의록 생성이 완료되었습니다!")
    
    except Exception as e:
        st.error(f"알 수 없는 오류가 발생했습니다: {str(e)}")
        st.code(str(e))

def save_minutes_to_file(full_transcript):
    """생성된 회의록을 파일로 저장"""
    base_name = os.path.splitext(st.session_state.file_name)[0] if st.session_state.file_name else "회의"
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file_name = f"{base_name}_회의록_{current_date}.md"
    
    try:
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(f"# 회의록: {base_name} ({current_date})\n\n")
            f.write(st.session_state.summary)
            f.write("\n\n## 전체 회의 내용\n\n")
            f.write(full_transcript)
        
        st.session_state.output_file = output_file_name
        st.session_state.processing_complete = True
    except Exception as file_error:
        st.error(f"파일 저장 중 오류 발생: {str(file_error)}")
        st.session_state.output_file = None
        st.session_state.processing_complete = True

def display_minutes_results():
    """회의록 결과 표시 및 다운로드 옵션 제공"""
    st.markdown('<h3 class="subheader">결과 확인 및 다운로드</h3>', unsafe_allow_html=True)
    
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(st.session_state.summary)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 다운로드 버튼 (파일이 성공적으로 저장된 경우에만)
    if hasattr(st.session_state, 'output_file') and st.session_state.output_file:
        try:
            with open(st.session_state.output_file, "r", encoding="utf-8") as file:
                st.download_button(
                    label="회의록 다운로드",
                    data=file,
                    file_name=st.session_state.output_file,
                    mime="text/markdown",
                    use_container_width=True
                )
        except Exception as download_error:
            st.error(f"파일 다운로드 준비 중 오류: {str(download_error)}")
            
            # 대체 다운로드 방법
            full_transcript = update_full_transcript()
            markdown_content = f"# 회의록: {os.path.splitext(st.session_state.file_name)[0]} ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            markdown_content += st.session_state.summary
            markdown_content += "\n\n## 전체 회의 내용\n\n"
            markdown_content += full_transcript
            
            st.download_button(
                label="회의록 다운로드 (대체 방식)",
                data=markdown_content,
                file_name=f"회의록_{datetime.now().strftime('%Y-%m-%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    # 결과 리셋 버튼
    if st.button("새로운 회의록 만들기", use_container_width=True, key="reset_button"):
        st.session_state.summary = None
        st.session_state.processing_complete = False
        st.rerun()
