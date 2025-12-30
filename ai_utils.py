import google.generativeai as genai
import json

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def analyze_email(email_content, model_name="gemini-1.5-flash"):
    """
    Analyzes email content to provide summary, priority, and category.
    Returns a JSON object.
    """
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Analyze the following email content and provide:
        1. A concise summary (max 2 sentences).
        2. Priority level (High, Medium, Low) based on urgency and importance.
        3. A category (e.g., Work, Personal, Newsletter, Spam, Finance, Social).
        
        Return the result strictly in valid JSON format like this:
        {{
            "summary": "...",
            "priority": "...",
            "category": "..."
        }}
        
        Email Content:
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
