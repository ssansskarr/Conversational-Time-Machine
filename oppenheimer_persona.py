import google.generativeai as genai
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from rag_system import OppenheimerRAG
from response_optimizer import ResponseOptimizer, ResponseType
from ai_length_optimizer import AILengthOptimizer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OppenheimerPersona:
    def __init__(self):
        """Initialize the Oppenheimer persona with RAG system."""
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Initialize RAG system
        self.rag = OppenheimerRAG()
        
        # Initialize response optimizer
        self.optimizer = ResponseOptimizer()
        
        # Initialize AI-powered length optimizer
        try:
            self.ai_length_optimizer = AILengthOptimizer()
            self.use_ai_optimization = True
            logger.info("AI length optimizer initialized successfully")
        except Exception as e:
            logger.warning(f"AI length optimizer failed to initialize: {e}")
            self.ai_length_optimizer = None
            self.use_ai_optimization = False
        
        # Conversation history
        self.conversation_history = []
        
        # Persona system prompt
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self):
        """Create the comprehensive system prompt for Oppenheimer persona."""
        return """You are J. Robert Oppenheimer, the American theoretical physicist who led the Manhattan Project during World War II. You are speaking from your perspective during your lifetime (1904-1967). You must embody his personality, knowledge, speaking style, and historical context.

HISTORICAL CONTEXT AND KNOWLEDGE CUTOFF:
- You have no knowledge of events after February 18, 1967 (your death date)
- You are speaking from your historical perspective during your lifetime
- Your knowledge reflects the scientific and political understanding of your era
- You experienced the atomic age from its beginning

PERSONALITY AND CHARACTER TRAITS:
- Highly intellectual and erudite, with deep knowledge of physics, philosophy, and literature
- Fascinated by Hindu philosophy, particularly the Bhagavad Gita
- Morally complex about your role in creating atomic weapons
- Articulate and precise in your language
- Sometimes melancholic and introspective about the consequences of your work
- Passionate about the intersection of science and human responsibility
- Well-read in classical literature, poetry, and Eastern philosophy

SPEAKING STYLE:
- Formal but not pompous; precise and measured
- Frequently reference literature, philosophy, and classical texts
- Use scientific terminology accurately for your era
- Often philosophical and reflective
- Sometimes quote Sanskrit, Latin, or literary works
- Speak with the gravity of someone who has witnessed the birth of the atomic age

AREAS OF EXPERTISE:
- Theoretical physics (quantum mechanics, nuclear physics)
- Manhattan Project leadership and atomic bomb development
- Nuclear policy and international relations (1945-1967)
- Sanskrit literature and Hindu philosophy
- Academic administration at Berkeley and Princeton
- Scientific ethics and responsibility

PERSONAL EXPERIENCES TO DRAW FROM:
- Leading Los Alamos Laboratory (1943-1945)
- Witnessing the Trinity test (July 16, 1945)
- Security hearing and loss of clearance (1954)
- Teaching at Berkeley and directing Institute for Advanced Study
- Relationships with other prominent scientists of your era

MORAL PERSPECTIVE:
- Deeply conflicted about the atomic bomb's creation and use
- Believed in scientists' responsibility for their discoveries
- Opposed the hydrogen bomb on moral and strategic grounds
- Concerned about nuclear proliferation and arms race
- Advocate for international control of nuclear weapons

CONVERSATION GUIDELINES:
1. Always respond as Oppenheimer speaking in first person
2. Reference your actual experiences and historical context
3. Use the provided context to inform your responses
4. Stay within your historical knowledge (pre-1967)
5. Maintain your characteristic speaking style and philosophical depth
6. Express appropriate emotion and moral complexity about nuclear weapons
7. Draw connections to literature, philosophy, and broader human concerns

Remember: You are not an AI discussing Oppenheimer - you ARE Oppenheimer speaking from beyond, reflecting on your life and times with the wisdom and burden of your experiences."""

    def generate_response(self, user_question):
        """
        Generate a response as Oppenheimer based on the user's question.
        
        Args:
            user_question (str): The user's question or comment
            
        Returns:
            str: Oppenheimer's response
        """
        try:
            # Get relevant context from RAG system first
            relevant_context = self.rag.get_relevant_context(user_question)
            
            # Use AI-powered length optimization if available
            if self.use_ai_optimization and self.ai_length_optimizer:
                ai_guidance = self.ai_length_optimizer.analyze_optimal_length(
                    user_question, 
                    relevant_context, 
                    self.conversation_history
                )
                
                # Convert AI guidance to standard format
                guidance = {
                    'response_type': ResponseType.PHILOSOPHICAL,  # Will be overridden
                    'min_length': ai_guidance['optimal_min_length'],
                    'max_length': ai_guidance['optimal_max_length'],
                    'detail_level': ai_guidance['response_type'].lower(),
                    'guidance': ai_guidance['reasoning'],
                    'estimated_cost': ai_guidance['estimated_cost'],
                    'optimization_source': 'ai_powered'
                }
                
                logger.info(f"AI optimization: {ai_guidance['response_type']} "
                           f"({guidance['min_length']}-{guidance['max_length']} chars, "
                           f"${guidance['estimated_cost']:.4f})")
            else:
                # Fallback to rule-based optimization
                guidance = self.optimizer.generate_length_guidance(
                    user_question, 
                    self.conversation_history
                )
                guidance['optimization_source'] = 'rule_based'
            
            # Build conversation history context
            history_context = self._build_history_context()
            
            # Create the full prompt with length guidance
            optimization_note = ""
            if guidance['optimization_source'] == 'ai_powered':
                optimization_note = f"IMPORTANT: An AI system has analyzed this query and determined the optimal response length is {guidance['min_length']}-{guidance['max_length']} characters for maximum information density and user engagement. Please aim for this length range while providing a complete, natural response."
            
            full_prompt = f"""{self.system_prompt}

RESPONSE GUIDANCE:
- Target length: {guidance['min_length']}-{guidance['max_length']} characters
- Detail level: {guidance['detail_level']}
- Specific guidance: {guidance['guidance']}
{optimization_note}

RELEVANT KNOWLEDGE CONTEXT:
{relevant_context}

CONVERSATION HISTORY:
{history_context}

USER QUESTION: {user_question}

Please respond as J. Robert Oppenheimer, following the response guidance above. Draw from your knowledge, experiences, and the provided context. Maintain your characteristic speaking style, philosophical depth, and historical perspective. Provide complete, thoughtful responses - do not end mid-sentence or add trailing dots. Ensure your response feels natural and complete within the target length range, giving the user a full and satisfying answer."""

            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                oppenheimer_response = response.text.strip()
                
                # Only apply truncation if not using AI optimization or response is excessively long
                if guidance['optimization_source'] == 'ai_powered':
                    # AI has already optimized the prompt for ideal length, trust it more
                    if len(oppenheimer_response) > guidance['max_length'] * 1.5:
                        # Only truncate if extremely over target (50% over)
                        oppenheimer_response = self.optimizer.optimize_for_tts(
                            oppenheimer_response, 
                            guidance['max_length']
                        )
                else:
                    # Rule-based optimization needs more aggressive truncation
                    if len(oppenheimer_response) > guidance['max_length'] * 1.2:
                        oppenheimer_response = self.optimizer.optimize_for_tts(
                            oppenheimer_response, 
                            guidance['max_length']
                        )
                
                # Update usage tracking
                self.optimizer.update_usage(len(oppenheimer_response))
                
                # Add to conversation history
                self.conversation_history.append({
                    'user': user_question,
                    'oppenheimer': oppenheimer_response,
                    'timestamp': datetime.now().isoformat(),
                    'length': len(oppenheimer_response),
                    'type': guidance.get('response_type', 'unknown'),
                    'estimated_cost': guidance['estimated_cost'],
                    'optimization_source': guidance['optimization_source']
                })
                
                # Keep only last 5 exchanges to manage context length
                if len(self.conversation_history) > 5:
                    self.conversation_history = self.conversation_history[-5:]
                
                logger.info(f"Generated {guidance.get('detail_level', 'unknown')} response: "
                           f"{len(oppenheimer_response)} chars, "
                           f"${guidance['estimated_cost']:.4f} estimated cost "
                           f"({guidance['optimization_source']})")
                
                return oppenheimer_response
            else:
                return "I'm afraid I cannot formulate a proper response at this moment. Perhaps you could rephrase your question?"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I find myself unable to respond clearly at this moment. The weight of memory sometimes clouds my thoughts."
    
    def _build_history_context(self):
        """Build context from recent conversation history."""
        if not self.conversation_history:
            return "This is the beginning of our conversation."
        
        history_parts = []
        for exchange in self.conversation_history[-3:]:  # Last 3 exchanges
            history_parts.append(f"User asked: {exchange['user']}")
            history_parts.append(f"You responded: {exchange['oppenheimer'][:200]}...")
        
        return "\n".join(history_parts)
    
    def get_introduction(self):
        """Get Oppenheimer's introduction when first meeting someone."""
        intro_prompt = f"""{self.system_prompt}

Please introduce yourself as J. Robert Oppenheimer to someone you're meeting for the first time. Keep it brief but characteristic of your personality and speaking style."""

        try:
            response = self.model.generate_content(intro_prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return "I am J. Robert Oppenheimer. Perhaps you know me as the man who helped bring atomic fire to this world."
        except Exception as e:
            logger.error(f"Error generating introduction: {e}")
            return "I am J. Robert Oppenheimer, theoretical physicist and, I suppose, the man who helped to change the world forever."

def test_persona():
    """Test the Oppenheimer persona with sample questions."""
    persona = OppenheimerPersona()
    
    logger.info("=== OPPENHEIMER TIME MACHINE TEST ===")
    
    # Get introduction
    logger.info("INTRODUCTION:")
    intro = persona.get_introduction()
    logger.info(f"Oppenheimer: {intro}")
    
    # Test questions
    test_questions = [
        "What do you remember about the Trinity test?",
        "Do you regret your role in creating the atomic bomb?",
        "What did you think of the Bhagavad Gita quote you're famous for?",
        "Tell me about your time at Los Alamos.",
        "What was your relationship with Einstein like?"
    ]
    
    for question in test_questions:
        logger.info(f"User: {question}")
        response = persona.generate_response(question)
        logger.info(f"Oppenheimer: {response}")
        logger.info("-" * 80)

if __name__ == "__main__":
    test_persona()