# 방구석 낚시꾼 Mac 자동 매크로

이 폴더는 **Windows에서 Python을 직접 실행하지 않고도**
GitHub Actions의 macOS 환경을 이용해 `FishingMacro.app`을 만드는 용도입니다.

## 들어있는 파일

- `fishing_macro.py` : 실제 프로그램
- `requirements.txt` : 필요한 Python 라이브러리 목록
- `.github/workflows/build-mac.yml` : GitHub가 Mac 앱을 자동으로 만들어주는 설정

## GitHub에서 빌드하는 가장 쉬운 순서

1. GitHub에 로그인합니다.
2. 새 저장소(Repository)를 하나 만듭니다.
3. 이 ZIP의 내용물을 **폴더 구조 그대로** 업로드합니다.
   - `.github/workflows/build-mac.yml` 경로가 반드시 유지되어야 합니다.
4. 저장소 상단의 **Actions** 탭으로 갑니다.
5. 왼쪽에서 **Build macOS App**을 선택합니다.
6. **Run workflow** 버튼을 누릅니다.
7. 빌드가 끝나면 실행 기록을 클릭합니다.
8. 화면 아래 **Artifacts**에서 `FishingMacro-macOS`를 받습니다.
9. 압축을 풀면 `FishingMacro.app`이 들어 있습니다.

## Mac에서 사용할 때

1. KakaoTalk을 실행합니다.
2. 실제로 사용할 채팅방을 **직접 열어둡니다**.
3. `FishingMacro.app`을 실행합니다.
4. 처음에는 macOS가 키보드 제어 권한을 요구할 수 있습니다.
   시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용에서 허용하세요.
5. 앱에서 `낚시 시작`을 누릅니다.

기본값:
- 채팅방: 낚시방
- 멘션 봇: 방구석낚시꾼
- 명령어: 낚시
- 반복 간격: 4초

## 매우 중요

카카오톡 macOS 버전의 멘션 자동완성 동작에 따라
`@방구석낚시꾼` 입력 후 `↓` 키가 필요한지 여부가 다를 수 있습니다.

현재 프로그램은 다음 순서입니다.

`@방구석낚시꾼 입력 → ↓ → Enter → " 낚시" 입력 → Enter`

만약 Mac에서 멘션 선택이 다르게 움직이면 그 부분만 조정하면 됩니다.

## 긴급 정지

PyAutoGUI의 안전장치를 켜 두었습니다.
문제가 생기면 마우스를 화면 **왼쪽 위 모서리**로 빠르게 이동하세요.
