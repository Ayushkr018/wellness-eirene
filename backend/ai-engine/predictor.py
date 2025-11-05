from prophet import Prophet
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from shared.db_config import get_db
from shared.redis_config import redis_cache
import logging

logger = logging.getLogger(__name__)

class WellnessPredictor:
    """Time-series prediction for mood/wellness trends using Prophet"""
    
    def __init__(self):
        self.min_history = int(os.getenv('MIN_HISTORY_FOR_PREDICTION', 7))
        self.prediction_horizon = int(os.getenv('PREDICTION_HORIZON_DAYS', 7))
    
    def prepare_data(self, user_id):
        """Prepare historical mood data for Prophet"""
        try:
            db = get_db()
            
            # Get user's mood history
            mood_entries = list(db.mood_entries.find(
                {'user_id': user_id}
            ).sort('timestamp', 1))
            
            if len(mood_entries) < self.min_history:
                logger.info(f"Insufficient history for user {user_id}: {len(mood_entries)} entries")
                return None
            
            # Convert to DataFrame
            data = []
            for entry in mood_entries:
                # Convert sentiment to numeric score
                sentiment = entry.get('sentiment_analysis', {})
                polarity = sentiment.get('polarity', 0)
                
                # Handle voice emotion if present
                if 'voice_emotion' in entry:
                    voice_probs = entry['voice_emotion'].get('probabilities', {})
                    # Weight voice emotions
                    voice_score = (
                        voice_probs.get('happy', 0) * 1 +
                        voice_probs.get('neutral', 0) * 0 +
                        voice_probs.get('sad', 0) * (-1) +
                        voice_probs.get('stressed', 0) * (-0.8)
                    )
                    # Average with text polarity
                    polarity = (polarity + voice_score) / 2
                
                data.append({
                    'ds': entry['timestamp'],
                    'y': polarity  # Wellness score (-1 to 1)
                })
            
            df = pd.DataFrame(data)
            
            # Ensure datetime format
            df['ds'] = pd.to_datetime(df['ds'])
            
            return df
            
        except Exception as e:
            logger.error(f"Data preparation failed: {str(e)}")
            return None
    
    def train_and_predict(self, user_id):
        """Train Prophet model and make predictions"""
        try:
            # Check cache first
            cached_prediction = redis_cache.get_prediction(user_id)
            if cached_prediction:
                logger.info(f"Using cached prediction for user {user_id}")
                return cached_prediction
            
            # Prepare data
            df = self.prepare_data(user_id)
            if df is None:
                return {
                    'success': False,
                    'error': 'Insufficient historical data',
                    'min_required': self.min_history
                }
            
            # Train Prophet model
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            model.fit(df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=self.prediction_horizon)
            forecast = model.predict(future)
            
            # Extract predictions
            predictions = []
            for i in range(len(df), len(forecast)):
                pred_date = forecast['ds'].iloc[i]
                pred_value = forecast['yhat'].iloc[i]
                pred_lower = forecast['yhat_lower'].iloc[i]
                pred_upper = forecast['yhat_upper'].iloc[i]
                
                # Calculate stress probability
                stress_prob = max(0, min(1, (1 - pred_value) / 2))  # Convert to 0-1 scale
                
                # Classify wellness level
                if pred_value > 0.3:
                    wellness_level = 'positive'
                elif pred_value > -0.1:
                    wellness_level = 'stable'
                elif pred_value > -0.5:
                    wellness_level = 'declining'
                else:
                    wellness_level = 'concerning'
                
                predictions.append({
                    'date': pred_date.isoformat(),
                    'wellness_score': round(float(pred_value), 3),
                    'confidence_lower': round(float(pred_lower), 3),
                    'confidence_upper': round(float(pred_upper), 3),
                    'stress_probability': round(stress_prob, 3),
                    'wellness_level': wellness_level
                })
            
            # Calculate trend
            recent_avg = df['y'].tail(7).mean()
            predicted_avg = np.mean([p['wellness_score'] for p in predictions])
            trend = 'improving' if predicted_avg > recent_avg + 0.1 else 'declining' if predicted_avg < recent_avg - 0.1 else 'stable'
            
            result = {
                'success': True,
                'user_id': user_id,
                'predictions': predictions,
                'trend': trend,
                'current_wellness': round(float(df['y'].iloc[-1]), 3),
                'predicted_avg': round(float(predicted_avg), 3),
                'generated_at': datetime.utcnow().isoformat(),
                'data_points_used': len(df)
            }
            
            # Cache prediction
            redis_cache.set_prediction(user_id, result)
            
            # Save to database
            db = get_db()
            db.wellness_predictions.insert_one({
                **result,
                'timestamp': datetime.utcnow()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_proactive_suggestions(self, prediction):
        """Generate proactive suggestions based on predictions"""
        try:
            if not prediction.get('success'):
                return []
            
            suggestions = []
            predictions = prediction.get('predictions', [])
            trend = prediction.get('trend', 'stable')
            
            # Check for concerning patterns
            concerning_days = [p for p in predictions if p['wellness_level'] in ['declining', 'concerning']]
            
            if len(concerning_days) >= 3:
                suggestions.append({
                    'type': 'preventive_alert',
                    'priority': 'high',
                    'message': 'Your wellness forecast shows some challenging days ahead. [translate:Thoda apna khayal rakhna]. Consider scheduling some self-care time.',
                    'actions': ['Schedule therapy', 'Practice mindfulness', 'Connect with support']
                })
            
            if trend == 'declining':
                suggestions.append({
                    'type': 'trend_alert',
                    'priority': 'medium',
                    'message': 'Your overall wellness trend is declining. [translate:Chalo kuch positive karte hain]. Let\'s work on turning this around together.',
                    'actions': ['Review coping strategies', 'Increase social connections', 'Try creative therapy']
                })
            
            # Check for high stress probability
            high_stress_days = [p for p in predictions if p['stress_probability'] > 0.7]
            if high_stress_days:
                stress_date = high_stress_days[0]['date']
                suggestions.append({
                    'type': 'stress_warning',
                    'priority': 'medium',
                    'message': f'High stress predicted around {stress_date[:10]}. [translate:Pehle se taiyaar raho]. Plan some stress-relief activities.',
                    'actions': ['Practice breathing exercises', 'Plan breaks', 'Prepare support network']
                })
            
            if trend == 'improving':
                suggestions.append({
                    'type': 'positive_reinforcement',
                    'priority': 'low',
                    'message': 'Great news! Your wellness trend is improving! [translate:Bahut accha chal raha hai]. Keep up the good work!',
                    'actions': ['Continue current practices', 'Share your success', 'Set new goals']
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {str(e)}")
            return []
