import openai
import os
from datetime import datetime

class AICounselor:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def generate_response(self, mood_text, sentiment_data):
        """
        Generate empathetic response using OpenAI GPT
        Style: Hinglish, short, culturally friendly
        """
        sentiment = sentiment_data['sentiment']
        polarity = sentiment_data['polarity']
        
        # Create context-aware prompt
        system_prompt = """You are a compassionate AI counselor for an Indian mental wellness app. 
        Respond in a warm, empathetic tone using Hinglish (mix of Hindi and English). 
        Keep responses short (2-3 sentences max), culturally sensitive, and supportive.
        Use common Hindi words naturally mixed with English."""
        
        user_prompt = f"""
        User shared: "{mood_text}"
        Sentiment: {sentiment} (polarity: {polarity})
        
        Provide a supportive response that acknowledges their feelings and offers gentle encouragement.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback responses if OpenAI fails
            fallback_responses = {
                'positive': "Yeh sunke bahut khushi hui! 😊 Aap ka positive energy infectious hai. Keep spreading the good vibes!",
                'negative': "Main samajh sakta hun ki aap kuch mushkil waqt se guzar rahe hain. Remember, har raat ke baad ek nayi subah hoti hai. ✨",
                'neutral': "Thanks for sharing yeh mere saath. Sometimes it's okay to feel normal - not every day needs to be extraordinary. Take care! 🌱"
            }
            
            return fallback_responses.get(sentiment, "Thank you for sharing. Main yahaan hun aap ke saath. 💙")
