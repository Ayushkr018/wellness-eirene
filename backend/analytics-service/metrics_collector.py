from datetime import datetime, timedelta
from shared.db_config import get_db
import logging

class MetricsCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_user_action(self, user_id, action_type, metadata=None):
        """Log user actions for analytics"""
        try:
            db = get_db()
            
            action_log = {
                'user_id': user_id,
                'action_type': action_type,  # mood_checkin, ai_interaction, voice_analysis, etc.
                'timestamp': datetime.utcnow(),
                'metadata': metadata or {}
            }
            
            db.user_actions.insert_one(action_log)
            self.logger.info(f"Logged action: {action_type} for user: {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to log action: {str(e)}")
    
    def get_user_engagement_metrics(self, user_id, days=30):
        """Get user engagement metrics for the last N days"""
        try:
            db = get_db()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get mood check-ins
            mood_checkins = db.mood_entries.count_documents({
                'user_id': user_id,
                'timestamp': {'$gte': start_date}
            })
            
            # Get AI interactions
            ai_interactions = db.user_actions.count_documents({
                'user_id': user_id,
                'action_type': 'ai_interaction',
                'timestamp': {'$gte': start_date}
            })
            
            # Get voice analyses
            voice_analyses = db.user_actions.count_documents({
                'user_id': user_id,
                'action_type': 'voice_analysis',
                'timestamp': {'$gte': start_date}
            })
            
            # Get creative therapy interactions
            therapy_interactions = db.user_actions.count_documents({
                'user_id': user_id,
                'action_type': 'creative_therapy',
                'timestamp': {'$gte': start_date}
            })
            
            # Calculate engagement frequency
            total_interactions = mood_checkins + ai_interactions + voice_analyses + therapy_interactions
            avg_daily_interactions = total_interactions / days if days > 0 else 0
            
            # Get mood trend
            mood_trend = self._calculate_mood_trend(user_id, days)
            
            return {
                'period_days': days,
                'mood_checkins': mood_checkins,
                'ai_interactions': ai_interactions,
                'voice_analyses': voice_analyses,
                'therapy_interactions': therapy_interactions,
                'total_interactions': total_interactions,
                'avg_daily_interactions': round(avg_daily_interactions, 2),
                'mood_trend': mood_trend,
                'engagement_level': self._classify_engagement(avg_daily_interactions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get engagement metrics: {str(e)}")
            return None
    
    def _calculate_mood_trend(self, user_id, days):
        """Calculate mood improvement trend"""
        try:
            db = get_db()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get mood entries sorted by date
            mood_entries = list(db.mood_entries.find({
                'user_id': user_id,
                'timestamp': {'$gte': start_date}
            }).sort('timestamp', 1))
            
            if len(mood_entries) < 2:
                return {'trend': 'insufficient_data', 'change': 0}
            
            # Calculate average sentiment for first and last half
            mid_point = len(mood_entries) // 2
            first_half = mood_entries[:mid_point]
            second_half = mood_entries[mid_point:]
            
            first_avg = sum(entry['sentiment_analysis']['polarity'] for entry in first_half) / len(first_half)
            second_avg = sum(entry['sentiment_analysis']['polarity'] for entry in second_half) / len(second_half)
            
            change = second_avg - first_avg
            
            if change > 0.1:
                trend = 'improving'
            elif change < -0.1:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'trend': trend,
                'change': round(change, 3),
                'first_half_avg': round(first_avg, 3),
                'second_half_avg': round(second_avg, 3)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate mood trend: {str(e)}")
            return {'trend': 'error', 'change': 0}
    
    def _classify_engagement(self, avg_daily_interactions):
        """Classify user engagement level"""
        if avg_daily_interactions >= 2:
            return 'high'
        elif avg_daily_interactions >= 1:
            return 'medium'
        elif avg_daily_interactions >= 0.5:
            return 'low'
        else:
            return 'very_low'
    
    def get_platform_analytics(self, days=30):
        """Get overall platform analytics"""
        try:
            db = get_db()
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total users
            total_users = db.users.count_documents({})
            
            # Active users (users who had any interaction in the period)
            active_users = db.user_actions.distinct('user_id', {
                'timestamp': {'$gte': start_date}
            })
            active_user_count = len(active_users)
            
            # Total interactions
            total_interactions = db.user_actions.count_documents({
                'timestamp': {'$gte': start_date}
            })
            
            # Most popular features
            feature_usage = list(db.user_actions.aggregate([
                {'$match': {'timestamp': {'$gte': start_date}}},
                {'$group': {'_id': '$action_type', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]))
            
            # Daily active users trend
            daily_active = list(db.user_actions.aggregate([
                {'$match': {'timestamp': {'$gte': start_date}}},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                    'unique_users': {'$addToSet': '$user_id'}
                }},
                {'$project': {
                    'date': '$_id',
                    'active_users': {'$size': '$unique_users'}
                }},
                {'$sort': {'date': 1}}
            ]))
            
            return {
                'period_days': days,
                'total_users': total_users,
                'active_users': active_user_count,
                'user_retention_rate': round((active_user_count / total_users * 100), 2) if total_users > 0 else 0,
                'total_interactions': total_interactions,
                'avg_interactions_per_active_user': round(total_interactions / active_user_count, 2) if active_user_count > 0 else 0,
                'feature_usage': feature_usage,
                'daily_active_users': daily_active
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform analytics: {str(e)}")
            return None
