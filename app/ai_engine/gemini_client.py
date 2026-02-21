"""Gemini client: send prompts and get text (or JSON) back."""
import google.generativeai as genai
from app.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY or "")

# Use a model that supports generateContent in the current API. If you get 429, try gemini-2.5-flash-lite.
MODEL_NAME = "gemini-2.5-flash"


def get_model():
    """Return the Gemini model instance."""
    return genai.GenerativeModel(MODEL_NAME)


def generate_text(prompt, system_instruction=None):
    """Send the prompt to Gemini and return the response as a string."""
    model = get_model()
    response = model.generate_content(prompt)
    if response and response.candidates:
        part = response.candidates[0].content.parts[0]
        return part.text if hasattr(part, "text") else str(part)
    return ""