import google.generativeai as genai
import os
import logging
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AILengthOptimizer:
    """AI-powered response length optimizer using separate Gemini API for cost-effectiveness."""
    
    def __init__(self):
        """Initialize the AI length optimizer with dedicated API key."""
        # Use separate API key for length optimization
        self.optimizer_api_key = os.getenv('GEMINI_LENGTH_OPTIMIZER_KEY')
        if not self.optimizer_api_key:
            raise ValueError("GEMINI_LENGTH_OPTIMIZER_KEY environment variable not set")
        
        # Configure separate Gemini instance for optimization
        genai.configure(api_key=self.optimizer_api_key)
        self.optimizer_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Cost parameters
        self.cost_per_char_tts = 0.000016  # Google TTS cost
        self.cost_per_token_gemini = 0.00000075  # Gemini Flash cost (approximate)
        
    def analyze_optimal_length(self, user_query: str, context: str = "", conversation_history: list = None) -> Dict:
        """
        Use AI to determine optimal response length based on information density and cost.
        
        Args:
            user_query (str): The user's question
            context (str): RAG context available
            conversation_history (list): Previous conversation exchanges
            
        Returns:
            Dict: Optimization recommendations
        """
        
        # Build conversation context
        history_summary = self._summarize_conversation_history(conversation_history or [])
        
        # Create optimization prompt
        optimization_prompt = f"""
You are a response length optimizer for an AI system simulating J. Robert Oppenheimer. 
Your task is to determine the optimal response length that maximizes information density while minimizing cost.

COST CONSIDERATIONS:
- TTS synthesis: $0.000016 per character
- User engagement drops significantly after 1000 characters
- Very short responses (<200 chars) feel unsatisfying
- Very long responses (>1500 chars) are expensive and lose user attention

CONTEXT ANALYSIS:
User Query: "{user_query}"
Available Context: "{context[:500]}..."
Conversation History: {history_summary}

RESPONSE TYPE CLASSIFICATION:
Analyze the query and classify it as one of:
1. FACTUAL: Simple factual questions (optimal: 150-400 chars)
2. PHILOSOPHICAL: Deep moral/philosophical questions (optimal: 400-800 chars)
3. NARRATIVE: Historical storytelling (optimal: 500-1000 chars)
4. PERSONAL: Emotional/personal reflections (optimal: 300-600 chars)
5. SCIENTIFIC: Technical explanations (optimal: 400-700 chars)

INFORMATION DENSITY FACTORS:
- How much context is available to draw from?
- How complex is the question?
- What level of detail would satisfy the user?
- Is this a follow-up question that can be shorter?

Provide your analysis in this JSON format:
{{
    "response_type": "PHILOSOPHICAL",
    "complexity_score": 8,
    "information_density_needed": "high",
    "optimal_min_length": 400,
    "optimal_max_length": 650,
    "reasoning": "This is a complex moral question about nuclear weapons that requires philosophical depth but should remain engaging. The user expects Oppenheimer's characteristic introspection without excessive length.",
    "cost_effectiveness_score": 9,
    "engagement_prediction": "high"
}}

Analyze and respond with the optimal length recommendation:
"""

        try:
            response = self.optimizer_model.generate_content(optimization_prompt)
            
            if response and response.text:
                # Parse the JSON response
                import json
                import re
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    optimization_data = json.loads(json_match.group())
                    
                    # Validate and sanitize the response
                    return self._validate_optimization_response(optimization_data, user_query)
                else:
                    logger.warning("Failed to parse optimization response, using fallback")
                    return self._fallback_optimization(user_query)
                    
        except Exception as e:
            logger.error(f"AI optimization failed: {e}")
            return self._fallback_optimization(user_query)
    
    def _summarize_conversation_history(self, history: list) -> str:
        """Summarize conversation history for context."""
        if not history:
            return "New conversation"
        
        recent_exchanges = history[-3:]  # Last 3 exchanges
        summary_parts = []
        
        for exchange in recent_exchanges:
            if isinstance(exchange, dict):
                user_msg = exchange.get('user', '')[:100]
                summary_parts.append(f"User asked about: {user_msg}")
        
        return "; ".join(summary_parts) if summary_parts else "Brief conversation history"
    
    def _validate_optimization_response(self, data: Dict, query: str) -> Dict:
        """Validate and sanitize the AI optimization response."""
        # Ensure required fields exist
        required_fields = ['optimal_min_length', 'optimal_max_length', 'response_type']
        for field in required_fields:
            if field not in data:
                return self._fallback_optimization(query)
        
        # Sanitize length values
        min_length = max(100, min(1500, int(data.get('optimal_min_length', 300))))
        max_length = max(min_length + 100, min(1500, int(data.get('optimal_max_length', 600))))
        
        # Ensure reasonable bounds
        if max_length - min_length < 50:
            max_length = min_length + 200
        
        return {
            'response_type': data.get('response_type', 'NARRATIVE'),
            'complexity_score': max(1, min(10, int(data.get('complexity_score', 5)))),
            'optimal_min_length': min_length,
            'optimal_max_length': max_length,
            'reasoning': data.get('reasoning', 'AI-optimized length calculation'),
            'cost_effectiveness_score': max(1, min(10, int(data.get('cost_effectiveness_score', 7)))),
            'engagement_prediction': data.get('engagement_prediction', 'medium'),
            'estimated_cost': max_length * self.cost_per_char_tts,
            'optimization_source': 'ai_powered'
        }
    
    def _fallback_optimization(self, query: str) -> Dict:
        """Fallback optimization using simple heuristics."""
        query_lower = query.lower()
        
        # Simple classification
        if any(word in query_lower for word in ['when', 'where', 'who', 'born', 'died']):
            response_type = 'FACTUAL'
            min_length, max_length = 150, 350
        elif any(word in query_lower for word in ['regret', 'feel', 'think', 'philosophy', 'moral']):
            response_type = 'PHILOSOPHICAL'
            min_length, max_length = 400, 700
        elif any(word in query_lower for word in ['tell me about', 'describe', 'what happened']):
            response_type = 'NARRATIVE'
            min_length, max_length = 500, 900
        else:
            response_type = 'PERSONAL'
            min_length, max_length = 300, 600
        
        return {
            'response_type': response_type,
            'complexity_score': 5,
            'optimal_min_length': min_length,
            'optimal_max_length': max_length,
            'reasoning': 'Fallback heuristic-based optimization',
            'cost_effectiveness_score': 6,
            'engagement_prediction': 'medium',
            'estimated_cost': max_length * self.cost_per_char_tts,
            'optimization_source': 'fallback_heuristic'
        }
    
    def calculate_cost_benefit_ratio(self, text_length: int, engagement_score: int) -> float:
        """Calculate cost-benefit ratio for a given response length."""
        cost = text_length * self.cost_per_char_tts
        
        # Engagement drops off after certain lengths
        if text_length < 200:
            engagement_multiplier = 0.6  # Too short, unsatisfying
        elif text_length < 500:
            engagement_multiplier = 1.0  # Sweet spot
        elif text_length < 800:
            engagement_multiplier = 0.9  # Still good
        elif text_length < 1200:
            engagement_multiplier = 0.7  # Getting long
        else:
            engagement_multiplier = 0.4  # Too long, losing attention
        
        adjusted_engagement = engagement_score * engagement_multiplier
        
        # Return value per dollar (higher is better)
        return adjusted_engagement / (cost * 1000) if cost > 0 else 0

def test_ai_length_optimizer():
    """Test the AI length optimizer with sample queries."""
    try:
        optimizer = AILengthOptimizer()
        
        test_queries = [
            "When were you born?",
            "Do you regret creating the atomic bomb?",
            "Tell me about your relationship with Einstein.",
            "What was the Trinity test like?",
            "How does nuclear fission work?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = optimizer.analyze_optimal_length(query)
            print(f"Type: {result['response_type']}")
            print(f"Optimal length: {result['optimal_min_length']}-{result['optimal_max_length']} chars")
            print(f"Reasoning: {result['reasoning'][:100]}...")
            print(f"Cost: ${result['estimated_cost']:.4f}")
            print(f"Source: {result['optimization_source']}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_ai_length_optimizer()