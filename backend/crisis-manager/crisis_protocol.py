import requests
import os
from datetime import datetime
from shared.db_config import get_db
import logging

logger = logging.getLogger(__name__)

class CrisisProtocol:
    """Automated crisis response protocol"""
    
    def __init__(self):
        self.auto_trigger = os.getenv('AUTO_TRIGGER_RESOURCES', 'true').lower() == 'true'
        self.resource_finder_url = os.getenv('RESOURCE_FINDER_URL')
        self.notification_url = os.getenv('NOTIFICATION_SERVICE_URL')
    
    def trigger_crisis_response(self, user_id, risk_assessment, mood_data, token):
        """Execute crisis management protocol"""
        try:
            response_actions = []
            
            # 1. Log crisis event
            crisis_log = self._log_crisis_event(user_id, risk_assessment, mood_data)
            response_actions.append({
                'action': 'crisis_logged',
                'log_id': str(crisis_log),
                'status': 'success'
            })
            
            # 2. Fetch emergency resources
            if self.auto_trigger:
                resources = self._fetch_emergency_resources(user_id, token)
                response_actions.append({
                    'action': 'resources_fetched',
                    'resources': resources,
                    'status': 'success'
                })
            
            # 3. Send crisis notification
            notification_result = self._send_crisis_notification(user_id, resources, token)
            response_actions.append({
                'action': 'notification_sent',
                'result': notification_result,
                'status': 'success' if notification_result else 'failed'
            })
            
            # 4. Generate immediate support message
            support_message = self._generate_crisis_message(risk_assessment)
            response_actions.append({
                'action': 'support_message_generated',
                'message': support_message,
                'status': 'success'
            })
            
            # 5. Flag user for priority support
            self._flag_user_priority(user_id, risk_assessment)
            response_actions.append({
                'action': 'user_flagged_priority',
                'status': 'success'
            })
            
            return {
                'protocol_triggered': True,
                'risk_level': risk_assessment['risk_level'],
                'actions_taken': response_actions,
                'emergency_resources': resources if self.auto_trigger else None,
                'support_message': support_message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Crisis protocol failed: {str(e)}")
            return {
                'protocol_triggered': False,
                'error': str(e)
            }
    
    def _log_crisis_event(self, user_id, risk_assessment, mood_data):
        """Log crisis event securely"""
        try:
            db = get_db()
            
            crisis_log = {
                'user_id': user_id,  # Keep for internal tracking
                'risk_assessment': risk_assessment,
                'mood_snapshot': {
                    'sentiment': mood_data.get('sentiment_analysis', {}).get('sentiment'),
                    'polarity': mood_data.get('sentiment_analysis', {}).get('polarity'),
                    'text_preview': mood_data.get('mood_text', '')[:100] if mood_data.get('mood_text') else None
                },
                'timestamp': datetime.utcnow(),
                'protocol_version': '1.0',
                'status': 'active'
            }
            
            result = db.crisis_logs.insert_one(crisis_log)
            logger.warning(f"CRISIS EVENT LOGGED - User: {user_id}, Risk: {risk_assessment['risk_level']}")
            
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Crisis logging failed: {str(e)}")
            return None
    
    def _fetch_emergency_resources(self, user_id, token):
        """Fetch emergency helplines and resources"""
        try:
            # Get user location if available
            db = get_db()
            user = db.users.find_one({'_id': user_id})
            region = user.get('region', 'IN-DELHI')  # Default to Delhi
            
            # Call resource finder
            response = requests.get(
                f"{self.resource_finder_url}/get-resources",
                params={'region': region, 'level': 'crisis'},
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('resources', [])
            else:
                logger.error(f"Resource fetch failed: {response.status_code}")
                return self._get_fallback_resources()
                
        except Exception as e:
            logger.error(f"Emergency resource fetch failed: {str(e)}")
            return self._get_fallback_resources()
    
    def _get_fallback_resources(self):
        """Fallback emergency resources"""
        return [
            {
                'name': 'National Suicide Prevention Helpline',
                'phone': '+91-9152987821',
                'available': '24/7',
                'language': 'English, Hindi'
            },
            {
                'name': 'AASRA',
                'phone': '+91-22-27546669',
                'available': '24/7',
                'language': 'English, Hindi'
            },
            {
                'name': 'Vandrevala Foundation',
                'phone': '1860-2662-345',
                'available': '24/7',
                'language': 'English, Hindi, Multiple'
            }
        ]
    
    def _send_crisis_notification(self, user_id, resources, token):
        """Send emergency notification"""
        try:
            # Get user contact
            db = get_db()
            user = db.users.find_one({'_id': user_id})
            
            notification_data = {
                'type': 'crisis_alert',
                'priority': 'urgent',
                'user_email': user.get('email'),
                'resources': resources,
                'message': 'We detected you might be in distress. Please reach out to these helplines immediately.'
            }
            
            response = requests.post(
                f"{self.notification_url}/send-crisis-alert",
                json=notification_data,
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Crisis notification failed: {str(e)}")
            return False
    
    def _generate_crisis_message(self, risk_assessment):
        """Generate immediate crisis support message"""
        if risk_assessment['crisis_detected']:
            return """
🚨 I'm really concerned about you right now. You're not alone, and help is available immediately.

**Please reach out to:**
- National Suicide Prevention: +91-9152987821 (24/7)
- AASRA: +91-22-27546669 (24/7)

These are trained professionals who want to help. Your life matters. 💙

If you're in immediate danger, please call emergency services: 112
"""
        else:
            return """
I can sense you're going through a really difficult time. Your feelings are valid, and you don't have to face this alone.

**Support is available:**
- Talk to someone you trust
- Contact helplines: +91-9152987821 (24/7)
- Consider professional support

Remember: [translate:Yeh waqt bhi guzar jayega]. You matter, and there are people who care. 💙
"""
    
    def _flag_user_priority(self, user_id, risk_assessment):
        """Flag user for priority human intervention"""
        try:
            db = get_db()
            db.users.update_one(
                {'_id': user_id},
                {
                    '$set': {
                        'priority_support': True,
                        'risk_level': risk_assessment['risk_level'],
                        'last_risk_assessment': datetime.utcnow()
                    }
                }
            )
            logger.warning(f"User {user_id} flagged for priority support")
            
        except Exception as e:
            logger.error(f"Priority flagging failed: {str(e)}")
