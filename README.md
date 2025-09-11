🕉️ Eirene AI Wellness Platform
<div align="center">
A comprehensive AI-powered mental wellness ecosystem tailored for Indian youth, integrating creative therapy, proactive mood sensing, culturally aware AI counseling, and community support designed specifically for the cultural context of young Indians.

[
[
[
[
[
[
[
[
[
[
[
[

</div>
📋 Table of Contents
🌟 Platform Overview

🎯 Hackathon Challenge Solution

🚀 Core Features

🛠️ Technology Stack

📁 Project Structure

⚡ Installation & Setup

🎮 Usage Guide

💡 Innovation Highlights

🌐 Browser Support

🤝 Contributing

📄 License

🌟 Platform Overview
Eirene AI Wellness is a revolutionary mental health platform designed specifically to address the unique challenges faced by Indian youth. By combining cutting-edge AI technology with deep cultural understanding, the platform creates a safe, anonymous, and empowering space for emotional wellness and personal growth.

🎪 Key Mission:
Breaking the stigma around mental health in India while providing culturally-sensitive, accessible, and innovative support through AI-powered creative therapy, proactive mood monitoring, and community healing.

Full README documentation for Eirene AI Wellness
🎯 Hackathon Challenge Solution
Challenge: Mental health stigma and lack of accessible, culturally-aware mental wellness solutions for Indian youth.

Solution: Eirene leverages Google Cloud's generative AI to create an innovative ecosystem that:

🎨 Transforms emotions into creative expressions (art, music, stories)

🧠 Proactively detects emotional patterns before crisis

🇮🇳 Provides culturally-aware counseling in native languages

🤝 Enables anonymous peer support and community healing

🔒 Maintains complete privacy with zero-knowledge architecture

🚀 Core Features
🎨 1. Emotion Canvas Studio - Creative AI Therapy
AI Art Therapy: Personalized visual art generation based on emotional state

Mood Music Composer: Custom instrumental tracks matching current feelings

Visual Mood Journal: Transform emotions into visual stories and abstract art

Creative Expression Timeline: Track emotional healing through artistic creations

Collaborative Creation: Work with AI to create therapeutic content

🧠 2. Invisible Mood Sensing - Smart Detection Engine
Smart Text Analysis: Detects mood from casual typing patterns (WhatsApp-style)

Voice Emotion Reader: Analyzes tone, pace, pauses in voice notes

Behavioral Pattern Detection: Tracks app usage patterns to predict mental state

Early Warning System: Proactive alerts before emotional crisis hits

Continuous Monitoring: Background emotional health tracking

🇮🇳 3. Culturally-Aware AI Counselor
Family Pressure Navigator: Understanding of Indian family dynamics and career pressures

Cultural Therapy: Mental health guidance through Indian philosophy and meditation

Regional Language Support: Hindi, Tamil, Bengali, Telugu, Marathi with local slang

Festival/Season Awareness: Contextual understanding of cultural events impact

Academic Stress Management: Specialized support for Indian educational pressure

⚠️ 4. Emergency Intervention Engine
Crisis Radar: Detects suicidal thoughts and self-harm patterns from conversation

Instant Connect Protocol: One-click access to verified counselors and helplines

Smart Emergency Contacts: AI decides when to alert family/friends based on severity

Location-Based Resources: Find nearest mental health professionals and support groups

24/7 Crisis Support: Round-the-clock emergency response system

🎮 5. Gamified Wellness Journey
Mental Health Quest: Daily wellness challenges to build emotional strength

Stigma Buster Missions: Earn points by spreading awareness anonymously

Emotion Streaks: Track consecutive days of positive mental activities

Wellness Badges: Unlock achievements for resilience, creativity, helping others

Community Challenges: Group activities for collective healing

🔒 6. Invisible Privacy Mode
Zero-Knowledge Architecture: App works without storing personal details

Self-Destructing Data: All conversations auto-delete after specified time

Phantom Mode: Use app without creating accounts or leaving digital footprints

Encrypted Creative Vault: Military-grade encryption for all personal content

Anonymous Community: Connect with others without revealing identity

📈 7. Proactive Wellness Prediction
Mental Weather Forecast: Predicts tough emotional days based on patterns

Stress Storm Alerts: Warns about upcoming stressful periods (exams, interviews)

Preventive Care Suggestions: Recommends activities before emotional dip

Personalized Coping Toolkit: AI learns what works and suggests customized solutions

Trend Analysis: Long-term emotional health pattern recognition

🌍 8. Smart Resource Integration
Campus Mental Health Map: Find counselors and safe spaces in your college/school

Helpline Intelligence: Smart routing to most appropriate helpline

Professional Matching: AI matches with counselors understanding your background

Community Resource Discovery: Local support groups, workshops, healing events

Verified Provider Network: Trusted and culturally-aware mental health professionals

🗣️ 9. Multilingual Emotional Expression
Code-Switching Support: Understands mix of English-Hindi-regional languages

Cultural Metaphor Understanding: Recognizes Indian ways of expressing emotions

Local Slang Detection: Regional expressions of distress and happiness

Voice Note Comfort: Full voice support in native languages

Contextual Translation: Maintains emotional nuance across languages

🤝 10. Creative Collaboration Mode
Healing Through Creation: Work with AI to create music, poetry, art as therapy

Emotional Remix: Transform negative thoughts into positive creative content

Collaborative Storytelling: Co-write stories about overcoming challenges

Mind Map Visualization: AI helps visualize thoughts, feelings, solutions graphically

Peer Creative Projects: Anonymous collaboration on healing content

🛠️ Technology Stack
Frontend Architecture
javascript
HTML5 + CSS3 + Vanilla JavaScript ES6+
├── Modern CSS Grid/Flexbox (responsive design)
├── CSS Animations (smooth transitions) 
├── Web Audio API (voice recording & analysis)
├── Canvas API (mood visualizations & 3D OM)
├── Chart.js (analytics & progress tracking)
└── Local Storage (session management)
Backend Architecture
python
Flask (lightweight Python framework)
├── Flask-CORS (cross-origin API access)
├── Flask-SocketIO (real-time updates)
├── Requests (external API calls)
├── JSON handling (data management)
└── Google Cloud integration
AI/ML Integration
python
Google Cloud & AI Libraries:
├── google-cloud-language (sentiment analysis)
├── Gemini AI (creative content generation)
├── speech_recognition (voice processing)
├── librosa (audio analysis)
└── Pillow (image processing)
Database & Storage
text
Lightweight JSON Storage (hackathon optimized):
├── user_moods.json (mood history)
├── resources.json (counselor database)
├── generated_content.json (art/music prompts)
├── cultural_context.json (Indian context data)
└── Firebase (optional real-time sync)
📁 Project Structure
text
eirene-ai-wellness/
├── 📁 frontend/
│   ├── 📄 index.html              # Main dashboard
│   ├── 📄 dashboard.html          # Personal wellness dashboard
│   ├── 📄 creative-studio.html    # AI art/music generation
│   ├── 📄 mood-tracker.html       # Emotion tracking & analysis
│   ├── 📄 counselor.html          # AI counselor with 3D OM
│   ├── 📄 wellness-forecast.html  # Predictive wellness insights
│   ├── 📄 resources.html          # Local resource finder
│   ├── 📁 css/
│   │   ├── 📄 main.css           # Core styling
│   │   └── 📄 animations.css     # Smooth transitions
│   ├── 📁 js/
│   │   ├── 📄 app.js             # Main application logic
│   │   ├── 📄 moodDetection.js   # Client-side mood analysis
│   │   ├── 📄 creativeTool.js    # Art/music interface
│   │   └── 📄 voiceHandler.js    # Audio processing
│   └── 📁 assets/
│       ├── 📁 icons/             # App icons & favicons
│       └── 📁 sounds/            # Notification sounds
├── 📁 backend/
│   ├── 📄 app.py                 # Main Flask server
│   ├── 📄 mood_analyzer.py       # Sentiment analysis engine
│   ├── 📄 creative_engine.py     # GenAI content creation
│   ├── 📄 voice_processor.py     # Audio emotion detection
│   ├── 📄 resource_finder.py     # Local counselor matching
│   └── 📄 emergency_handler.py   # Crisis intervention
├── 📁 data/
│   ├── 📄 moods.json            # User mood data
│   ├── 📄 resources.json        # Help resources
│   └── 📄 cultural_context.json # Indian context data
├── 📄 requirements.txt           # Python dependencies
└── 📄 README.md                 # This documentation
⚡ Installation & Setup
🚀 Quick Start (5 minutes)
📥 Clone Repository

bash
git clone https://github.com/yourusername/eirene-ai-wellness.git
cd eirene-ai-wellness
🐍 Setup Python Environment

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
📦 Install Dependencies

bash
pip install -r requirements.txt
🔑 Configure API Keys

bash
# Create .env file
echo "GEMINI_API_KEY=your_actual_gemini_key" > .env
echo "OPENAI_API_KEY=your_actual_openai_key" >> .env
🚀 Launch Backend

bash
python backend/app.py
🌐 Open Frontend

text
Open frontend/index.html in your browser
Backend runs on: http://localhost:5000
🔐 API Configuration
python
# Required API Keys:
GEMINI_API_KEY    # Google Cloud Generative AI
OPENAI_API_KEY    # OpenAI for creative content
SPEECH_KEY        # Azure Speech Services (optional)
🎮 Usage Guide
🏁 Getting Started
🌍 Open Dashboard: Start with frontend/index.html

🎨 Create Art: Navigate to Creative Studio for AI art therapy

📊 Track Mood: Use Mood Tracker for emotion analysis

💬 Chat with AI: Access culturally-aware counselor

📈 View Forecast: Check wellness predictions

🆘 Get Resources: Find local mental health support

🎯 Feature Workflow
text
User Journey:
Dashboard → Mood Check → Creative Expression → AI Counseling → Resource Access
     ↓              ↓              ↓              ↓              ↓
Analytics → Pattern Detection → Therapy → Cultural Support → Crisis Help
💡 Innovation Highlights
🏆 Technical Uniqueness
Beyond Traditional Chatbots: Creative companion using art, music, stories

Proactive Intervention: Predicts and prevents crisis instead of just responding

Cultural Intelligence: Built specifically for Indian youth psychology

Privacy-First Design: Works without compromising user anonymity

Multi-Sensory Approach: Text, voice, visual, creative expression together

🎨 Creative AI Pipeline
python
Emotion Detection → Creative Prompt Generation → AI Content Creation → User Collaboration
🔒 Privacy Architecture
Zero server-side personal data storage

Client-side emotion processing

Encrypted communication channels

Self-destructing session data

🌐 Browser Support
Browser	Version	Frontend	Backend API	3D Graphics	Voice
Chrome	90+	✅	✅	✅	✅
Firefox	88+	✅	✅	✅	✅
Safari	14+	✅	✅	⚠️	✅
Edge	90+	✅	✅	✅	✅
🤝 Contributing
🎯 Development Guidelines
Fork & Clone

bash
git clone https://github.com/yourusername/eirene-ai-wellness.git
Create Feature Branch

bash
git checkout -b feature/amazing-feature
Follow Code Standards

Clean, modular JavaScript (ES6+)

Responsive CSS with custom properties

Well-documented Python with type hints

Cultural sensitivity in AI responses

Submit Pull Request

Clear description of changes

Include screenshots for UI changes

Test across different browsers

Maintain backwards compatibility

🐛 Reporting Issues
Use GitHub Issues with detailed reproduction steps

Include browser version, device info, and screenshots

Label appropriately (bug, enhancement, documentation)

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

<div align="center">
🕉️ Built with love for Indian youth mental wellness 💙

Empowering minds, nurturing creativity, fostering healing

</div>
