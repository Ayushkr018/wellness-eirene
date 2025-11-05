import re
from datetime import datetime, timedelta
from shared.db_config import get_db
import logging

logger = logging.getLogger(__name__)

class RiskDetector:
    """Detect emotional crisis and risk levels"""
    
    def __init__(self):
        # Crisis keywords (configurable)
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'no reason to live',
            'want to die', 'better off dead', 'cant go on', 'ending my life',
            'self harm', 'hurt myself', 'overdose', 'jump off', 'hang myself'
        ]
        
        # High-risk indicators
        self.high_risk_keywords = [
            'hopeless', 'worthless', 'burden', 'give up', 'cant take it',
            'too much pain', 'unbearable', 'escape', 'numb', 'empty inside'
        ]
        
        self.crisis_threshold = float(os.getenv('CRISIS_THRESHOLD', 0.8))
    
    def detect_crisis_keywords(self, text):
        """Check for explicit crisis keywords"""
        if not text:
            return False, []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def calculate_risk_score(self, mood_data, user_history=None):
        """Calculate comprehensive risk score (0-1)"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # 1. Check crisis keywords (highest weight)
            has_crisis, crisis_keywords = self.detect_crisis_keywords(
                mood_data.get('mood_text', '')
            )
            if has_crisis:
                risk_score += 0.6
                risk_factors.append({
                    'factor': 'crisis_keywords',
                    'severity': 'critical',
                    'keywords': crisis_keywords
                })
            
            # 2. Check sentiment polarity
            sentiment = mood_data.get('sentiment_analysis', {})
            polarity = sentiment.get('polarity', 0)
            if polarity < -0.7:
                risk_score += 0.2
                risk_factors.append({
                    'factor': 'extreme_negative_sentiment',
                    'severity': 'high',
                    'polarity': polarity
                })
            elif polarity < -0.4:
                risk_score += 0.1
                risk_factors.append({
                    'factor': 'negative_sentiment',
                    'severity': 'medium',
                    'polarity': polarity
                })
            
            # 3. Check voice emotion (if available)
            voice_emotion = mood_data.get('voice_emotion', {})
            if voice_emotion:
                sad_prob = voice_emotion.get('probabilities', {}).get('sad', 0)
                stressed_prob = voice_emotion.get('probabilities', {}).get('stressed', 0)
                if sad_prob > 0.7 or stressed_prob > 0.7:
                    risk_score += 0.15
                    risk_factors.append({
                        'factor': 'distressed_voice',
                        'severity': 'high',
                        'emotion': voice_emotion.get('emotion')
                    })
            
            # 4. Check historical trend
            if user_history:
                trend = user_history.get('mood_trend', 'stable')
                if trend == 'declining':
                    risk_score += 0.1
                    risk_factors.append({
                        'factor': 'declining_trend',
                        'severity': 'medium'
                    })
                
                # Check for prolonged negative moods
                recent_moods = user_history.get('recent_moods', [])
                negative_count = sum(1 for m in recent_moods[:7] 
                                   if m.get('sentiment') == 'negative')
                if negative_count >= 5:
                    risk_score += 0.15
                    risk_factors.append({
                        'factor': 'prolonged_distress',
                        'severity': 'high',
                        'negative_days': negative_count
                    })
            
            # 5. Check high-risk keywords
            text_lower = mood_data.get('mood_text', '').lower()
            high_risk_found = [k for k in self.high_risk_keywords if k in text_lower]
            if len(high_risk_found) >= 2:
                risk_score += 0.1
                risk_factors.append({
                    'factor': 'high_risk_language',
                    'severity': 'medium',
                    'keywords': high_risk_found
                })
            
            # Cap at 1.0
            risk_score = min(1.0, risk_score)
            
            # Determine risk level
            if risk_score >= self.crisis_threshold:
                risk_level = 'CRISIS'
            elif risk_score >= 0.6:
                risk_level = 'HIGH'
            elif risk_score >= 0.4:
                risk_level = 'MEDIUM'
            elif risk_score >= 0.2:
                risk_level = 'LOW'
            else:
                risk_level = 'MINIMAL'
            
            return {
                'risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'crisis_detected': has_crisis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk calculation failed: {str(e)}")
            return {
                'risk_score': 0.0,
                'risk_level': 'UNKNOWN',
                'error': str(e)
            }
