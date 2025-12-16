import streamlit as st
import time

# 페이지 설정
st.set_page_config(page_title="AI Outlook Design Preview", page_icon="🎨", layout="wide")

# ==========================================
# [사이드바]
# ==========================================
with st.sidebar:
    st.header("⚙️ 설정")
    st.text_input("Gemini API Key", type="password", placeholder="디자인 미리보기 모드입니다")
    st.slider("검색 시간 범위(시간)", 1, 72, 24)
    st.info("💡 현재는 '디자인 미리보기' 모드이므로 실제 메일을 가져오지 않습니다.")
    st.divider()
    st.caption("Developed by You")

# ==========================================
# [메인 화면]
# ==========================================
st.title("📧 AI Outlook Assistant (Preview)")
st.markdown("##### 🚀 AI가 당신의 메일함을 정리하고 있습니다.")

# 버튼 스타일
if st.button("🔄 메일 가져오기 및 분석 시작", type="primary"):
    
    # 가짜 로딩 효과
    with st.spinner('Outlook 메일 스캔 중...'):
        time.sleep(0.5)
    
    # 진행률 표시
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        progress_bar.progress(i + 1)
    
    st.success("분석이 완료되었습니다!")

    # ==========================================
    # [가짜 데이터 - UI 확인용]
    # ==========================================
    dummy_emails = [
        {
            "sender": "김철수 팀장",
            "subject": "[긴급] 2025년 상반기 개발 로드맵 수정 요청",
            "time": "2025-12-16 09:30",
            "preview": "안녕하세요, 김팀장입니다. 지난 회의에서 논의된 사항을 바탕으로 로드맵 수정이 필요합니다...",
            "ai_result": {
                "summary": "지난 회의 내용을 반영하여 상반기 개발 로드맵을 수정하고 내일 오전까지 재송부 요청함.",
                "category": "업무",
                "priority": "High",
                "todos": ["로드맵 수정안 작성", "내일 오전 10시 전까지 메일 회신"],
                "translation": None
            }
        },
        {
            "sender": "John Doe (AWS)",
            "subject": "AWS Notification - EC2 Instance Scheduled Maintenance",
            "time": "2025-12-16 08:15",
            "preview": "Hello, This is a notification regarding your EC2 instances in ap-northeast-2 region...",
            "ai_result": {
                "summary": "ap-northeast-2 리전의 EC2 인스턴스 정기 점검이 예정되어 있음. 리부팅 필요.",
                "category": "뉴스/알림",
                "priority": "Medium",
                "todos": ["서버 상태 확인", "점검 시간 공지"],
                "translation": "귀하의 ap-northeast-2 리전 EC2 인스턴스에 대한 유지 보수 작업 알림입니다."
            }
        },
        {
            "sender": "쿠팡",
            "subject": "(광고) 이번 주 특가 상품을 놓치지 마세요!",
            "time": "2025-12-15 18:00",
            "preview": "고객님을 위한 특별한 혜택! 최대 50% 할인 쿠폰이 도착했습니다...",
            "ai_result": {
                "summary": "주간 특가 상품 및 50% 할인 쿠폰 안내 광고 메일.",
                "category": "광고",
                "priority": "Low",
                "todos": [],
                "translation": None
            }
        }
    ]

    # ==========================================
    # [카드 UI 렌더링]
    # ==========================================
    for idx, email in enumerate(dummy_emails):
        ai = email['ai_result']
        
        # Expander: 접었다 폈다 할 수 있는 카드
        with st.expander(f"[{email['sender']}] {email['subject']}", expanded=True):
            
            col1, col2 = st.columns([1, 2])
            
            # 왼쪽: 메일 기본 정보
            with col1:
                st.caption(f"📅 수신: {email['time']}")
                st.text_area("메일 원문", email['preview'], height=120, disabled=True, key=f"txt_{idx}")
            
            # 오른쪽: AI 분석 결과
            with col2:
                # 1. 뱃지 및 카테고리 헤더
                if ai['priority'] == 'High':
                    badge_color = "red"
                    emoji = "🔴"
                elif ai['priority'] == 'Medium':
                    badge_color = "orange"
                    emoji = "🟠"
                else:
                    badge_color = "green"
                    emoji = "🟢"
                
                st.markdown(f"### {emoji} :{badge_color}[**{ai['priority']} Priority**] &nbsp; | &nbsp; 📂 {ai['category']}")
                
                # 2. 요약 박스
                st.info(f"**요약:** {ai['summary']}")
                
                # 3. 할 일 (체크박스)
                if ai['todos']:
                    st.write("**✅ Action Items:**")
                    for todo in ai['todos']:
                        st.checkbox(todo, key=f"todo_{idx}_{todo}")
                
                # 4. 번역 (채팅 UI 느낌)
                if ai['translation']:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(f"**번역:** {ai['translation']}")

    st.toast("모든 메일 분석이 완료되었습니다!", icon="🎉")