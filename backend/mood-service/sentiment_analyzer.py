from textblob import TextBlob

class SentimentAnalyzer:
    @staticmethod
    def analyze_text(text):
        """
        Analyze sentiment using TextBlob
        Returns: dict with sentiment classification
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'confidence': 'low'
            }
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Determine confidence based on absolute polarity
        confidence = 'high' if abs(polarity) > 0.5 else 'medium' if abs(polarity) > 0.2 else 'low'
        
        return {
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'confidence': confidence
        }
