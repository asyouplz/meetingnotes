# 통합 회의록 자동화 시스템

회의 내용을 효율적으로 요약하고 구조화된 회의록을 자동으로 생성하는 시스템입니다.

## 주요 기능

- **텍스트 파일 업로드**: 텍스트 파일(.txt)에서 회의 내용 가져오기
- **텍스트 직접 입력**: 회의 내용을 직접 입력하고 타임스탬프와 함께 저장
- **오디오 파일 변환**: 회의 녹음 파일(MP3, WAV 등)을 텍스트로 자동 변환
  - 네이버 클로바 STT API 지원
  - OpenAI Whisper API 지원
- **AI 회의록 생성**: Claude 또는 GPT 모델을 사용하여 구조화된 회의록 자동 생성

## 프로젝트 구조

```
meeting-minutes-system/
├── app.py                  # 메인 애플리케이션 진입점
├── requirements.txt        # 필요한 패키지 목록
├── .gitignore              # Git 무시 파일 목록
├── README.md               # 프로젝트 설명서
│
├── modules/                # 기능별 모듈 디렉토리
│   ├── __init__.py         # 패키지 초기화 파일
│   ├── upload.py           # 파일 업로드 처리 모듈
│   ├── text_conversion.py  # 오디오->텍스트 변환 모듈
│   ├── text_management.py  # 텍스트 확정 및 관리 모듈
│   ├── minutes_generator.py # 회의록 생성 모듈
│   └── utils.py            # 공통 유틸리티 함수
│
├── config/                 # 설정 파일 디렉토리
│   ├── __init__.py
│   └── settings.py         # 앱 설정 및 기본값
│
├── static/                 # 정적 자산 파일
│   └── css/
│       └── styles.css      # 스타일시트
│
└── templates/              # 잠재적인 HTML 템플릿 (향후 확장용)
    └── README.md           # 템플릿 사용 방법 설명
```

## 설치 및 실행 방법

1. 필요한 패키지 설치:
   ```
   pip install -r requirements.txt
   ```

2. API 키 설정:
   - Streamlit의 secrets 관리 기능을 사용하여 API 키 설정
   - `.streamlit/secrets.toml` 파일 생성 후 다음 내용 추가:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   CLAUDE_API_KEY = "your-claude-api-key"
   NAVER_CLIENT_ID = "your-naver-client-id"
   NAVER_CLIENT_SECRET = "your-naver-client-secret"
   ```

3. 애플리케이션 실행:
   ```
   streamlit run app.py
   ```

## 사용 방법

### TXT 파일로 회의록 생성:
1. TXT 파일을 업로드하세요 (텍스트 파일 형식)
2. 업로드된 텍스트 내용을 확인하고 필요시 수정하세요
3. '회의록 생성하기' 버튼을 클릭하세요

### 텍스트로 직접 회의록 생성:
1. '텍스트 직접 입력' 탭을 선택하세요
2. 회의 내용을 텍스트 영역에 입력하세요
3. '텍스트 추가' 버튼을 클릭하여 타임스탬프와 함께 저장하세요
4. 여러 번 텍스트를 추가할 수 있습니다
5. '회의록 생성하기' 버튼을 클릭하세요

### 오디오 파일로 회의록 생성:
1. '오디오 파일 업로드' 탭을 선택하세요
2. 사이드바에서 원하는 음성 인식 엔진을 선택하세요
3. 회의 녹음 파일을 업로드하세요 (MP3, WAV, M4A 등)
4. 파일이 자동으로 텍스트로 변환됩니다
5. 필요시 변환된 텍스트를 수정하세요
6. '회의록 생성하기' 버튼을 클릭하세요

## 의존성

- streamlit
- openai
- anthropic
- requests
- python-dotenv (개발용)

## 라이센스

이 프로젝트는 MIT 라이센스로 배포됩니다.

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 만듭니다 (`git checkout -b feature/amazing-feature`)
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 제출합니다.