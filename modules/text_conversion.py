"""
오디오->텍스트 변환 모듈 (간소화된 안정 버전)
"""
import os
import json
import tempfile
import streamlit as st
import openai
import requests
import re
from modules.utils import get_file_hash, add_entry_with_timestamp
from config.settings import ALLOWED_AUDIO_FORMATS, WHISPER_MODEL, DEFAULT_LANGUAGE

# pydub 가져오기 시도 (없어도 기본 기능 동작)
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

def setup_conversion_interface():
    """오디오 파일 업로드 및 변환 인터페이스 설정"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    st.markdown('<h3 class="subheader">오디오 파일 업로드</h3>', unsafe_allow_html=True)
    st.write("회의 녹음 파일을 업로드하면 자동으로 텍스트로 변환됩니다.")
    
    # 현재 선택된 음성 인식 엔진 표시
    engine_name = "네이버 클로바" if st.session_state.speech_to_text_engine == "clova" else "OpenAI Whisper"
    st.info(f"현재 선택된 음성 인식 엔진: {engine_name} (사이드바에서 변경 가능)")
    
    # 화자 인식 옵션
    enable_speaker_diarization = st.checkbox("화자 구분 활성화", value=True, 
                                          help="오디오에서 서로 다른 화자를 식별합니다.")
    
    if enable_speaker_diarization:
        st.session_state.enable_speaker_diarization = True
    else:
        st.session_state.enable_speaker_diarization = False
    
    # 오디오 파일 업로더
    audio_file = st.file_uploader("회의 녹음 파일을 업로드하세요", type=ALLOWED_AUDIO_FORMATS, key="audio_uploader")
    
    if audio_file:
        process_audio_file(audio_file, engine_name)
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_audio_file(audio_file, engine_name):
    """
    업로드된 오디오 파일 처리
    
    Parameters:
    audio_file: Streamlit 업로드된 파일 객체
    engine_name: 표시용 엔진 이름
    """
    # 파일 해시 계산 (중복 처리 방지)
    audio_content = audio_file.getvalue()
    audio_hash = get_file_hash(audio_content)
    
    # 이미 처리한 파일인지 확인
    if audio_hash in st.session_state.processed_files:
        processed_name = st.session_state.processed_files[audio_hash]
        # 중복 파일이지만 이름이 다른 경우 특별히 알림
        if processed_name != audio_file.name:
            st.warning(f"중복 파일이 감지되었습니다! 이 파일의 내용은 이전에 처리된 '{processed_name}' 파일과 동일합니다.")
        else:
            st.info(f"이 파일은 이미 처리되었습니다: {audio_file.name}")
        
        # 중복 파일 처리 방법 선택 옵션 제공
        if st.button("그래도 이 파일을 다시 처리하기", key="force_process"):
            # 해시 목록에서 제거하여 재처리 허용
            st.session_state.processed_files.pop(audio_hash, None)
            st.rerun()
        return
    
    # 새 파일 처리 로직
    st.session_state.file_name = audio_file.name
    
    with st.spinner(f"{engine_name}로 오디오 파일을 텍스트로 변환 중..."):
        # 오디오 처리 진행
        transcript_text = convert_audio_to_text(audio_file)
        
        if transcript_text:
            # 변환된 텍스트를 타임스탬프와 함께 저장
            add_entry_with_timestamp(transcript_text, f"오디오 파일 ({audio_file.name})")
            # 처리된 파일 해시값 저장 (중복 방지)
            st.session_state.processed_files[audio_hash] = audio_file.name
            
            # 사용된 엔진에 따라 다른 메시지 표시
            used_engine = st.session_state.audio_info[audio_file.name].get("engine", "unknown")
            
            if "(백업)" in used_engine:
                st.warning(f"기본 엔진에 오류가 발생하여 백업 엔진으로 변환되었습니다: {audio_file.name}")
            else:
                st.success(f"오디오 파일이 {engine_name}로 텍스트로 변환되었습니다: {audio_file.name}")
        else:
            st.error("텍스트 변환에 실패했습니다. 파일을 확인하고 다시 시도해주세요.")
        
        st.session_state.input_method = 'audio'

def convert_audio_to_text(audio_file):
    """
    오디오 파일을 텍스트로 변환
    
    Parameters:
    audio_file: Streamlit 업로드된 파일 객체
    
    Returns:
    str: 변환된 텍스트 또는 None (실패 시)
    """
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_path = tmp_file.name
        
        # 파일 정보 저장
        file_info = {
            "original_name": audio_file.name,
            "file_size": len(audio_file.getvalue()) / (1024 * 1024),  # MB 단위
            "temp_path": tmp_path,
            "engine": st.session_state.speech_to_text_engine  # 사용된 엔진 저장
        }
        
        transcript_text = ""
        
        # 선택된 음성 인식 엔진에 따라 처리
        if st.session_state.speech_to_text_engine == "whisper":
            st.info("OpenAI Whisper로 텍스트 변환 중...")
            transcript_text = convert_with_whisper(tmp_path)
            if transcript_text:
                st.success("Whisper 변환 완료!")
                
        elif st.session_state.speech_to_text_engine == "clova":
            try:
                st.info("네이버 클로바로 텍스트 변환 중...")
                # 클로바 API 키 확인
                if not hasattr(st.session_state, 'naver_client_secret') or not st.session_state.naver_client_secret:
                    raise Exception("네이버 클로바 API 키가 설정되지 않았습니다.")
                
                transcript_text = convert_with_clova(tmp_path)
                if transcript_text:
                    st.success("클로바 변환 완료!")
                    
            except Exception as clova_error:
                st.error(f"Clova API 오류: {str(clova_error)}")
                # 오류 발생 시 Whisper로 백업
                st.warning("Clova API 오류 발생, Whisper로 대체합니다...")
                try:
                    transcript_text = convert_with_whisper(tmp_path)
                    if transcript_text:
                        st.success("Whisper 변환 성공! (백업 사용)")
                    else:
                        st.error("Whisper 변환 실패: 텍스트를 추출할 수 없습니다")
                    file_info["engine"] = "whisper (백업)"
                except Exception as whisper_error:
                    st.error(f"Whisper API 오류: {str(whisper_error)}")
                    # 임시 파일 삭제
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    return None
        
        # 임시 파일 삭제
        try:
            os.unlink(tmp_path)
        except Exception as e:
            st.warning(f"임시 파일 삭제 실패: {str(e)}")
        
        # 결과값 저장
        file_info["duration"] = "자동 감지"  # 실제로는 API 응답에서 추출할 수 있음
        file_info["transcript"] = transcript_text
        
        st.session_state.audio_info[audio_file.name] = file_info
        return transcript_text
        
    except Exception as e:
        st.error(f"오디오 파일 처리 중 오류가 발생했습니다: {str(e)}")
        return None

def convert_with_whisper(file_path):
    """OpenAI Whisper API로 변환 - 화자 구분 가능"""
    try:
        # 화자 인식 활성화 여부 확인
        enable_diarization = st.session_state.get('enable_speaker_diarization', False)
        
        # 기본 옵션
        options = {
            "model": WHISPER_MODEL,
            "language": DEFAULT_LANGUAGE
        }
        
        # 화자 구분 옵션 추가 (Whisper는 현재 공식적으로 화자 구분 지원 X)
        # 변환 후 포스트 프로세싱에서 화자 구분 추정
        with open(file_path, "rb") as audio:
            transcript = openai.audio.transcriptions.create(
                file=audio,
                **options
            )
        
        # 화자 구분 활성화된 경우 임의로 화자 구분 형식으로 변환
        if enable_diarization:
            return estimate_speakers_from_whisper(transcript.text)
        else:
            return transcript.text
            
    except Exception as e:
        raise Exception(f"Whisper API 오류: {str(e)}")

def convert_with_clova(file_path):
    """네이버 클로바 API로 변환 - 화자 구분 지원"""
    try:
        # API 호출 준비 - Invoke URL 및 Secret Key 사용
        invoke_url = "https://clovaspeech-gw.ncloud.com/external/v1/10576/25e1436c8b6a648441382ef258197ba987660c32a80bc65b319acad99556b0e9"
        secret_key = st.session_state.naver_client_secret
        
        # 화자 인식 활성화 여부 확인
        enable_diarization = st.session_state.get('enable_speaker_diarization', False)
        
        # 요청 본문 설정
        request_body = {
            'language': 'ko-KR',
            'completion': 'sync',
            'wordAlignment': True,
            'fullText': True,
            'diarization': {
                'enable': enable_diarization,  # 화자 구분 활성화 여부
                'speakerCount': 0  # 0: 자동감지, 2~10: 화자 수 지정
            }
        }
        
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': secret_key
        }
        
        # 파일 읽기 및 API 요청 (파일 업로드 방식)
        with open(file_path, 'rb') as audio_file:
            files = {
                'media': audio_file,
                'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
            }
            
            response = requests.post(
                headers=headers, 
                url=invoke_url + '/recognizer/upload', 
                files=files
            )
        
        # 응답 처리
        if response.status_code == 200:
            result = response.json()
            
            # 화자 구분 활성화 시 포맷팅
            if enable_diarization and 'segments' in result and len(result['segments']) > 0:
                return format_clova_speaker_segments(result['segments'])
            # 일반 텍스트 변환
            elif 'text' in result:
                return result.get("text", "")
            elif 'segments' in result and len(result['segments']) > 0:
                segments = result.get("segments", [])
                full_text = " ".join([segment.get("text", "") for segment in segments if "text" in segment])
                return full_text
            else:
                raise Exception("API 응답에서 텍스트를 찾을 수 없습니다")
        else:
            raise Exception(f"API 응답 오류 ({response.status_code}): {response.text}")
            
    except Exception as e:
        raise Exception(f"Clova API 오류: {str(e)}")

def format_clova_speaker_segments(segments):
    """클로바 API의 화자 세그먼트를 화자-시간 형식으로 변환"""
    formatted_text = ""
    for segment in segments:
        if 'text' in segment:
            speaker = segment.get('speaker', {}).get('label', '알 수 없음')
            start_time = format_time_to_mm_ss(segment.get('start', 0))
            text = segment.get('text', '')
            
            formatted_text += f"{speaker} {start_time}\n{text}\n"
    
    return formatted_text

def estimate_speakers_from_whisper(text):
    """Whisper 결과에서 화자 구분 추정 (문장 및 구두점 기반)"""
    # 문장 단위로 분리 (마침표, 느낌표, 물음표 뒤 공백으로 분리)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    formatted_text = ""
    current_time = 0
    speakers = ["참석자 A", "참석자 B"]  # 기본 화자 이름
    
    # 대화 패턴 추정을 위한 간단한 규칙
    current_speaker_idx = 0  # 초기 화자
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue
            
        # 매우 기본적인 화자 전환 추정 로직
        # 질문 이후 화자 전환
        if i > 0 and sentences[i-1].strip().endswith('?'):
            current_speaker_idx = 1 - current_speaker_idx  # 화자 전환
            
        # 매우 짧은 응답은 화자 전환 가능성 높음
        elif i > 0 and len(sentence.strip().split()) <= 3 and len(sentences[i-1].strip().split()) > 5:
            current_speaker_idx = 1 - current_speaker_idx  # 화자 전환
            
        # 화자 결정
        speaker = speakers[current_speaker_idx]
        
        # 문장 길이에 비례하여 시간 추정
        words_count = len(sentence.split())
        time_per_word = 0.5  # 단어 당 약 0.5초로 가정
        sentence_duration = max(1.0, words_count * time_per_word)  # 최소 1초
        
        current_time += sentence_duration
        time_str = format_time_to_mm_ss(current_time)
        
        formatted_text += f"{speaker} {time_str}\n{sentence}\n"
    
    return formatted_text

def format_time_to_mm_ss(seconds):
    """초를 MM:SS 형식으로 변환"""
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
