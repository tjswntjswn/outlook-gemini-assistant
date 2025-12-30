import google.generativeai as genai

# 새로 발급받은 키 (이미 확인했습니다)
genai.configure(api_key="{api_key}")

# 목록에 있던 모델 중 가장 안정적인 것으로 변경
model = genai.GenerativeModel("models/gemma-3-4b-it")

try:
    # 아주 가벼운 요청으로 쿼터 체크
    response = model.generate_content("hi")
    print("✅ 드디어 성공! 요약 내용:", response.text)
except Exception as e:
    print(f"❌ 아직 안 됨. 에러 내용: {e}")