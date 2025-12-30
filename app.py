from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import email_utils
import ai_utils
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# 1. 로그인 페이지 (GET)
@app.route('/')
def login_page():
    return render_template('login.html')

# 2. 로그인 처리 및 대시보드 (POST/GET)
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    # 세션에서 정보 확인
    if request.method == 'GET':
        if 'email_id' not in session:
            return redirect(url_for('login_page'))
        
        email_id = session['email_id']
        email_pw = session['email_pw']
        server = session['server']
        api_key = session['api_key']
    else:
        # POST 요청: 로그인 폼 제출
        server = request.form['server']
        email_id = request.form['email'].strip()
        email_pw = request.form['password'].strip()
        api_key = request.form['apikey'].strip()

    # ---------------------------------------------------
    # [1단계] 이메일 서버(IMAP) 로그인 & 이메일 가져오기
    # ---------------------------------------------------
    mail = email_utils.connect_imap(server, email_id, email_pw)
    if not mail:
        if request.method == 'POST':
            flash("이메일 로그인 실패! 아이디와 앱 비밀번호를 확인해주세요.")
            return redirect(url_for('login_page'))
        else:
            # 세션은 있는데 연결이 안 되면 다시 로그인 유도
            session.clear()
            return redirect(url_for('login_page'))

    # 검색어 처리
    search_query = request.args.get('search', 'ALL')
    if request.args.get('search'):
        # Simple keyword search on Subject
        # IMAP search criteria is complex, simplistic approach:
        # SEARCH SUBJECT "keyword"
        keyword = request.args.get('search')
        search_criteria = f'(SUBJECT "{keyword}")'
    else:
        search_criteria = "ALL"

    try:
        emails = email_utils.fetch_emails(mail, limit=15, search_criteria=search_criteria)
    except Exception as e:
        flash(f"이메일 가져오기 실패: {e}")
        emails = []
    
    mail.logout()

    # ---------------------------------------------------
    # [2단계] Gemini API 설정 (세션 저장)
    # ---------------------------------------------------
    if api_key:
        ai_utils.configure_gemini(api_key)
    
    # 세션 저장 (로그인 시에만, 혹은 갱신)
    session['email_id'] = email_id
    session['email_pw'] = email_pw
    session['server'] = server
    session['api_key'] = api_key

    return render_template('dashboard.html', emails=emails)


# 3. AI 분석 endpoint (AJAX)
@app.route('/api/analyze', methods=['POST'])
def analyze_email_api():
    if 'api_key' not in session:
        return jsonify({"error": "No API Key provided"}), 401
    
    content = request.json.get('content')
    if not content:
        return jsonify({"error": "No content to analyze"}), 400

    # AI 설정 확인
    ai_utils.configure_gemini(session['api_key'])
    
    result = ai_utils.analyze_email(content)
    return jsonify(result)

if __name__ == '__main__':
    # 맥북 포트 충돌 방지를 위해 5001번 사용
    app.run(debug=True, port=5001)