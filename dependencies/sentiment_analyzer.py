"""
Real Sentiment Analysis Module for CryptSIST Social Agent
Menggunakan VADER, TextBlob, dan Transformers untuk analisis sentimen cryptocurrency
"""

import os
import re
import json
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import logging

# Sentiment Analysis Libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# Optional transformers (will fallback if not available)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoSentimentAnalyzer:
    """
    Comprehensive Sentiment Analysis untuk cryptocurrency menggunakan multiple models
    """
    
    def __init__(self):
        """Initialize all sentiment analysis models"""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize transformer model for financial sentiment (optional)
        self.finbert_available = False
        if TRANSFORMERS_AVAILABLE:
            try:
                self.finbert_analyzer = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                self.finbert_available = True
                logger.info("✅ FinBERT model loaded successfully")
            except Exception as e:
                self.finbert_available = False
                logger.warning(f"⚠️ FinBERT not available: {e}")
        else:
            logger.info("📦 Transformers library not available, using VADER + TextBlob only")
        
        # Crypto-specific keywords for sentiment weighting
        self.crypto_keywords = {
            'positive': [
                'moon', 'bullish', 'hodl', 'pump', 'rally', 'breakout', 'surge',
                'adoption', 'partnership', 'launch', 'upgrade', 'integration',
                'institutional', 'massive', 'breakthrough', 'all-time high', 'ath'
            ],
            'negative': [
                'dump', 'crash', 'bearish', 'sell', 'panic', 'correction', 'decline',
                'regulation', 'ban', 'hack', 'scam', 'bubble', 'overvalued',
                'manipulation', 'whale dump', 'bear market'
            ],
            'neutral': [
                'analysis', 'prediction', 'forecast', 'trend', 'consolidation',
                'sideways', 'resistance', 'support', 'technical'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep crypto symbols
        text = re.sub(r'[^\w\s#$@]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_with_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # Classify sentiment
            if scores['compound'] >= 0.05:
                sentiment = 'Positif'
            elif scores['compound'] <= -0.05:
                sentiment = 'Negatif'
            else:
                sentiment = 'Netral'
            
            return {
                'sentiment': sentiment,
                'confidence': abs(scores['compound']),
                'scores': scores
            }
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            return {'sentiment': 'Netral', 'confidence': 0.5, 'scores': {}}
    
    def analyze_with_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'Positif'
            elif polarity < -0.1:
                sentiment = 'Negatif'
            else:
                sentiment = 'Netral'
            
            return {
                'sentiment': sentiment,
                'confidence': abs(polarity),
                'polarity': polarity,
                'subjectivity': subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
            return {'sentiment': 'Netral', 'confidence': 0.5}
    
    def analyze_with_finbert(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using FinBERT transformer model"""
        if not self.finbert_available:
            return {'sentiment': 'Netral', 'confidence': 0.5}
        
        try:
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            result = self.finbert_analyzer(text)[0]
            
            # Map FinBERT labels to Indonesian
            label_map = {
                'positive': 'Positif',
                'negative': 'Negatif',
                'neutral': 'Netral'
            }
            
            sentiment = label_map.get(result['label'].lower(), 'Netral')
            
            return {
                'sentiment': sentiment,
                'confidence': result['score'],
                'raw_result': result
            }
        except Exception as e:
            logger.error(f"FinBERT analysis error: {e}")
            return {'sentiment': 'Netral', 'confidence': 0.5}
    
    def calculate_crypto_keywords_weight(self, text: str) -> Dict[str, float]:
        """Calculate sentiment weight based on crypto-specific keywords"""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.crypto_keywords['positive'] if keyword in text_lower)
        negative_count = sum(1 for keyword in self.crypto_keywords['negative'] if keyword in text_lower)
        neutral_count = sum(1 for keyword in self.crypto_keywords['neutral'] if keyword in text_lower)
        
        total_keywords = positive_count + negative_count + neutral_count
        
        if total_keywords == 0:
            return {'weight': 0, 'crypto_relevance': 0}
        
        # Calculate crypto relevance score
        crypto_relevance = min(total_keywords / 10, 1.0)  # Max 1.0
        
        # Calculate sentiment weight
        if positive_count > negative_count:
            weight = 0.1 + (positive_count / total_keywords) * 0.3
        elif negative_count > positive_count:
            weight = -0.1 - (negative_count / total_keywords) * 0.3
        else:
            weight = 0
        
        return {
            'weight': weight,
            'crypto_relevance': crypto_relevance,
            'positive_keywords': positive_count,
            'negative_keywords': negative_count,
            'neutral_keywords': neutral_count
        }
    
    def ensemble_analysis(self, text: str) -> Dict[str, Any]:
        """Comprehensive sentiment analysis using ensemble of all models"""
        if not text:
            return self._default_sentiment()
        
        # Clean text
        clean_text = self.clean_text(text)
        
        # Analyze with all models
        vader_result = self.analyze_with_vader(clean_text)
        textblob_result = self.analyze_with_textblob(clean_text)
        finbert_result = self.analyze_with_finbert(clean_text)
        crypto_weight = self.calculate_crypto_keywords_weight(clean_text)
        
        # Ensemble scoring
        scores = []
        confidences = []
        
        # VADER
        if vader_result['sentiment'] == 'Positif':
            scores.append(1)
        elif vader_result['sentiment'] == 'Negatif':
            scores.append(-1)
        else:
            scores.append(0)
        confidences.append(vader_result['confidence'])
        
        # TextBlob
        if textblob_result['sentiment'] == 'Positif':
            scores.append(1)
        elif textblob_result['sentiment'] == 'Negatif':
            scores.append(-1)
        else:
            scores.append(0)
        confidences.append(textblob_result['confidence'])
        
        # FinBERT (weighted more heavily for financial text)
        if self.finbert_available:
            if finbert_result['sentiment'] == 'Positif':
                scores.extend([1, 1])  # Double weight
            elif finbert_result['sentiment'] == 'Negatif':
                scores.extend([-1, -1])  # Double weight
            else:
                scores.extend([0, 0])
            confidences.extend([finbert_result['confidence'], finbert_result['confidence']])
        
        # Calculate ensemble sentiment
        if not scores:
            final_sentiment = 'Netral'
            final_confidence = 0.5
        else:
            ensemble_score = sum(scores) / len(scores)
            
            # Apply crypto keyword weight
            if crypto_weight['crypto_relevance'] > 0.3:
                ensemble_score += crypto_weight['weight']
            
            # Determine final sentiment
            if ensemble_score > 0.15:
                final_sentiment = 'Positif'
            elif ensemble_score < -0.15:
                final_sentiment = 'Negatif'
            else:
                final_sentiment = 'Netral'
            
            # Calculate confidence
            final_confidence = min(sum(confidences) / len(confidences) + crypto_weight['crypto_relevance'] * 0.1, 0.95)
        
        return {
            'sentiment': final_sentiment,
            'confidence': round(final_confidence, 3),
            'ensemble_score': round(ensemble_score, 3),
            'crypto_relevance': round(crypto_weight['crypto_relevance'], 3),
            'models_used': {
                'vader': vader_result,
                'textblob': textblob_result,
                'finbert': finbert_result if self.finbert_available else None,
                'crypto_keywords': crypto_weight
            },
            'text_length': len(clean_text),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def analyze_multiple_texts(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze sentiment for multiple texts and aggregate results"""
        if not texts:
            return self._default_sentiment()
        
        results = []
        for text in texts:
            if text:  # Skip empty texts
                result = self.ensemble_analysis(text)
                results.append(result)
        
        if not results:
            return self._default_sentiment()
        
        # Aggregate results
        sentiments = [r['sentiment'] for r in results]
        confidences = [r['confidence'] for r in results]
        scores = [r['ensemble_score'] for r in results]
        
        # Calculate overall sentiment
        sentiment_counts = {
            'Positif': sentiments.count('Positif'),
            'Negatif': sentiments.count('Negatif'),
            'Netral': sentiments.count('Netral')
        }
        
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        overall_confidence = sum(confidences) / len(confidences)
        overall_score = sum(scores) / len(scores)
        
        return {
            'sentiment': overall_sentiment,
            'confidence': round(overall_confidence, 3),
            'ensemble_score': round(overall_score, 3),
            'total_texts_analyzed': len(results),
            'sentiment_distribution': sentiment_counts,
            'individual_results': results,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _default_sentiment(self) -> Dict[str, Any]:
        """Return default sentiment when no data available"""
        return {
            'sentiment': 'Netral',
            'confidence': 0.5,
            'ensemble_score': 0.0,
            'crypto_relevance': 0.0,
            'analysis_timestamp': datetime.now().isoformat()
        }

# Test function
def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample cryptocurrency texts"""
    analyzer = CryptoSentimentAnalyzer()
    
    test_texts = [
        "Bitcoin is going to the moon! 🚀 Bullish trend confirmed!",
        "Massive dump incoming, sell everything before it crashes",
        "BTC consolidating around support levels, waiting for breakout",
        "New institutional adoption shows strong fundamentals",
        "Regulatory concerns may impact market sentiment negatively"
    ]
    
    print("🧪 Testing Crypto Sentiment Analyzer")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        result = analyzer.ensemble_analysis(text)
        print(f"\n{i}. Text: {text}")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Score: {result['ensemble_score']:.3f}")
        print(f"   Crypto Relevance: {result['crypto_relevance']:.3f}")
    
    # Test multiple texts
    print(f"\n🔄 Testing Multiple Texts Analysis")
    print("=" * 50)
    
    multi_result = analyzer.analyze_multiple_texts(test_texts)
    print(f"Overall Sentiment: {multi_result['sentiment']}")
    print(f"Overall Confidence: {multi_result['confidence']:.3f}")
    print(f"Sentiment Distribution: {multi_result['sentiment_distribution']}")

if __name__ == "__main__":
    test_sentiment_analyzer()
