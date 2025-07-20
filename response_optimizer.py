import re
import logging
from typing import Dict, Tuple, List
from enum import Enum

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Classification of response types for appropriate length handling."""
    SIMPLE_FACT = "simple_fact"          # Brief factual answers
    PHILOSOPHICAL = "philosophical"       # Deep, thoughtful responses
    HISTORICAL_NARRATIVE = "historical"  # Detailed storytelling
    PERSONAL_REFLECTION = "personal"     # Emotional, introspective
    SCIENTIFIC_EXPLANATION = "scientific" # Technical details
    GREETING = "greeting"                # Introduction/casual

class ResponseOptimizer:
    """Optimizes response length and detail based on query type and context."""
    
    def __init__(self):
        # Keywords that indicate different response types
        self.response_patterns = {
            ResponseType.SIMPLE_FACT: [
                r'\b(when|where|who|what year|how old|born|died)\b',
                r'\b(yes|no)\b questions',
                r'\b(name|date|location)\b'
            ],
            ResponseType.PHILOSOPHICAL: [
                r'\b(think|feel|believe|philosophy|moral|ethics|regret)\b',
                r'\b(bhagavad|gita|meaning|purpose|responsibility)\b',
                r'\b(why|should|ought|right|wrong)\b'
            ],
            ResponseType.HISTORICAL_NARRATIVE: [
                r'\b(tell me about|describe|what happened|story|experience)\b',
                r'\b(trinity|los alamos|manhattan project|bomb|war)\b',
                r'\b(relationship|worked with|knew)\b'
            ],
            ResponseType.PERSONAL_REFLECTION: [
                r'\b(how did you feel|personal|private|family|emotions)\b',
                r'\b(guilt|pride|fear|hope|regret|memory)\b'
            ],
            ResponseType.SCIENTIFIC_EXPLANATION: [
                r'\b(physics|quantum|nuclear|atoms|science|theory)\b',
                r'\b(explain|how does|mechanism|process)\b'
            ],
            ResponseType.GREETING: [
                r'\b(hello|hi|who are you|introduce|meet)\b'
            ]
        }
        
        # Target lengths for different response types (in characters)
        self.target_lengths = {
            ResponseType.SIMPLE_FACT: (100, 300),        # Short and direct
            ResponseType.PHILOSOPHICAL: (400, 800),      # Thoughtful depth
            ResponseType.HISTORICAL_NARRATIVE: (500, 1000), # Rich detail
            ResponseType.PERSONAL_REFLECTION: (400, 700), # Measured emotion
            ResponseType.SCIENTIFIC_EXPLANATION: (400, 800), # Clear but thorough
            ResponseType.GREETING: (150, 250)            # Brief but characterful
        }
        
        # Cost thresholds (characters to TTS cost estimation)
        self.cost_per_char = 0.000016  # Approximate Google TTS cost
        self.max_daily_chars = 50000   # Budget limit
        self.daily_usage = 0
    
    def classify_query(self, query: str) -> ResponseType:
        """Classify the query to determine appropriate response type."""
        query_lower = query.lower()
        
        # Score each response type
        scores = {}
        for response_type, patterns in self.response_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[response_type] = score
        
        # Return the highest scoring type, default to HISTORICAL_NARRATIVE
        if max(scores.values()) == 0:
            return ResponseType.HISTORICAL_NARRATIVE
        
        return max(scores, key=scores.get)
    
    def _analyze_query_complexity(self, query: str) -> str:
        """Analyze query complexity to determine appropriate response length."""
        query_lower = query.lower()
        
        # Simple questions (short answers needed)
        simple_indicators = [
            r'\b(when|where|who|what year|how old|born|died)\b',
            r'\b(yes|no)\b',
            r'\b(name|date|location)\b',
            r'^(who|what|when|where)\s+\w+\s*\?*$'  # Single word questions
        ]
        
        # Complex questions (longer answers needed)
        complex_indicators = [
            r'\b(why|how|explain|describe|tell me about|what was.*like)\b',
            r'\b(relationship|experience|thoughts|feelings|philosophy)\b',
            r'\b(compare|contrast|difference|similar)\b',
            r'\s+and\s+',  # Multiple questions joined with "and"
            r'\?.*\?'      # Multiple question marks
        ]
        
        simple_score = sum(len(re.findall(pattern, query_lower)) for pattern in simple_indicators)
        complex_score = sum(len(re.findall(pattern, query_lower)) for pattern in complex_indicators)
        
        # Length-based complexity
        if len(query) > 100:
            complex_score += 1
        elif len(query) < 20:
            simple_score += 1
            
        if complex_score > simple_score:
            return 'complex'
        elif simple_score > complex_score:
            return 'simple'
        else:
            return 'medium'
    
    def generate_length_guidance(self, query: str, conversation_history: List = None) -> Dict:
        """Generate guidance for response length and detail level."""
        response_type = self.classify_query(query)
        min_length, max_length = self.target_lengths[response_type]
        
        # Analyze query complexity for smarter length adjustment
        query_complexity = self._analyze_query_complexity(query)
        
        # Adjust based on query complexity
        if query_complexity == 'simple':
            max_length = int(max_length * 0.7)  # Shorter for simple questions
        elif query_complexity == 'complex':
            max_length = int(max_length * 1.2)  # Slightly longer for complex questions
        
        # Adjust based on conversation context
        if conversation_history and len(conversation_history) > 3:
            # Later in conversation, can be more concise
            max_length = int(max_length * 0.9)
        
        # Budget considerations
        estimated_cost = max_length * self.cost_per_char
        remaining_budget = (self.max_daily_chars - self.daily_usage) * self.cost_per_char
        
        if estimated_cost > remaining_budget * 0.5:  # 50% of remaining budget
            # Reduce length if approaching budget limits
            max_length = int(max_length * 0.7)
            logger.warning(f"Reducing response length due to budget constraints")
        
        # Ensure reasonable bounds
        max_length = min(max_length, 1200)  # Hard cap at 1200 characters
        min_length = max(min_length, 100)   # Minimum 100 characters
        
        return {
            "response_type": response_type,
            "min_length": min_length,
            "max_length": max_length,
            "detail_level": self._get_detail_level(response_type),
            "estimated_cost": max_length * self.cost_per_char,
            "guidance": self._get_response_guidance(response_type),
            "complexity": query_complexity
        }
    
    def _get_detail_level(self, response_type: ResponseType) -> str:
        """Get detail level instruction for the response."""
        detail_map = {
            ResponseType.SIMPLE_FACT: "concise",
            ResponseType.PHILOSOPHICAL: "thoughtful_depth",
            ResponseType.HISTORICAL_NARRATIVE: "rich_detail",
            ResponseType.PERSONAL_REFLECTION: "measured_emotion",
            ResponseType.SCIENTIFIC_EXPLANATION: "clear_thorough",
            ResponseType.GREETING: "brief_characterful"
        }
        return detail_map[response_type]
    
    def _get_response_guidance(self, response_type: ResponseType) -> str:
        """Get specific guidance for generating the response."""
        guidance_map = {
            ResponseType.SIMPLE_FACT: (
                "Provide a direct, factual answer. Include only essential details. "
                "Be precise and avoid unnecessary elaboration."
            ),
            ResponseType.PHILOSOPHICAL: (
                "Explore the deeper implications thoughtfully. Reference relevant literature "
                "or philosophical concepts. Show moral complexity and introspection."
            ),
            ResponseType.HISTORICAL_NARRATIVE: (
                "Paint a vivid picture of the events. Include sensory details, emotions, "
                "and context. Make the historical moment come alive."
            ),
            ResponseType.PERSONAL_REFLECTION: (
                "Share genuine emotional insight. Be vulnerable but measured. "
                "Connect personal experience to broader themes."
            ),
            ResponseType.SCIENTIFIC_EXPLANATION: (
                "Explain clearly without oversimplifying. Use appropriate technical terms "
                "but ensure accessibility. Include the human element of discovery."
            ),
            ResponseType.GREETING: (
                "Be characteristically formal yet warm. Hint at your philosophical nature "
                "and historical significance briefly."
            )
        }
        return guidance_map[response_type]
    
    def optimize_for_tts(self, text: str, target_length: int = None) -> str:
        """Optimize text for TTS while preserving meaning and character."""
        if target_length is None:
            return text
        
        current_length = len(text)
        
        if current_length <= target_length:
            return text
        
        # Intelligent truncation strategies
        # 1. Remove redundant phrases
        text = self._remove_redundancy(text)
        
        # 2. Shorten complex sentences
        if len(text) > target_length:
            text = self._simplify_sentences(text, target_length)
        
        # 3. Smart truncation as last resort
        if len(text) > target_length:
            text = self._smart_truncate(text, target_length)
        
        return text
    
    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant phrases while preserving meaning."""
        # Remove filler phrases that don't add substantial meaning
        redundant_phrases = [
            r'\b(as I have mentioned|as I said|you see|you know|well,)\b',
            r'\b(it is important to note that|it should be noted that)\b',
            r'\b(I would say that|I believe that|I think that)\b'
        ]
        
        for phrase in redundant_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _simplify_sentences(self, text: str, target_length: int) -> str:
        """Simplify complex sentences to reduce length."""
        sentences = text.split('. ')
        simplified = []
        
        for sentence in sentences:
            # Split compound sentences
            if ' and ' in sentence and len(sentence) > 100:
                parts = sentence.split(' and ')
                # Keep the most important part (usually the first)
                simplified.append(parts[0])
            else:
                simplified.append(sentence)
        
        result = '. '.join(simplified)
        if not result.endswith('.'):
            result += '.'
        
        return result
    
    def _smart_truncate(self, text: str, target_length: int) -> str:
        """Intelligently truncate text at natural breaking points."""
        if len(text) <= target_length:
            return text
        
        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= target_length - 3:  # Leave room for "..."
                truncated += sentence + '. '
            else:
                break
        
        if truncated:
            return truncated.rstrip() + "..."
        
        # If no good sentence break, truncate at word boundary
        words = text[:target_length-3].split()
        return ' '.join(words[:-1]) + "..."
    
    def update_usage(self, text_length: int):
        """Update daily usage tracking."""
        self.daily_usage += text_length
        
    def get_cost_estimate(self, text: str) -> float:
        """Get cost estimate for TTS of given text."""
        return len(text) * self.cost_per_char
    
    def should_use_tts(self, text: str) -> bool:
        """Determine if TTS should be used based on length and budget."""
        cost = self.get_cost_estimate(text)
        remaining_budget = (self.max_daily_chars - self.daily_usage) * self.cost_per_char
        
        # Use TTS if cost is reasonable and within budget
        return cost <= remaining_budget and len(text) <= 1200

# Example usage functions
def demonstrate_optimization():
    """Demonstrate the response optimization system."""
    optimizer = ResponseOptimizer()
    
    test_queries = [
        "When were you born?",
        "What do you think about the moral implications of nuclear weapons?",
        "Tell me about the Trinity test experience.",
        "Do you regret creating the atomic bomb?",
        "How does nuclear fission work?",
        "Hello, who are you?"
    ]
    
    for query in test_queries:
        guidance = optimizer.generate_length_guidance(query)
        print(f"\nQuery: {query}")
        print(f"Type: {guidance['response_type'].value}")
        print(f"Target length: {guidance['min_length']}-{guidance['max_length']} chars")
        print(f"Detail level: {guidance['detail_level']}")
        print(f"Estimated cost: ${guidance['estimated_cost']:.4f}")
        print(f"Guidance: {guidance['guidance'][:100]}...")

if __name__ == "__main__":
    demonstrate_optimization()