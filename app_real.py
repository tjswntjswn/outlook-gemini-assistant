import streamlit as st          # 웹 UI 프레임워크 (화면 구성용)
import imaplib                  # IMAP 프로토콜 사용 (메일 서버 통신용)
import email                    # 이메일 MIME 파싱 라이브러리
from email.header import decode_header # 이메일 제목 인코딩(UTF-8 등) 해독
import google.generativeai as genai # Google Gemini AI API 라이브러리
import time                     # 시간 지연 (API 호출 제한 방지 등)
import json                     # AI 응답(JSON 문자열)을 파이썬 객체로 변환
import re                       # 정규표현식 (필요 시 텍스트 전처리용)

# ==========================================
# [설정] 페이지 기본 설정 및 CSS 디자인 주입
# ==========================================

# 1. 페이지 탭 제목, 아이콘, 레이아웃 설정
st.set_page_config(page_title="Smart AI Outlook", page_icon="🐾", layout="wide")

# 2. 커스텀 CSS 주입
# - unsafe_allow_html=True: Streamlit의 기본 스타일을 덮어쓰기 위해 필수
st.markdown("""
    <style>
    /* 전체 컨테이너 상단 여백 조정 */
    .block-container { padding-top: 2rem; }
    
    /* 버튼(Button) 스타일 커스터마이징 */
    /* 둥근 모서리(border-radius)와 호버 효과(Hover) 추가 */
    .stButton>button {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        background-color: #ffffff;
        color: #333;
        transition: all 0.3s; /* 부드러운 전환 효과 */
    }
    /* 버튼에 마우스 올렸을 때 스타일 */
    .stButton>button:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
        background-color: #fff0f0;
    }
    
    /* 사이드바 프로필 카드 디자인 */
    /* !important: Streamlit 기본 테마(다크모드 등)에 의해 글자색이 바뀌는 것을 방지 (검정 고정) */
    .profile-card {
        color: #000000 !important; 
        background-color: #fff;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #f0f0f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* 메일 상세 화면 헤더 디자인 */
    .mail-header {
        background-color: #f8f9fa;
        color: #000000 !important; /* 글자색 검정 고정 */
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    /* AI 요약 결과 박스 디자인 */
    .summary-box {
        background-color: #e8f5e9; /* 연한 초록 배경 */
        color: #000000 !important; /* 글자색 검정 고정 */
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4caf50; /* 왼쪽 강조선 */
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [함수] 백엔드 로직 (데이터 처리 및 API 통신)
# ==========================================

def get_email_body(msg):
    """
    이메일 객체(msg)에서 순수 텍스트 본문만 추출하는 함수
    이메일은 Multipart(텍스트, HTML, 첨부파일) 구조이므로 재귀적 탐색이 필요함
    """
    if msg.is_multipart():
        # 이메일의 각 파트(Part)를 순회 (walk)
        for part in msg.walk():
            ctype = part.get_content_type() # Content-Type 확인 (text/plain, text/html 등)
            cdispo = str(part.get("Content-Disposition")) # 첨부파일 여부 확인
            
            # 1. 텍스트 타입이고(text/plain)
            # 2. 첨부파일이 아닌 경우(attachment 아님)에만 본문으로 간주
            if ctype == "text/plain" and "attachment" not in cdispo:
                # 바이트 데이터를 디코딩하여 문자열로 반환
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        # Multipart가 아닌 일반 메일일 경우 바로 디코딩
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""

def fetch_emails_imap(username, password, server, limit=15):
    """
    IMAP 프로토콜을 사용하여 메일 서버에서 최근 메일을 가져오는 함수
    params: limit (기본값 15개만 가져오도록 제한하여 속도 최적화)
    """
    email_list = []
    try:
        # 1. SSL 보안 연결 수립 (기본 포트 993)
        mail = imaplib.IMAP4_SSL(server)
        
        # 2. 로그인 (앱 비밀번호 사용)
        mail.login(username, password)
        
        # 3. '받은 편지함(inbox)' 선택
        mail.select("inbox")
        
        # 4. 모든 메일 검색 (검색 조건: ALL) -> 메일 ID 리스트 반환
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split() # ID 문자열을 리스트로 변환
        
        # 5. 최신 메일 순으로 정렬하기 위해 슬라이싱 및 뒤집기
        latest_email_ids = email_ids[-limit:] # 뒤에서부터 limit개 선택
        latest_email_ids.reverse()            # 최신순 정렬

        # 6. 각 메일 ID에 대해 상세 내용 가져오기 (Fetch)
        for e_id in latest_email_ids:
            # RFC822 포맷(이메일 표준 원문)으로 데이터 요청
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # 바이트 데이터를 이메일 객체로 변환
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 제목 디코딩 (한글 깨짐 방지 처리)
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # 보낸 사람, 날짜, 본문 추출
                    sender = msg.get("From")
                    date_str = msg.get("Date")
                    body = get_email_body(msg)

                    # 딕셔너리 형태로 리스트에 추가 (프론트엔드에서 사용하기 위함)
                    email_list.append({
                        "subject": subject,
                        "sender": sender,
                        "body": body,
                        "time": date_str,
                        "summary": None,   # 분석 결과 (초기값 None)
                        "analyzed": False  # 분석 완료 여부 플래그
                    })
        
        # 7. 연결 종료 및 로그아웃
        mail.close()
        mail.logout()
        return email_list
        
    except Exception as e:
        # 에러 발생 시 UI에 에러 메시지 표시
        st.error(f"로그인 실패: {e}")
        return None

def analyze_email_with_gemini(api_key, email_text):
    """
    Google Gemini API를 호출하여 이메일 본문을 분석하는 함수
    """
    try:
        # API 키 공백 제거 (사용자 실수 방지)
        genai.configure(api_key=api_key.strip())
        
        # 모델 설정 (가장 안정적인 최신 Flash 모델 사용)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # [프롬프트 엔지니어링]
        # AI에게 역할을 부여하고, 반드시 JSON 포맷으로 출력하도록 제약조건 설정
        prompt = f"""
        Analyze the email below and return a valid JSON object.
        Strictly follow this JSON format (no markdown code blocks):
        {{
            "summary": "Korean summary in 1-2 sentences",
            "category": "One of [Work, Ad, News, Security, Other]",
            "priority": "High, Medium, or Low",
            "todos": ["Action 1", "Action 2"] (empty list if none)
        }}
        Email Body:
        {email_text[:3000]} 
        """
        # (본문이 너무 길면 토큰 초과될 수 있으므로 앞 3000자만 자름)

        # API 호출 및 응답 받기
        response = model.generate_content(prompt)
        return response.text 
    except Exception as e:
        # API 오류 발생 시 에러 메시지 반환
        return str(e)

def parse_json_result(text):
    """
    AI 응답(문자열)을 파이썬 딕셔너리로 변환하는 헬퍼 함수
    """
    try:
        if not text: return None
        # AI가 가끔 ```json ... ``` 같은 마크다운 코드를 포함하므로 제거
        clean_text = text.replace("```json", "").replace("```", "").strip()
        # JSON 문자열 -> 파이썬 객체 변환
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # JSON 형식이 깨졌을 경우 None 반환 (예외 처리)
        return None

# ==========================================
# [상태 관리] Session State 초기화
# ==========================================
# Streamlit은 상호작용 시마다 코드가 재실행되므로,
# 데이터가 날아가지 않도록 session_state(전역 메모리)에 저장해야 함

if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'user_info' not in st.session_state: st.session_state.user_info = {} # 로그인 정보
if 'my_emails' not in st.session_state: st.session_state.my_emails = [] # 가져온 메일 리스트
if 'selected_idx' not in st.session_state: st.session_state.selected_idx = None # 선택된 메일 인덱스
if 'selected_mail' not in st.session_state: st.session_state.selected_mail = None # 선택된 메일 객체

# ==========================================
# [UI] 사이드바 영역 (로그인 & 필터)
# ==========================================
with st.sidebar:
    # 1. 로그인 전 상태
    if not st.session_state.is_logged_in:
        st.header("🔐 로그인")
        server = st.selectbox("메일 서버", ["outlook.office365.com", "imap.gmail.com"])
        u_email = st.text_input("이메일")
        u_pw = st.text_input("앱 비밀번호", type="password") # 비밀번호 마스킹 처리
        g_key = st.text_input("Gemini API Key", type="password")
        
        if st.button("로그인", type="primary", use_container_width=True):
            if u_email and u_pw and g_key:
                with st.spinner("접속 중..."):
                    # 메일 가져오기 시도
                    emails = fetch_emails_imap(u_email, u_pw, server)
                    if emails is not None:
                        # 성공 시 세션 상태 업데이트 (로그인 처리)
                        st.session_state.is_logged_in = True
                        st.session_state.user_info = {"email": u_email, "pw": u_pw, "server": server, "key": g_key}
                        st.session_state.my_emails = emails
                        st.rerun() # 화면 새로고침
    
    # 2. 로그인 후 상태 (프로필 & 컨트롤 패널)
    else:
        # [프로필 영역]
        user_id = st.session_state.user_info['email'].split('@')[0]
        # RoboHash API를 사용하여 이메일 기반 고유 고양이 아바타 생성 (set4=고양이)
        avatar_url = f"https://robohash.org/{user_id}.png?set=set4&size=150x150" 
        
        # HTML을 사용하여 프로필 카드 렌더링
        st.markdown(f"""
            <div class="profile-card">
                <img src="{avatar_url}" width="100" style="border-radius: 50%; background-color: #f0f0f0; padding: 5px;">
                <h3 style="margin:10px 0 5px 0;">{user_id}</h3>
                <p style="color:gray; font-size:0.8em; margin:0;">{st.session_state.user_info['email']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---") 

        # [필터링 UI]
        st.subheader("🔍 검색")
        search_query = st.text_input("검색어", placeholder="제목/보낸이")
        date_filter = st.selectbox("📅 기간", ["전체 메일", "오늘", "최근 3일", "최근 1주일"])
        
        st.markdown("---")
        
        st.subheader("🔥 중요도")
        priority_filter = st.radio("중요도", ["전체", "High", "Medium", "Low"])
        
        st.markdown("---")
        
        st.subheader("📂 카테고리")
        category_filter = st.radio("카테고리", ["전체", "Work", "Ad", "News", "Security", "Other"])
        
        st.divider()
        
        # 하단 버튼 (동기화/로그아웃)
        c1, c2 = st.columns(2)
        if c1.button("🔄 동기화"):
            info = st.session_state.user_info
            emails = fetch_emails_imap(info['email'], info['pw'], info['server'])
            if emails: st.session_state.my_emails = emails
            st.rerun()
            
        if c2.button("로그아웃"):
            st.session_state.clear() # 세션 초기화
            st.rerun()

# ==========================================
# [UI] 메인 화면 (리스트 & 상세 보기)
# ==========================================
if st.session_state.is_logged_in:
    
    # ---------------------------
    # 1. 필터링 로직 (Python List Filtering)
    # ---------------------------
    filtered_emails = st.session_state.my_emails
    
    # 날짜 필터 (IMAP 검색 대신 파이썬 슬라이싱으로 간략 구현)
    if date_filter == "오늘": filtered_emails = filtered_emails[:2]
    elif date_filter == "최근 3일": filtered_emails = filtered_emails[:5]
    
    # 검색어 필터 (제목 또는 보낸사람 매칭)
    if search_query:
        q = search_query.lower()
        filtered_emails = [e for e in filtered_emails if q in e['subject'].lower() or q in e['sender'].lower()]
        
    # 중요도 필터 (분석 완료된 메일에 한해 JSON 결과값 비교)
    if priority_filter != "전체":
        temp_list = []
        for e in filtered_emails:
            if e['analyzed']:
                data = parse_json_result(e['summary'])
                if data and data.get('priority') == priority_filter: temp_list.append(e)
        filtered_emails = temp_list
        
    # 카테고리 필터
    if category_filter != "전체":
        temp_list = []
        for e in filtered_emails:
            if e['analyzed']:
                data = parse_json_result(e['summary'])
                # 대소문자 무시 비교 (in 연산자 사용)
                if data and category_filter.lower() in data.get('category', '').lower(): temp_list.append(e)
        filtered_emails = temp_list

    # ---------------------------
    # 2. 레이아웃 분할 (2단)
    # ---------------------------
    col_list, col_detail = st.columns([2, 3]) # 2:3 비율
    
    # [왼쪽] 메일 목록 패널
    with col_list:
        st.subheader(f"📥 메일함 ({len(filtered_emails)})")
        
        if not filtered_emails: st.info("메일이 없어요! 🐱")
        
        # 메일 리스트 루프
        for i, mail in enumerate(filtered_emails):
            # 분석 여부에 따라 아이콘 변경
            status = "✅" if mail['analyzed'] else "✉️"
            label = f"{status} {mail['sender'].split('<')[0]}\n\n{mail['subject'][:20]}..."
            
            # 버튼 클릭 시 해당 메일 객체를 세션에 저장 (선택 상태 유지)
            # key 값을 유니크하게 설정하여 충돌 방지
            if st.button(label, key=f"btn_{i}_{mail['subject'][:5]}", use_container_width=True):
                st.session_state.selected_mail = mail

    # [오른쪽] 상세 보기 패널
    with col_detail:
        # 선택된 메일이 없을 때 안내 메시지
        if 'selected_mail' not in st.session_state or st.session_state.selected_mail is None:
            st.markdown("<div style='text-align:center; padding-top:50px;'><h3>👈 왼쪽에서 메일을 선택해주세요!</h3></div>", unsafe_allow_html=True)
        else:
            sel_mail = st.session_state.selected_mail
            
            # 메일 헤더 (제목/보낸이/시간) 렌더링
            st.markdown(f"""
                <div class="mail-header">
                    <h3 style="margin-top:0;">{sel_mail['subject']}</h3>
                    <p style="margin-bottom:0; color:#555;"><b>보낸사람:</b> {sel_mail['sender']}</p>
                    <p style="font-size:0.8em; color:#888;">{sel_mail['time']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # A. 아직 분석되지 않은 경우
            if not sel_mail['analyzed']:
                if st.button("✨ AI 분석 실행", type="primary"):
                    with st.spinner("고양이가 읽는 중... 🐱"):
                        # Gemini API 호출
                        raw_res = analyze_email_with_gemini(st.session_state.user_info['key'], sel_mail['body'])
                        # 결과 저장 및 분석 플래그 True 설정
                        sel_mail['summary'] = raw_res
                        sel_mail['analyzed'] = True
                        st.rerun() # UI 갱신
            
            # B. 분석 완료된 경우 (결과 시각화)
            else:
                data = parse_json_result(sel_mail['summary'])
                if data:
                    # 상단 배지 영역 (카테고리 / 중요도)
                    c1, c2 = st.columns(2)
                    with c1: st.markdown(f"**📂 카테고리:** `{data.get('category', '기타')}`")
                    with c2:
                        # 중요도에 따른 색상 분기 처리
                        prio = data.get('priority', 'Low')
                        color = "red" if prio == 'High' else "orange" if prio == 'Medium' else "green"
                        st.markdown(f"**🔥 중요도:** :{color}[{prio}]")
                    
                    # 요약 박스 (CSS .summary-box 적용)
                    st.markdown(f"""
                        <div class="summary-box">
                            <b>📌 AI 요약:</b><br>
                            {data.get('summary', '요약 없음')}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 할 일 목록 체크박스
                    todos = data.get('todos', [])
                    if todos:
                        st.write("✅ **할 일 목록**")
                        for todo in todos: st.checkbox(todo, key=f"check_{todo}")
            
            # 원문 보기 (아코디언)
            st.divider()
            with st.expander("📄 메일 원문 보기"): st.text(sel_mail['body'])

else:
    # 로그인 전 메인 화면은 비워둠
    st.empty()