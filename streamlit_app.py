import streamlit as st
from datetime import datetime

# ==========================================
# [기본 설정] 페이지 및 데이터
# ==========================================
st.set_page_config(page_title="Outlook Style AI", page_icon="📧", layout="wide")

# 더미 데이터
dummy_emails = [
    {"id": 1, "subject": "[긴급] 2025년 상반기 개발 로드맵 수정 요청", "sender": "김철수 팀장", "time": "10:30", "category": "업무", "priority": "High", "summary": "로드맵 수정 및 내일 오전 회신 요청.", "body": "팀장입니다. 어제 회의 결과 반영하여..."},
    {"id": 2, "subject": "AWS EC2 Scheduled Maintenance Notification", "sender": "AWS Support", "time": "09:15", "category": "뉴스/알림", "priority": "Medium", "summary": "EC2 인스턴스 정기 점검 알림.", "body": "Hello, We have scheduled maintenance..."},
    {"id": 3, "subject": "(광고) 연말 맞이 50% 할인 쿠폰", "sender": "쿠팡", "time": "08:00", "category": "광고", "priority": "Low", "summary": "할인 쿠폰 광고.", "body": "고객님만을 위한 특별한 혜택..."},
    {"id": 4, "subject": "주간 업무 보고 제출 부탁드립니다.", "sender": "이영희 대리", "time": "어제", "category": "업무", "priority": "Medium", "summary": "금주 주간 업무 보고 작성 요청.", "body": "다들 고생 많으십니다. 이번 주 업무 보고..."},
    {"id": 5, "subject": "사내 시스템 점검 안내 (12/20)", "sender": "IT 지원팀", "time": "어제", "category": "사내공지", "priority": "Low", "summary": "12월 20일 사내 시스템 점검 예정.", "body": "안정적인 서비스 제공을 위해..."}
]

# ==========================================
# [핵심 로직] Session State (선택 상태 기억)
# ==========================================
if 'selected_email_index' not in st.session_state:
    st.session_state.selected_email_index = None 

def select_email(index):
    st.session_state.selected_email_index = index

# ==========================================
# [UI 구조] 3단 레이아웃
# ==========================================

# 1. [좌측 패널] 사이드바
with st.sidebar:
    st.header("🗂️ 폴더")
    st.button("📥 받은 편지함 (5)", use_container_width=True, type="primary")
    st.button("📤 보낸 편지함", use_container_width=True)
    st.button("📝 임시 보관함", use_container_width=True)
    
    st.divider()
    
    st.header("🔍 검색 및 필터")
    st.date_input("날짜", datetime.now())
    categories = ["전체"] + sorted(list(set(e['category'] for e in dummy_emails)))
    selected_category = st.radio("카테고리", categories)

col_list, col_read = st.columns([2, 3])

# 2. [중간 패널] 메일 목록
with col_list:
    st.subheader("받은 편지함")
    filtered_emails = dummy_emails if selected_category == "전체" else [e for e in dummy_emails if e['category'] == selected_category]
    
    st.markdown("---")
    
    if not filtered_emails:
        st.info("표시할 메일이 없습니다.")
    else:
        # [수정됨] 오타 수정 (unsafe_allow_allow_html -> unsafe_allow_html)
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                text-align: left; 
                border-radius: 0px;
                border: none;
                border-bottom: 1px solid #f0f2f6;
                padding: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        for i, mail in enumerate(filtered_emails):
            emoji = "🔴" if mail['priority'] == "High" else "🟠" if mail['priority'] == "Medium" else "🟢"
            button_label = f"{emoji} **{mail['sender']}** \n {mail['subject']} \n 🕒 {mail['time']}"
            
            st.button(
                button_label, 
                key=f"mail_btn_{i}", 
                use_container_width=True,
                on_click=select_email,
                args=(i,)
            )

# 3. [우측 패널] 읽기 창
with col_read:
    current_index = st.session_state.selected_email_index
    
    if current_index is None or current_index >= len(filtered_emails):
        st.markdown(
            """
            <div style='text-align: center; padding: 50px; color: gray;'>
                <h1>📧</h1>
                <h3>메일을 선택하여 내용을 확인하세요.</h3>
                <p>AI 요약과 할 일이 이곳에 표시됩니다.</p>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        selected_mail = filtered_emails[current_index]
        
        # [수정됨] 오타 수정 (unsafe_allow_allow_html -> unsafe_allow_html)
        st.markdown(
            f"""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>
                <h2 style='margin:0; color: #0078d4;'>{selected_mail['subject']}</h2>
                <p style='margin: 10px 0 5px 0;'><b>보낸사람:</b> {selected_mail['sender']}</p>
                <p style='margin:0; color: gray; font-size: 0.9em;'>수신: {selected_mail['time']}</p>
                <div style='margin-top: 15px;'>
                    <span style='background-color: #e1dfdd; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;'>{selected_mail['category']}</span>
                    <span style='background-color: {'#ffcccc' if selected_mail['priority'] == 'High' else '#ffe5cc'}; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 5px;'>중요도: {selected_mail['priority']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

        st.info(f"🤖 **AI 요약:** {selected_mail['summary']}", icon="📌")
        
        tab1, tab2 = st.tabs(["📄 메일 본문", "✅ 할 일(Action Items)"])
        
        with tab1:
            st.write(selected_mail['body'])
            st.write("---")
            st.caption("이 메일은 AI 비서가 분석했습니다.")
            
        with tab2:
            st.write("이 메일에서 추출된 할 일입니다.")
            st.checkbox("메일 내용 확인 및 회신")
            if selected_mail['priority'] == 'High':
                 st.checkbox("팀장님께 보고", value=True)