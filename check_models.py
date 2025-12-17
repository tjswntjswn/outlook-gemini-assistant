import google.generativeai as genai
import os

# 여기에 아까 발급받은 API 키를 넣으세요
GOOGLE_API_KEY = "AIzaSyB7on3tB0RuGPimgxYZCPuycGRwLeBMHpo"

genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 사용 가능한 모델 목록 조회 중...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"❌ 에러 발생: {e}")