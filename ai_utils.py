import google.generativeai as genai
import json

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def analyze_email(email_content, model_name="models/gemma-3-4b-it"):
    """
    Analyzes email content to provide summary, priority, and category.
    Returns a JSON object.
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        다음 이메일 내용을 분석해서 JSON 형식으로 응답해줘.
        1. summary: 핵심 내용 1~2문장 요약 (한국어)
        2. priority: 중요도 (High, Medium, Low 중 하나)
        3. category: 분류 (업무, 개인, 뉴스레터, 쇼핑, 금융 중 하나)
        
        응답은 반드시 아래 JSON 형식만 출력해:
        {{
            "summary": "...",
            "priority": "...",
            "category": "..."
        }}
        
        이메일 내용:
        {email_content}
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up potential markdown formatting in response (```json ... ```)
        if text_response.startswith("```"):
            text_response = text_response.strip("`")
            if text_response.startswith("json"):
                text_response = text_response[4:]
        
        return json.loads(text_response)
        
    except Exception as e:
        print(f"AI Analysis failed: {e}")
        return {
            "summary": "Analysis failed.",
            "priority": "Unknown",
            "category": "Uncategorized"
        }
