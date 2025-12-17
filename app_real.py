import streamlit as st
import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import time
import json  # <--- 이 친구가 데이터를 예쁘게 바꿔줄 핵심입니다!

# ==========================================
# [설정] 페이지 설정
# ==========================================
st.set_page_config(page_title="AI Outlook Master", page_icon="📧", layout="wide")

# ==========================================
# [함수] 메일 처리 및 AI 분석
# ==========================================

def get_email_body(msg):
    """이메일 본문 텍스트 추출"""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in cdispo:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

def fetch_emails_imap(username, password, server="outlook.office365.com", limit=5):
    """IMAP을 통해 실제 이메일 가져오기"""
    email_list = []
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(username, password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        latest_email_ids = email_ids[-limit:]
        latest_email_ids.reverse()

        for e_id in latest_email_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    sender = msg.get("From")
                    body = get_email_body(msg)
                    date_str = msg.get("Date")

                    email_list.append({
                        "subject": subject,
                        "sender": sender,
                        "body": body,
                        "time": date_str,
                        "summary": None, # 분석 전에는 None
                        "analyzed": False
                    })
        mail.close()
        mail.logout()
        return email_list
    except Exception as e:
        st.error(f"메일 로그인 실패: {e}")
        return []

def analyze_email_with_gemini(api_key, email_text):
    """Gemini API로 메일 분석"""
    try:
        clean_key = api_key.strip()
        if not clean_key: return None

        genai.configure(api_key=clean_key)
        
        # 가장 안정적인 최신 모델 사용
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # 프롬프트: 반드시 JSON 포맷으로 달라고 강력하게 요청
        prompt = f"""
        You are a smart email assistant. Analyze the email below.
        Return ONLY a JSON object. Do not write "json" or use code blocks.
        
        Format:
        {{
            "summary": "Korean summary in 1 sentence",
            "category": "One of [Work, Ad, News, Security, Other]",
            "priority": "One of [High, Medium, Low]",
            "todos": ["Action item 1", "Action item 2"]
        }}

        Email Body:
        {email_text[:3000]}
        """
        
        time.sleep(1) # 에러 방지 딜레이
        response = model.generate_content(prompt)
        return response.text 
    except Exception as e:
        return str(e)

# ==========================================
# [UI] 사이드바
# ==========================================
with st.sidebar:
    st.header("🔐 로그인 설정")
    imap_server = st.selectbox("메일 서버", ["outlook.office365.com", "imap.gmail.com"])
    user_email = st.text_input("이메일 주소")
    user_pw = st.text_input("비밀번호 (앱 비밀번호)", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.write("---")
    if st.button("🔄 메일 가져오기", type="primary", use_container_width=True):
        if user_email and user_pw:
            with st.spinner("메일함 동기화 중..."):
                st.session_state.my_emails = fetch_emails_imap(user_email, user_pw, imap_server)
                st.session_state.selected_idx = None
                st.rerun()

# ==========================================
# [UI] 메인 화면
# ==========================================
if 'my_emails' not in st.session_state: st.session_state.my_emails = []
if 'selected_idx' not in st.session_state: st.session_state.selected_idx = None

col_list, col_read = st.columns([2, 3])

# [왼쪽] 메일 목록
with col_list:
    st.subheader("📥 받은 편지함")
    st.markdown("---")
    for i, mail in enumerate(st.session_state.my_emails):
        # 분석 여부에 따른 아이콘 변화
        status_icon = "✅" if mail['analyzed'] else "✉️"
        btn_text = f"{status_icon} **{mail['sender'][:15]}**... \n {mail['subject'][:25]}..."
        
        if st.button(btn_text, key=f"list_{i}", use_container_width=True):
            st.session_state.selected_idx = i
            st.rerun()

# [오른쪽] 상세 보기 및 디자인 렌더링
with col_read:
    if st.session_state.selected_idx is None:
        st.info("👈 왼쪽에서 메일을 선택해주세요.")
    else:
        idx = st.session_state.selected_idx
        mail = st.session_state.my_emails[idx]
        
        # 1. 메일 헤더
        st.markdown(f"### {mail['subject']}")
        st.caption(f"From: {mail['sender']} | Time: {mail['time']}")
        st.divider()

        # 2. 분석되지 않은 메일일 경우
        if not mail['analyzed']:
            st.info("🤖 아직 분석되지 않은 메일입니다.")
            if st.button("✨ AI 분석 시작", type="primary"):
                with st.spinner("AI가 내용을 읽고 있습니다..."):
                    raw_result = analyze_email_with_gemini(gemini_key, mail['body'])
                    st.session_state.my_emails[idx]['summary'] = raw_result
                    st.session_state.my_emails[idx]['analyzed'] = True
                    st.rerun()
        
        # 3. 분석 완료된 메일 (여기가 디자인의 핵심!)
        else:
            raw_text = mail['summary']
            
            # JSON 파싱 시도 (지저분한 텍스트를 예쁜 데이터로 변환)
            try:
                # 혹시 모를 마크다운 기호 제거
                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json) # 문자열 -> 딕셔너리 변환
                
                # (1) 뱃지 & 중요도 표시
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"📂 카테고리: **{data.get('category', '기타')}**")
                with c2:
                    prio = data.get('priority', 'Low')
                    p_color = "red" if prio == "High" else "orange" if prio == "Medium" else "green"
                    st.markdown(f"#### 중요도: :{p_color}[{prio}]")

                # (2) 요약 박스
                st.info(f"📌 **요약:** {data.get('summary', '요약 없음')}")

                # (3) 할 일 체크리스트
                todos = data.get('todos', [])
                if todos:
                    st.write("✅ **할 일 목록 (To-Do):**")
                    for todo in todos:
                        st.checkbox(todo, key=f"todo_{idx}_{todo}")
                else:
                    st.caption("발견된 할 일이 없습니다.")

            except Exception:
                # 파싱 실패 시 원본 그대로 보여주기 (비상용)
                st.warning("분석 결과 형식이 올바르지 않지만 내용은 다음과 같습니다:")
                st.code(raw_text)

            st.divider()
            with st.expander("📄 메일 원문 보기"):
                st.text(mail['body'])