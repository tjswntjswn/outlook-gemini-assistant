import imaplib

# ==========================================
# 👇 여기에 정보를 입력해서 테스트해보세요!
# ==========================================
email_user = "{email_user}"
email_pass = "{email_pass}"
server_type = "gmail"  # "gmail" 또는 "outlook"
# ==========================================

def test_connection():
    try:
        # 1. 서버 설정
        if server_type == "gmail":
            imap_server = "imap.gmail.com"
        elif server_type == "outlook":
            imap_server = "outlook.office365.com"
        else:
            print("❌ 지원하지 않는 서버입니다.")
            return

        # 2. 서버 연결 시도
        print(f"📡 {server_type} 서버에 연결 중...")
        mail = imaplib.IMAP4_SSL(imap_server)
        
        # 3. 로그인 시도
        print(f"🔑 로그인 시도 중... ({email_user})")
        mail.login(email_user, email_pass)
        
        # 4. 결과
        print("\n" + "="*30)
        print("✅ 로그인 성공! 아이디/비밀번호가 정확합니다.")
        print("="*30 + "\n")
        
        mail.logout()

    except Exception as e:
        print("\n" + "="*30)
        print("❌ 로그인 실패! 다음을 확인해주세요:")
        print(f"에러 메시지: {e}")
        print("1. 이메일 주소 오타 확인")
        print("2. '앱 비밀번호'가 맞는지 확인 (일반 비번 X)")
        print("3. IMAP 설정이 켜져 있는지 확인")
        print("="*30 + "\n")

if __name__ == "__main__":
    test_connection()