import google.generativeai as genai

# 👇 여기에 발급받은 API 키를 넣어주세요
api_key = "{api_key}"

genai.configure(api_key=api_key)

print("🔍 사용 가능한 Gemini 모델 목록 조회 중...")

try:
    available_models = []
    for m in genai.list_models():
        # 대화(채팅) 기능이 있는 모델만 필터링
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 발견: {m.name}")
            available_models.append(m.name)

    if not available_models:
        print("\n❌ 사용 가능한 모델이 하나도 안 뜹니다. API 키 권한 문제일 수 있습니다.")
    else:
        print("\n💡 위 목록에 뜬 이름 중 하나를 app.py에 적으면 100% 됩니다.")

except Exception as e:
    print(f"\n🚨 조회 실패: {e}")