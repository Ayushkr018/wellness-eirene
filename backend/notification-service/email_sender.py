import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.email = os.getenv('SMTP_EMAIL')
        self.password = os.getenv('SMTP_PASSWORD')
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, body, is_html=False):
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_daily_reminder(self, user_email, user_name=""):
        """Send daily check-in reminder"""
        subject = "🌻 Daily Check-in - How are you feeling today?"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Namaste {user_name}! 🙏</h2>
                
                <p>Hope aap ka din achha ja raha hai! It's time for your daily mood check-in.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                    <p><strong>Today's gentle reminder:</strong></p>
                    <p>"Har din ek nayi shururat hai. Take a moment to breathe and check in with yourself." ✨</p>
                </div>
                
                <p>Take 2 minutes to:</p>
                <ul>
                    <li>Share how you're feeling today</li>
                    <li>Get personalized support from your AI counselor</li>
                    <li>Try some creative therapy if you're up for it</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.getenv('APP_URL', 'http://localhost:5000')}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Check In Now
                    </a>
                </div>
                
                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    Eirene - Your AI Mental Wellness Companion<br>
                    You can update your notification preferences anytime in the app.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, is_html=True)
    
    def send_motivational_nudge(self, user_email, user_name="", message_type="general"):
        """Send motivational nudges"""
        messages = {
            'general': "Remember, progress > perfection. You're doing better than you think! 💪",
            'streak': "You've been consistent with your check-ins. Keep it up! 🔥",
            'missed': "We missed you! Your mental health journey matters. Come back when you're ready. 💙",
            'celebration': "You've been taking care of your mental health - that's worth celebrating! 🎉"
        }
        
        subject = "💙 A little motivation from Eirene"
        message = messages.get(message_type, messages['general'])
        
        body = f"""
        Hi {user_name}! 👋
        
        {message}
        
        Your mental wellness journey is unique and valuable. Keep going, one day at a time.
        
        With care,
        Team Eirene ✨
        """
        
        return self.send_email(user_email, subject, body)
