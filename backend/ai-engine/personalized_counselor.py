import openai
import os
from datetime import datetime, timedelta
from shared.db_config import get_db
from shared.redis_config import redis_cache
import logging

logger = logging.getLogger(__name__)

class PersonalizedCounselor:
    """AI Counselor with user memory and personalization"""
    
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.context_limit = int(os.getenv('USER_CONTEXT_HISTORY_LIMIT', 10))
        self.tone_adaptive = os.getenv('COUNSELOR_TONE_ADAPTIVE', 'true').lower() == 'true'
    
    def get_user_context(self, user_id):
        """Get user context from cache or database"""
        try:
            # Check cache first
            if os.getenv('MEMORY_CACHE_ENABLED', 'true').lower() == 'true':
                cached_context = redis_cache.get_user_context(user_id)
                if cached_context:
                    return cached_context
            
            # Build context from database
            db = get_db()
            
            # Get recent mood entries
            recent_moods = list(db.mood_entries.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(self.context_limit))
            
            # Get user info
            user = db.users.find_one({'_id': user_id})
            
            # Build context
            context = {
                'user_id': user_id,
                'name': user.get('name', ''),
                'recent_moods': [],
                'dominant_stressors': [],
                'mood_trend': 'unknown',
                'last_interaction': None
            }
            
            # Process recent moods
            stressor_counts = {}
            mood_scores = []
            
            for entry in recent_moods:
                # Add to recent moods
                context['recent_moods'].append({
                    'timestamp': entry['timestamp'].isoformat(),
                    'sentiment': entry.get('sentiment_analysis', {}).get('sentiment', 'neutral'),
                    'text_preview': entry.get('mood_text', '')[:50] if entry.get('mood_text') else ''
                })
                
                # Count stressors
                cultural_context = entry.get('cultural_context', {})
                for stressor in cultural_context.get('stressor_categories', []):
                    stressor_counts[stressor] = stressor_counts.get(stressor, 0) + 1
                
                # Track mood scores
                polarity = entry.get('sentiment_analysis', {}).get('polarity', 0)
                mood_scores.append(polarity)
            
            # Determine dominant stressors
            if stressor_counts:
                sorted_stressors = sorted(stressor_counts.items(), key=lambda x: x[1], reverse=True)
                context['dominant_stressors'] = [s[0] for s in sorted_stressors[:3]]
            
            # Calculate mood trend
            if len(mood_scores) >= 3:
                recent_avg = sum(mood_scores[:3]) / 3
                older_avg = sum(mood_scores[3:]) / len(mood_scores[3:]) if len(mood_scores) > 3 else recent_avg
                
                if recent_avg > older_avg + 0.2:
                    context['mood_trend'] = 'improving'
                elif recent_avg < older_avg - 0.2:
                    context['mood_trend'] = 'declining'
                else:
                    context['mood_trend'] = 'stable'
            
            # Last interaction
            if recent_moods:
                context['last_interaction'] = recent_moods[0]['timestamp'].isoformat()
            
            # Cache context
            if os.getenv('MEMORY_CACHE_ENABLED', 'true').lower() == 'true':
                redis_cache.set_user_context(user_id, context)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get user context: {str(e)}")
            return {'user_id': user_id}
    
    def determine_tone(self, user_context, current_sentiment):
        """Determine appropriate counselor tone"""
        if not self.tone_adaptive:
            return 'supportive'
        
        mood_trend = user_context.get('mood_trend', 'stable')
        sentiment = current_sentiment.get('sentiment', 'neutral')
        
        # Decision matrix for tone
        if mood_trend == 'improving' and sentiment in ['positive', 'neutral']:
            return 'motivational'
        elif mood_trend == 'declining' or sentiment == 'negative':
            return 'compassionate'
        elif mood_trend == 'stable':
            return 'reflective'
        else:
            return 'supportive'
    
    def generate_personalized_response(self, mood_text, sentiment_data, cultural_context, user_context, voice_emotion=None):
        """Generate personalized AI response with memory"""
        try:
            sentiment = sentiment_data.get('sentiment', 'neutral')
            tone = self.determine_tone(user_context, sentiment_data)
            
            # Build system prompt with tone
            tone_instructions = {
                'supportive': 'Be warm, understanding, and encouraging. Show consistent support.',
                'motivational': 'Be energetic, positive, and inspiring. Celebrate their progress.',
                'compassionate': 'Be gentle, empathetic, and validating. Acknowledge their struggles deeply.',
                'reflective': 'Be thoughtful, curious, and help them explore their feelings.'
            }
            
            system_prompt = f"""You are a compassionate AI counselor for Eirene mental wellness app.
            You remember past conversations and provide personalized support.
            
            Tone: {tone.upper()} - {tone_instructions.get(tone, 'Be supportive and warm')}
            
            Response Style:
            - Use natural Hinglish (Hindi + English mix)
            - Keep responses 3-4 sentences
            - Reference past conversations when relevant
            - Be culturally sensitive to Indian context
            - Show continuity and memory of user's journey"""
            
            # Build user prompt with context
            prompt_parts = []
            
            # Add user history
            name = user_context.get('name', '')
            if name:
                prompt_parts.append(f"User name: {name}")
            
            # Add mood trend
            mood_trend = user_context.get('mood_trend', 'unknown')
            if mood_trend != 'unknown':
                prompt_parts.append(f"Recent mood trend: {mood_trend}")
            
            # Add dominant stressors
            stressors = user_context.get('dominant_stressors', [])
            if stressors:
                prompt_parts.append(f"Recurring stressors: {', '.join(stressors)}")
            
            # Add recent context
            recent_moods = user_context.get('recent_moods', [])
            if len(recent_moods) > 1:
                last_mood = recent_moods[1]  # Previous mood (not current)
                days_ago = (datetime.utcnow() - datetime.fromisoformat(last_mood['timestamp'])).days
                if days_ago <= 7:
                    prompt_parts.append(f"Last time ({days_ago} days ago): {last_mood['sentiment']} - '{last_mood['text_preview']}'")
            
            # Current situation
            prompt_parts.append(f"\nCurrent message: \"{mood_text}\"")
            prompt_parts.append(f"Current sentiment: {sentiment}")
            
            # Cultural context
            if cultural_context and cultural_context.get('cultural_context_detected'):
                stressor_list = ", ".join(cultural_context.get('stressor_categories', []))
                prompt_parts.append(f"Cultural stressors detected: {stressor_list}")
            
            # Voice context
            if voice_emotion:
                prompt_parts.append(f"Voice emotion: {voice_emotion.get('emotion', 'unknown')}")
            
            prompt_parts.append("\nProvide a personalized response that:")
            prompt_parts.append("1. Shows you remember their journey")
            prompt_parts.append("2. Acknowledges their current feelings")
            prompt_parts.append("3. References relevant past experiences if applicable")
            prompt_parts.append(f"4. Uses {tone} tone")
            prompt_parts.append("5. Responds in natural Hinglish")
            
            user_prompt = "\n".join(prompt_parts)
            
            # Generate response
            response = openai.ChatCompletion.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 200)),
                temperature=float(os.getenv('OPENAI_TEMPERATURE', 0.7))
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            logger.info(f"Personalized response generated with tone: {tone}")
            
            return {
                'response': ai_response,
                'tone': tone,
                'personalized': True,
                'context_used': len(recent_moods) > 0
            }
            
        except Exception as e:
            logger.error(f"Personalized response generation failed: {str(e)}")
            # Fallback to basic response
            return {
                'response': self._get_fallback_response(sentiment_data, tone if 'tone' in locals() else 'supportive'),
                'tone': 'supportive',
                'personalized': False,
                'error': str(e)
            }
    
    def _get_fallback_response(self, sentiment_data, tone='supportive'):
        """Fallback responses"""
        sentiment = sentiment_data.get('sentiment', 'neutral')
        
        responses = {
            'supportive': {
                'positive': "[translate:Bahut khushi hui] hearing this! Keep up the positive energy! 😊",
                'negative': "[translate:Samajh sakta hun] this is tough. [translate:Main yahaan hun] for you. Take it one step at a time. 💙",
                'neutral': "Thanks for sharing. [translate:Kaise feel kar rahe ho], we can explore it together. 🌱"
            },
            'motivational': {
                'positive': "Yes! You're doing amazing! [translate:Aur aage badho]! 🚀",
                'negative': "I know it's hard, but you've got this! [translate:Himmat mat haro]! 💪",
                'neutral': "[translate:Achha chal raha hai]. Let's build on this momentum! ⭐"
            },
            'compassionate': {
                'positive': "[translate:Bahut accha lag raha hai] seeing you happy. [translate:Yeh moment enjoy karo]. 💕",
                'negative': "[translate:Bohot tough lag raha hai na]? Your feelings are completely valid. [translate:Main yahaan hun]. 🤗",
                'neutral': "[translate:Theek hai], sometimes we just feel normal. That's okay too. 🌸"
            }
        }
        
        return responses.get(tone, responses['supportive']).get(sentiment, "Thanks for sharing. [translate:Main yahaan hun] for you. 💙")
