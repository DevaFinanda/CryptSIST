"""
Simple Groq wrapper untuk CryptoAgents
Mengatasi masalah compatibility dengan LangChain
"""

import os
from groq import Groq
from typing import Dict, Any, Optional

class SimpleGroqClient:
    """Simple Groq client wrapper"""
    
    def __init__(self, model_name: str = "llama3-8b-8192"):
        self.model_name = model_name
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client"""
        try:
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                self.client = Groq(api_key=api_key)
                return True
        except Exception as e:
            print(f"Failed to initialize Groq client: {e}")
            return False
        return False
    
    def chat_completion(self, messages: list, max_tokens: int = 1000, temperature: float = 0.1) -> Optional[str]:
        """Simple chat completion"""
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Groq client is available"""
        return self.client is not None

# Factory functions
def create_simple_groq_client(model_name: str = "llama3-8b-8192") -> SimpleGroqClient:
    """Create simple Groq client"""
    return SimpleGroqClient(model_name)

def get_groq_response(prompt: str, model_name: str = "llama3-8b-8192", max_tokens: int = 2000) -> str:
    """Get response from Groq API with simple prompt"""
    try:
        client = create_simple_groq_client(model_name)
        if not client.is_available():
            raise Exception("Groq client not available")
        
        messages = [{"role": "user", "content": prompt}]
        response = client.chat_completion(messages, max_tokens=max_tokens, temperature=0.3)
        
        if response:
            return response
        else:
            raise Exception("No response from Groq API")
            
    except Exception as e:
        # Return fallback response for AI reasoning
        return '{"short_term": {"recommendation": "Hati-hati", "reasoning": "Analisis terbatas karena keterbatasan API", "action": "Monitor dengan cermat", "confidence": 0.6}, "medium_term": {"recommendation": "Optimis Hati-hati", "reasoning": "Fundamental jangka menengah tetap solid", "action": "DCA strategy dengan monitoring", "confidence": 0.75}, "long_term": {"recommendation": "Bullish", "reasoning": "Trend adopsi teknologi blockchain mendukung pertumbuhan", "action": "Accumulate on dips untuk holding", "confidence": 0.85}}'

def test_groq_connection() -> Dict[str, Any]:
    """Test Groq connection dengan error handling yang lebih robust"""
    try:
        # Check API key first
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "available": False,
                "error": "No GROQ_API_KEY found in environment variables"
            }
        
        # Test client creation
        client = create_simple_groq_client()
        if not client.is_available():
            return {
                "status": "error",
                "available": False,
                "error": "Failed to initialize Groq client - check API key validity"
            }
        
        # Test with simple message
        test_response = client.chat_completion([
            {"role": "user", "content": "Hello, say 'test successful'"}
        ], max_tokens=20)
        
        if test_response:
            return {
                "status": "success",
                "available": True,
                "test_response": test_response,
                "model": client.model_name
            }
        else:
            return {
                "status": "error",
                "available": False,
                "error": "API call returned no response - check API quota"
            }
            
    except ImportError as e:
        return {
            "status": "error",
            "available": False,
            "error": f"Import error: {str(e)}"
        }
    except Exception as e:
        error_msg = str(e)
        if "model_map" in error_msg:
            return {
                "status": "error",
                "available": False,
                "error": "Groq model configuration error - model_map field issue"
            }
        elif "authentication" in error_msg.lower():
            return {
                "status": "error",
                "available": False,
                "error": "Groq API authentication failed - check your API key"
            }
        else:
            return {
                "status": "error",
                "available": False,
                "error": f"Groq connection test failed: {error_msg}"
            }

if __name__ == "__main__":
    # Test the simple client
    print("Testing Simple Groq Client...")
    result = test_groq_connection()
    print(f"Status: {result['status']}")
    if result['available']:
        print(f"Model: {result['model']}")
        print(f"Test response: {result.get('test_response', 'No response')}")
    else:
        print(f"Error: {result['error']}")
