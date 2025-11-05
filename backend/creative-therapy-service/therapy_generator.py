import openai
import os
import random
from datetime import datetime

class TherapyGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Pre-defined prompts for fallback
        self.art_prompts = [
            "Draw your current emotion as a weather pattern - is it sunny, stormy, or somewhere in between?",
            "Create a mandala representing your inner peace. Use colors that make you feel calm.",
            "Sketch a safe space where you feel completely comfortable. What does it look like?",
            "Draw your stress as a shape, then transform it into something beautiful.",
            "Create artwork showing your journey from today to where you want to be tomorrow."
        ]
        
        self.indian_classical_ragas = {
            'happy': ['Raga Yaman', 'Raga Bilawal', 'Raga Kafi'],
            'sad': ['Raga Darbari', 'Raga Malkauns', 'Raga Bhairav'],
            'stressed': ['Raga Bageshri', 'Raga Bhoopali', 'Raga Jaunpuri'],
            'neutral': ['Raga Khamaj', 'Raga Bihag', 'Raga Hamir']
        }
    
    def generate_art_prompt(self, mood_data, cultural_context=None):
        """Generate personalized art therapy prompt"""
        sentiment = mood_data['sentiment']
        mood_text = mood_data.get('mood_text', '')
        
        system_prompt = """You are a creative art therapist. Generate a personalized, therapeutic art prompt 
        that helps the user express and process their emotions. Keep it simple, achievable, and healing-focused.
        Make it culturally sensitive for Indian users. Maximum 2 sentences."""
        
        cultural_info = ""
        if cultural_context and cultural_context['cultural_context_detected']:
            stressors = ", ".join(cultural_context['stressor_categories'])
            cultural_info = f" considering their cultural stressors: {stressors}"
        
        user_prompt = f"""
        User is feeling: {sentiment}
        Their words: "{mood_text}"
        Generate a therapeutic art prompt{cultural_info} that helps them express and process these emotions.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            return {
                'type': 'art',
                'prompt': response.choices[0].message.content.strip(),
                'generated_by': 'ai',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Fallback to pre-defined prompts
            return {
                'type': 'art',
                'prompt': random.choice(self.art_prompts),
                'generated_by': 'fallback',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def generate_music_suggestion(self, mood_data, cultural_context=None):
        """Generate therapeutic music suggestions"""
        sentiment = mood_data['sentiment']
        
        # Classical Indian raga suggestion
        raga_suggestion = random.choice(self.indian_classical_ragas.get(sentiment, self.indian_classical_ragas['neutral']))
        
        system_prompt = """You are a music therapist specializing in Indian classical and fusion music.
        Suggest therapeutic music that combines Indian classical elements with modern genres.
        Include specific artists, ragas, or fusion styles. Keep it concise and practical."""
        
        user_prompt = f"""
        User is feeling: {sentiment}
        Suggest 2-3 specific therapeutic music recommendations that blend Indian classical with modern elements.
        Include the raga: {raga_suggestion}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_suggestion = response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback suggestions
            fallback_suggestions = {
                'happy': f"Try listening to {raga_suggestion} in a fusion style, or upbeat Bollywood instrumentals with classical touches.",
                'sad': f"Listen to {raga_suggestion} played on flute or santoor. The gentle melody can be very healing.",
                'stressed': f"{raga_suggestion} played at a slow tempo can help calm your mind. Try instrumental versions.",
                'neutral': f"Explore {raga_suggestion} in different interpretations - classical, fusion, or contemporary arrangements."
            }
            ai_suggestion = fallback_suggestions.get(sentiment, fallback_suggestions['neutral'])
        
        return {
            'type': 'music',
            'raga_suggestion': raga_suggestion,
            'detailed_suggestion': ai_suggestion,
            'spotify_search_terms': [
                f"{raga_suggestion} instrumental",
                "Indian classical fusion",
                "therapeutic Indian music",
                f"{sentiment} mood Indian classical"
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
