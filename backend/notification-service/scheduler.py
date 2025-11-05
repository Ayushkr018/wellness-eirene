import schedule
import time
from datetime import datetime, timedelta
import threading
from shared.db_config import get_db
from email_sender import EmailSender
import logging

class NotificationScheduler:
    def __init__(self):
        self.email_sender = EmailSender()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    def start_scheduler(self):
        """Start the notification scheduler"""
        self.running = True
        
        # Schedule daily reminders
        schedule.every().day.at("09:00").do(self.send_daily_reminders)
        schedule.every().day.at("20:00").do(self.send_evening_checkins)
        
        # Schedule weekly motivational messages
        schedule.every().monday.at("10:00").do(self.send_weekly_motivation)
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        self.logger.info("Notification scheduler started")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def send_daily_reminders(self):
        """Send daily check-in reminders to active users"""
        try:
            db = get_db()
            
            # Get users who have notifications enabled and last checked in within 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            users = db.users.find({
                'notification_preferences.daily_reminders': True,
                'last_activity': {'$gte': cutoff_date}
            })
            
            sent_count = 0
            for user in users:
                # Check if user hasn't checked in today
                today = datetime.utcnow().date()
                last_checkin = db.mood_entries.find_one(
                    {'user_id': user['_id']},
                    sort=[('timestamp', -1)]
                )
                
                if not last_checkin or last_checkin['timestamp'].date() < today:
                    if self.email_sender.send_daily_reminder(user['email'], user.get('name', '')):
                        sent_count += 1
            
            self.logger.info(f"Sent daily reminders to {sent_count} users")
            
        except Exception as e:
            self.logger.error(f"Failed to send daily reminders: {str(e)}")
    
    def send_evening_checkins(self):
        """Send evening check-in reminders"""
        try:
            db = get_db()
            
            # Get users who prefer evening reminders
            users = db.users.find({
                'notification_preferences.evening_reminders': True
            })
            
            sent_count = 0
            for user in users:
                # Check if user hasn't checked in today
                today = datetime.utcnow().date()
                last_checkin = db.mood_entries.find_one(
                    {'user_id': user['_id']},
                    sort=[('timestamp', -1)]
                )
                
                if not last_checkin or last_checkin['timestamp'].date() < today:
                    if self.email_sender.send_daily_reminder(user['email'], user.get('name', '')):
                        sent_count += 1
            
            self.logger.info(f"Sent evening reminders to {sent_count} users")
            
        except Exception as e:
            self.logger.error(f"Failed to send evening reminders: {str(e)}")
    
    def send_weekly_motivation(self):
        """Send weekly motivational messages"""
        try:
            db = get_db()
            
            users = db.users.find({
                'notification_preferences.motivational_messages': True
            })
            
            sent_count = 0
            for user in users:
                # Get user's recent activity to personalize message
                recent_entries = list(db.mood_entries.find(
                    {'user_id': user['_id']},
                    sort=[('timestamp', -1)],
                    limit=7
                ))
                
                if len(recent_entries) >= 3:
                    message_type = 'streak'
                elif len(recent_entries) == 0:
                    message_type = 'missed'
                else:
                    message_type = 'general'
                
                if self.email_sender.send_motivational_nudge(
                    user['email'], 
                    user.get('name', ''), 
                    message_type
                ):
                    sent_count += 1
            
            self.logger.info(f"Sent weekly motivation to {sent_count} users")
            
        except Exception as e:
            self.logger.error(f"Failed to send weekly motivation: {str(e)}")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        self.logger.info("Notification scheduler stopped")
