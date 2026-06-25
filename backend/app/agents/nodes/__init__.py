import json
import google.generativeai as genai
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def call_gemini_json(system_prompt: str, user_content: str, fallback_data: dict) -> dict:
    """
    Utility helper that requests a structured JSON output from Gemini.
    Provides immediate fallback structures if API key or execution fails.
    """
    if not settings.GEMINI_API_KEY:
        print("[WARNING] GEMINI_API_KEY is not set. Using fallback mockup data.")
        return fallback_data
        
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt
        )
        # Request JSON output specifically
        response = model.generate_content(
            user_content,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Clean response text and parse
        text = response.text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"[ERROR] Gemini API execution failed: {e}. Returning fallback mockup.")
        return fallback_data
