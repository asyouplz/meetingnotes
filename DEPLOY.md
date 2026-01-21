# fly.io 배포 가이드

## 사전 준비

1. [flyctl CLI 설치](https://fly.io/docs/hands-on/install-flyctl/)
2. fly.io 계정 생성 및 로그인
   ```
   flyctl auth login
   ```

## 배포 단계

1. 프로젝트 디렉토리에서 다음 명령어로 앱 시작하기
   ```
   flyctl launch
   ```
   - 이미 fly.toml이 존재하므로 기존 설정을 사용할지 물어보면 'y'를 입력하세요.
   - 새 앱 이름을 입력하거나 기본값을 사용하세요.
   - 리전 선택 시 nrt(도쿄)나 다른 가까운 리전을 선택하세요.
   - PostgreSQL이나 다른 DB 생성 요청은 'n'으로 대답하세요.

2. 환경 변수(API 키) 설정
   ```
   flyctl secrets set OPENAI_API_KEY="your-openai-api-key"
   flyctl secrets set CLAUDE_API_KEY="your-claude-api-key"
   flyctl secrets set NAVER_CLIENT_SECRET="your-naver-client-secret"
   flyctl secrets set NAVER_CLIENT_ID="your-naver-client-id"
   ```

3. 앱 배포
   ```
   flyctl deploy
   ```

## 참고 사항

- 포트: 애플리케이션은 fly.io 표준 포트인 8080에서 실행되도록 설정되어 있습니다.

## 볼륨 설정 (선택사항)

앱에서 영구 저장소가 필요한 경우:
```
flyctl volumes create meetingnotes_data --size 1 --region nrt
```

## 앱 확인 및 모니터링

1. 앱 상태 확인
   ```
   flyctl status
   ```

2. 로그 확인
   ```
   flyctl logs
   ```

3. 브라우저에서 앱 열기
   ```
   flyctl open
   ```

## 문제 해결

- 오류가 발생하면 `flyctl logs`로 로그를 확인하세요.
- 리소스 부족 문제: `flyctl scale memory 1024`로 메모리 크기를 조정할 수 있습니다.
- 앱이 시작되지 않는 경우: `flyctl doctor`로 진단할 수 있습니다. 