import streamlit as st          
import imaplib                  
import email                    
from email.header import decode_header 
import google.generativeai as genai 
import time
import json

# ==========================================
# [설정] 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="Brief Mail 📝", 
    page_icon="img/favicon/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 [디자인] 최종 완성 (Popcorn + Green + User Fix)
# ==========================================
st.markdown("""
    <style>
    /* 1. 폰트 정의 (다이어리체) */
    @font-face {
        font-family: 'EarlyFontDiary';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_220508@1.0/EarlyFontDiary.woff2') format('woff2');
        font-weight: normal;
        font-style: normal;
    }
    
    /* 2. 전체 요소 폰트 및 텍스트 색상 적용 */
    html, body, [class*="css"], select, textarea, input, p, h1, h2, h3, div, span, label {
        font-family: 'EarlyFontDiary', cursive;
        color: #5D4037 !important; 
    }

    /* 아이콘 폰트 깨짐 방지 (Streamlit 내부 아이콘) */
    button[kind="header"] span, 
    [data-testid="stSidebarCollapsedControl"] span,
    [data-testid="stSidebarExpandedControl"] span,
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', sans-serif !important;
        font-weight: normal !important;
    }

    /* 3. 앱 배경 */
    .stApp {
        background-color: #F1F8E9 !important; 
        background-image: radial-gradient(#C9D99E 2px, transparent 2px); 
        background-size: 30px 30px;
    }

    /* 4. 사이드바 디자인 */
    section[data-testid="stSidebar"] {
        background-color: #F8E287 !important; 
        border-right: 5px solid #FFFFFF;
        box-shadow: 5px 0 15px rgba(0,0,0,0.05);
    }
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* ==============================================================
       ✅ [사용자 FIX] 사이드바 열기/닫기 버튼 완벽 고정 및 위치 이동
       ============================================================== */

    /* 1) 닫기/열기 토글 버튼 강제 노출 (hover 여부 상관없이) */
    :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarExpandButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"],
        button[title*="sidebar"],
        button[kind="header"]
    ) {
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        pointer-events: auto !important;
    }

    /* 2) 버튼 내부 아이콘(svg/span) 강제 노출 */
    :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarExpandButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"],
        button[title*="sidebar"],
        button[kind="header"]
    ) svg,
    :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarExpandButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"],
        button[title*="sidebar"],
        button[kind="header"]
    ) span {
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        fill: #5D4037 !important; /* 아이콘 색상 초코색 */
        color: #5D4037 !important;
    }

    /* 3) Streamlit의 hover 시에만 보이게 하는 규칙 역으로 무력화 */
    section[data-testid="stSidebar"]:hover :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[aria-label="Close sidebar"],
        button[kind="header"]
    ),
    section[data-testid="stSidebar"] :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapseButton"],
        button[aria-label="Close sidebar"],
        button[kind="header"]
    ) {
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* 4) 버튼 위치 "오른쪽 상단" 고정 및 스타일링 */
    :is(
        [data-testid="stSidebarExpandedControl"],
        [data-testid="stSidebarCollapsedControl"],
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"]
    ) {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important; /* 오른쪽 고정 */
        left: unset !important; /* 왼쪽 설정 해제 */
        z-index: 9999999 !important;

        width: 45px !important;
        height: 45px !important;
        border-radius: 50% !important;
        background: #FFFFFF !important;
        border: 2px solid #C9D99E !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1) !important;
        color: #5D4037 !important;
    }

    /* ------------------------------------------------------- */
    /* [기타 UI] 입력창, 버튼, 컨테이너 등 */
    /* ------------------------------------------------------- */
    
    /* 마우스 커서 포인터 처리 */
    div[data-baseweb="select"], div[data-baseweb="select"] * { cursor: pointer !important; }

    /* 입력창 스타일 */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important; 
        border: 3px solid #C9D99E !important; 
        border-radius: 20px !important;
        box-shadow: 2px 2px 0px #AED581 !important;
    }
    input[type="text"], input[type="password"] {
        background-color: #FFFFFF !important; 
        color: #5D4037 !important; 
        font-family: 'EarlyFontDiary', cursive !important;
    }
    div[data-baseweb="input"] button { background-color: #FFFFFF !important; border: none !important; }
    div[data-baseweb="input"] svg { fill: #5D4037 !important; }

    /* 셀렉트 박스 */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 3px solid #C9D99E !important;
        border-radius: 20px !important;
        box-shadow: 2px 2px 0px #AED581 !important;
        color: #5D4037 !important;
        font-family: 'EarlyFontDiary', cursive !important;
    }

    /* 메인 컨테이너 */
    .block-container {
        background-color: #FFFFFF; 
        border-radius: 30px; 
        border: 4px solid #C9D99E; 
        box-shadow: 8px 8px 0px #AED581; 
        padding: 40px !important;
        margin-top: 20px;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #F8E287 !important;
        color: #5D4037 !important;
        border: 3px solid #F0D566 !important;
        border-radius: 25px !important;
        font-size: 20px !important;
        padding: 10px 20px !important;
        box-shadow: 0px 5px 0px #C9D99E !important;
        transition: all 0.2s;
        font-family: 'EarlyFontDiary', cursive !important;
    }
    .stButton > button:hover {
        background-color: #FFEB99 !important;
        transform: translateY(-2px);
    }
    .stButton > button[kind="primary"] {
        background-color: #AED581 !important;
        border-color: #9CCC65 !important;
        box-shadow: 0px 5px 0px #8BC34A !important;
        color: #FFFFFF !important;
    }

    /* 리스트 박스 */
    .mail-card, .detail-box, .summary-box {
        background-color: #FFFFFF;
        border-radius: 20px;
        border: 3px dashed #F8E287;
        padding: 25px;
        box-shadow: 4px 4px 0px #F1F8E9;
        margin-bottom: 20px;
        color: #5D4037 !important;
    }
    .summary-box {
        background-color: #F1F8E9;
        border: 3px solid #C9D99E;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [함수] 백엔드 로직
# ==========================================
def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in cdispo:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

def fetch_emails_imap(username, password, server, limit=15):
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
                    date_str = msg.get("Date")
                    body = get_email_body(msg)
                    email_list.append({
                        "subject": subject, "sender": sender, "body": body,
                        "time": date_str, "summary": None, "analyzed": False
                    })
        mail.close()
        mail.logout()
        return email_list
    except Exception as e:
        st.error(f"로그인 실패: {e}")
        return None

def analyze_email_with_gemini(api_key, email_text):
    try:
        genai.configure(api_key=api_key.strip())
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Analyze the email below. Return ONLY a valid JSON object.
        JSON Format:
        {{
            "summary": "한국어로 핵심 내용만 명확하고 깔끔하게 1-2문장 요약 (다나까 말투 지양, 친절한 해요체)",
            "category": "업무, 광고, 뉴스, 보안, 기타",
            "priority": "높음, 보통, 낮음",
            "todos": ["할 일 1", "할 일 2"]
        }}
        Email Body:
        {email_text[:3000]} 
        """
        response = model.generate_content(prompt)
        return response.text 
    except Exception as e:
        return str(e)

def parse_json_result(text):
    try:
        if not text: return None
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except: return None

# ==========================================
# [상태 관리]
# ==========================================
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'my_emails' not in st.session_state: st.session_state.my_emails = []
if 'selected_mail' not in st.session_state: st.session_state.selected_mail = None

# ==========================================
# [UI] 사이드바
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>📝 Brief Mail</h2>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.write("메일을 요약해드려요! 🌿")
        server = st.selectbox("메일 서버", ["outlook.office365.com", "imap.gmail.com"])
        u_email = st.text_input("아이디 (Email)")
        u_pw = st.text_input("비밀번호 (App Pw)", type="password")
        g_key = st.text_input("Gemini API Key", type="password")
        
        st.write("")
        if st.button("로그인", type="primary", use_container_width=True):
            if u_email and u_pw and g_key:
                with st.spinner("접속 중... ✨"):
                    emails = fetch_emails_imap(u_email, u_pw, server)
                    if emails is not None:
                        st.session_state.is_logged_in = True
                        st.session_state.user_info = {"email": u_email, "pw": u_pw, "server": server, "key": g_key}
                        st.session_state.my_emails = emails
                        st.rerun()
    else:
        st.markdown(f"""
            <div style="text-align:center; padding:20px; background:white; border-radius:20px; border:3px dashed #C9D99E;">
                <div style="font-size:50px;">👩🏻‍💻</div>
                <h3>{st.session_state.user_info['email'].split('@')[0]}님</h3>
                <p>오늘의 요약 도착!</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메일 검색", placeholder="제목, 보낸 사람...")
        category_filter = st.radio("카테고리", ["전체", "업무", "광고"], horizontal=True)
        
        st.write("---")
        c1, c2 = st.columns(2)
        if c1.button("새로고침"):
            info = st.session_state.user_info
            emails = fetch_emails_imap(info['email'], info['pw'], info['server'])
            if emails: st.session_state.my_emails = emails
            st.rerun()
        if c2.button("로그아웃"):
            st.session_state.clear()
            st.rerun()

# ==========================================
# [UI] 메인 화면
# ==========================================

if not st.session_state.is_logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
            <div class="mail-card" style="text-align:center; padding: 50px; border: 5px solid #F8E287;">
                <div style="font-size: 80px;">📝✨</div>
                <h1 style="font-size: 40px; margin-top:20px;">Brief Mail</h1>
                <p style="font-size: 20px; margin-top: 20px;">
                    AI가 당신의 메일함을<br>
                    간결하게 요약해드립니다.<br><br>
                    👈 왼쪽에서 로그인을 해주세요.
                </p>
            </div>
        """, unsafe_allow_html=True)

else:
    filtered_emails = st.session_state.my_emails
    if search_query:
        q = search_query.lower()
        filtered_emails = [e for e in filtered_emails if q in e['subject'].lower() or q in e['sender'].lower()]
    
    col1, col2 = st.columns([1.5, 2.5])
    
    with col1:
        st.markdown(f"### 📬 편지함 ({len(filtered_emails)})")
        for i, mail in enumerate(filtered_emails):
            status = "💛" if mail['analyzed'] else "✉️"
            subj = mail['subject'][:20] + "..." if len(mail['subject']) > 20 else mail['subject']
            btn_text = f"{status} {subj}\n{mail['sender'].split('<')[0]}"
            
            if st.button(btn_text, key=f"mail_{i}", use_container_width=True):
                st.session_state.selected_mail = mail
                
    with col2:
        if st.session_state.selected_mail:
            m = st.session_state.selected_mail
            st.markdown(f"""
                <div class="detail-box">
                    <h2>{m['subject']}</h2>
                    <p>📤 <b>From:</b> {m['sender']}</p>
                    <p style="color:#777;">🕒 {m['time']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if not m['analyzed']:
                st.info("아직 읽지 않은 메일이에요! 🌿")
                if st.button("✨ AI 요약하기", type="primary"):
                    with st.spinner("핵심 내용 파악 중... 🧠"):
                        res = analyze_email_with_gemini(st.session_state.user_info['key'], m['body'])
                        m['summary'] = res
                        m['analyzed'] = True
                        st.rerun()
            else:
                data = parse_json_result(m['summary'])
                if data:
                    st.markdown(f"""
                        <div class="summary-box">
                            <h3 style="background:none;">📝 Brief Note</h3>
                            <p style="font-size:1.2em;">{data.get('summary', '')}</p>
                            <div style="margin-top:15px;">
                                <span style="background:#FFF9C4; padding:5px 10px; border-radius:15px; border:1px solid #FBC02D;">🏷️ {data.get('category', '기타')}</span>
                                <span style="background:#DCEDC8; padding:5px 10px; border-radius:15px; border:1px solid #AED581;">🔥 중요도: {data.get('priority', '보통')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            with st.expander("📜 원문 보기"):
                st.text(m['body'])
        else:
            st.markdown("""
                <div class="mail-card" style="text-align:center; padding: 100px 20px;">
                    <div style="font-size:60px;">🌱</div>
                    <h3>왼쪽에서 메일을 선택해주세요!</h3>
                </div>
            """, unsafe_allow_html=True)