from datetime import datetime, timedelta
from shared.db_config import get_db
import logging

logger = logging.getLogger(__name__)

class StreakTracker:
    """Track wellness streaks and engagement"""
    
    def __init__(self):
        self.db = get_db()
    
    def update_streak(self, user_id):
        """Update user's check-in streak"""
        try:
            user_progress = self.db.user_progress.find_one({'user_id': user_id})
            
            if not user_progress:
                # Initialize progress
                user_progress = {
                    'user_id': user_id,
                    'current_streak': 1,
                    'longest_streak': 1,
                    'total_checkins': 1,
                    'last_checkin': datetime.utcnow(),
                    'streak_history': [],
                    'badges': [],
                    'points': 10
                }
                self.db.user_progress.insert_one(user_progress)
                return user_progress
            
            # Calculate streak
            last_checkin = user_progress['last_checkin']
            now = datetime.utcnow()
            days_diff = (now.date() - last_checkin.date()).days
            
            if days_diff == 0:
                # Same day, no streak change
                return user_progress
            elif days_diff == 1:
                # Consecutive day
                current_streak = user_progress['current_streak'] + 1
                points_earned = 10 + (current_streak // 7) * 5  # Bonus every week
            else:
                # Streak broken
                # Log previous streak
                if user_progress['current_streak'] > 1:
                    self.db.user_progress.update_one(
                        {'user_id': user_id},
                        {
                            '$push': {
                                'streak_history': {
                                    'streak_length': user_progress['current_streak'],
                                    'ended_at': last_checkin
                                }
                            }
                        }
                    )
                current_streak = 1
                points_earned = 10
            
            # Check for new badges
            new_badges = self._check_badges(current_streak, user_progress)
            
            # Update progress
            update_data = {
                'current_streak': current_streak,
                'longest_streak': max(current_streak, user_progress.get('longest_streak', 0)),
                'total_checkins': user_progress.get('total_checkins', 0) + 1,
                'last_checkin': now,
                'points': user_progress.get('points', 0) + points_earned
            }
            
            if new_badges:
                update_data['$addToSet'] = {'badges': {'$each': new_badges}}
            
            self.db.user_progress.update_one(
                {'user_id': user_id},
                {'$set': update_data}
            )
            
            # Fetch updated progress
            updated_progress = self.db.user_progress.find_one({'user_id': user_id})
            updated_progress['points_earned'] = points_earned
            updated_progress['new_badges'] = new_badges
            
            return updated_progress
            
        except Exception as e:
            logger.error(f"Streak update failed: {str(e)}")
            return None
    
    def _check_badges(self, current_streak, user_progress):
        """Check for new badge achievements"""
        new_badges = []
        existing_badges = [b['badge_id'] for b in user_progress.get('badges', [])]
        
        # Streak badges
        streak_badges = [
            {'badge_id': 'week_warrior', 'name': 'Week Warrior', 'requirement': 7},
            {'badge_id': 'month_master', 'name': 'Month Master', 'requirement': 30},
            {'badge_id': 'quarter_champion', 'name': 'Quarter Champion', 'requirement': 90}
        ]
        
        for badge in streak_badges:
            if current_streak >= badge['requirement'] and badge['badge_id'] not in existing_badges:
                new_badges.append({
                    'badge_id': badge['badge_id'],
                    'name': badge['name'],
                    'earned_at': datetime.utcnow(),
                    'description': f"Maintained {badge['requirement']} day streak"
                })
        
        # Milestone badges
        total_checkins = user_progress.get('total_checkins', 0) + 1
        milestone_badges = [
            {'badge_id': 'first_step', 'name': 'First Step', 'requirement': 1},
            {'badge_id': 'dedicated_user', 'name': 'Dedicated User', 'requirement': 50},
            {'badge_id': 'wellness_champion', 'name': 'Wellness Champion', 'requirement': 100}
        ]
        
        for badge in milestone_badges:
            if total_checkins >= badge['requirement'] and badge['badge_id'] not in existing_badges:
                new_badges.append({
                    'badge_id': badge['badge_id'],
                    'name': badge['name'],
                    'earned_at': datetime.utcnow(),
                    'description': f"Completed {badge['requirement']} check-ins"
                })
        
        return new_badges
    
    def get_progress(self, user_id):
        """Get user's progress"""
        try:
            progress = self.db.user_progress.find_one({'user_id': user_id})
            
            if not progress:
                return {
                    'current_streak': 0,
                    'longest_streak': 0,
                    'total_checkins': 0,
                    'points': 0,
                    'badges': [],
                    'level': 1
                }
            
            # Calculate level
            points = progress.get('points', 0)
            level = (points // 100) + 1  # Level up every 100 points
            
            return {
                'current_streak': progress.get('current_streak', 0),
                'longest_streak': progress.get('longest_streak', 0),
                'total_checkins': progress.get('total_checkins', 0),
                'points': points,
                'level': level,
                'badges': progress.get('badges', []),
                'next_level_points': level * 100
            }
            
        except Exception as e:
            logger.error(f"Progress fetch failed: {str(e)}")
            return None
