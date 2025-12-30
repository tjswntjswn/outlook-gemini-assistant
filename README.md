📬 Brief Mail (브리프 메일)
Gemini AI 기반 이메일 자동 요약 및 분류 서비스

바쁜 일상 속에서 쏟아지는 이메일을 일일이 읽기 힘드신가요? Brief Mail은 구글의 최신 AI인 Gemini를 사용하여 받은 편지함의 메일들을 분석하고, 핵심 내용 요약 및 중요도 분류를 통해 효율적인 메일 관리를 도와줍니다.

✨ 주요 기능 (Key Features)
AI 자동 요약: 메일 본문의 핵심 내용을 1~2문장으로 요약하여 빠르게 파악할 수 있습니다.

스마트 우선순위 설정: 메일의 긴급도와 중요도를 분석하여 High, Medium, Low로 분류합니다.

카테고리 자동 분류: 업무, 뉴스레터, 재무, 소셜 등 메일의 성격을 자동으로 파악하여 태그를 달아줍니다.

실시간 이메일 연동: Gmail, Outlook 등 주요 IMAP 서버와 실시간으로 연동되어 최신 메일을 가져옵니다.

🛠 기술 스택 (Tech Stack)
Backend: Python, Flask

AI Engine: Google Gemini API (gemini-flash-latest)

Email Protocol: IMAP (imaplib)

Frontend: HTML5, CSS3 (Responsive Design)

🚀 시작하기 (Getting Started)
1. 환경 설정
본 프로젝트를 실행하려면 Python 3.x 환경이 필요합니다. 필수 라이브러리를 설치해 주세요.

Bash

pip install flask google-generativeai
2. API 키 발급
이 서비스는 Google Gemini API를 사용합니다. Google AI Studio에서 API 키를 발급받아야 합니다.

참고: API 사용을 위해 Google Cloud 프로젝트에 결제 계정 연결이 필요할 수 있습니다.

3. 서버 실행
Bash

python app.py
서버 실행 후 브라우저에서 http://localhost:5001에 접속하여 로그인해 주세요.

📝 사용 방법 (Usage)
로그인: 이메일 주소와 앱 비밀번호(Gmail의 경우 2단계 인증 필수)를 입력합니다.

API 키 입력: 발급받은 Gemini API 키를 입력합니다.

대시보드 확인: AI가 분석한 메일 요약 목록을 확인하고 시간을 절약하세요!

💡 주의 사항
Gmail 사용자의 경우, 계정 설정에서 IMAP 사용이 활성화되어 있어야 하며, 일반 비밀번호가 아닌 **'앱 비밀번호'**를 생성해서 사용해야 보안 오류 없이 로그인이 가능합니다.

앞으로의 계획: 대기 중인 AI 요약 기능이 활성화되면, 진짜 메일 제목과 본문을 가져와서 요약하는 기능을 완성할 예정입니다! 🚀