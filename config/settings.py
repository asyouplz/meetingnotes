"""
애플리케이션 설정 모듈
"""

# 앱 기본 설정
APP_TITLE = "통합 회의록 자동화 시스템"
APP_ICON = "📝"
SIDEBAR_STATE = "expanded"  # 'expanded' 또는 'collapsed'
APP_VERSION = "1.0.0"

# API 기본 설정
DEFAULT_SPEECH_TO_TEXT_ENGINE = "clova"  # 'clova' 또는 'whisper'
DEFAULT_SUMMARY_MODEL = "claude"         # 'claude' 또는 'openai'

# 클로드 모델 설정
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"
CLAUDE_MAX_TOKENS = 5000
CLAUDE_TEMPERATURE = 0.3

# OpenAI 모델 설정
OPENAI_MODEL = "o3-mini"
OPENAI_MAX_TOKENS = 5000
OPENAI_TEMPERATURE = 0.3

# 오디오 파일 설정
ALLOWED_AUDIO_FORMATS = ["mp3", "wav", "m4a", "ogg"]
WHISPER_MODEL = "whisper-1"
DEFAULT_LANGUAGE = "ko"

# 시스템 프롬프트
MINUTES_SYSTEM_PROMPT = """당신은 회의 내용을 구조화된 회의록으로 요약하는 전문가입니다. 
기본 포맷은 다음과 같습니다: 
1) 회의 개요, 
2) 주요 논의사항, 
3) 결정사항, 
4) 행동계획(담당자와 마감일). 

참석자 명단, 시간 등 중요 정보를 포함하고, 핵심을 명확하고 객관적으로 요약해 주세요."""
