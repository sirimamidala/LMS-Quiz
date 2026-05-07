import google.generativeai as genai
import json
import re
from django.conf import settings

def generate_mcqs(topic, count=30):
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    prompt = f"""
    Generate {count} multiple-choice questions about '{topic}'.
    The output must be a valid JSON array of objects.
    Each object must have exactly these keys:
    - "question": The question text.
    - "a": Option A
    - "b": Option B
    - "c": Option C
    - "d": Option D
    - "answer": The correct option letter (A, B, C, or D).
    
    Make the questions engaging and varied in difficulty. 
    Ensure the JSON is strictly formatted without any markdown or extra text.
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Clean potential markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        questions = json.loads(content)
        return questions
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        return []
