import streamlit as st
import os
import tempfile
import pygame
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import our custom modules
from oppenheimer_persona import OppenheimerPersona
from local_tts_service import LocalTTS  # <-- Import the new local TTS service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
except:
    logger.warning("pygame mixer initialization failed - audio playback may not work")

class ConversationalTimeMachine:
    def __init__(self):
        """Initialize the Conversational Time Machine."""
        self.persona = OppenheimerPersona()
        self.tts = LocalTTS()  # <-- Use the new LocalTTS service
        
    def process_conversation(self, user_input):
        """
        Process a conversation turn: generate response and synthesize speech.
        
        Args:
            user_input (str): User's question or comment
            
        Returns:
            tuple: (text_response, audio_file_path, cost_info)
        """
        try:
            # Generate Oppenheimer's text response
            text_response = self.persona.generate_response(user_input)
            
            # Check if TTS should be used based on cost and length
            should_use_tts = self.persona.optimizer.should_use_tts(text_response)
            estimated_cost = self.persona.optimizer.get_cost_estimate(text_response)
            
            cost_info = {
                'text_length': len(text_response),
                'estimated_cost': estimated_cost,
                'tts_enabled': should_use_tts,
                'daily_usage': self.persona.optimizer.daily_usage
            }
            
            audio_path = None
            if should_use_tts:
                # Generate audio response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_file = f"oppenheimer_response_{timestamp}.wav"
                
                try:
                    # Use the local TTS service to synthesize speech
                    audio_path = self.tts.synthesize(text_response, audio_file)
                    logger.info(f"Local TTS generated: {len(text_response)} chars")
                except Exception as tts_error:
                    logger.warning(f"Local TTS failed: {tts_error}")
                    cost_info['tts_enabled'] = False
            else:
                logger.info(f"TTS skipped for cost optimization: {len(text_response)} chars, ${estimated_cost:.4f}")
            
            return text_response, audio_path, cost_info
                
        except Exception as e:
            logger.error(f"Conversation processing error: {e}")
            error_response = "I find myself momentarily unable to respond. The burden of memory weighs heavily at times."
            return error_response, None, {'error': True}

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="The Conversational Time Machine: J. Robert Oppenheimer",
        page_icon="⚛️",
        layout="wide"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .oppenheimer-quote {
        font-style: italic;
        text-align: center;
        color: #666;
        padding: 1rem;
        border-left: 3px solid #2a5298;
        margin: 1rem 0;
    }
    .chat-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .oppenheimer-message {
        background: #fff3e0;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #ff9800;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚛️ The Conversational Time Machine</h1>
        <h2>Speak with J. Robert Oppenheimer</h2>
        <p>Experience a conversation with the "Father of the Atomic Bomb"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Oppenheimer quote
    st.markdown("""
    <div class="oppenheimer-quote">
        "Now I am become Death, the destroyer of worlds."<br>
        — J. Robert Oppenheimer, recalling the Trinity test
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'time_machine' not in st.session_state:
        st.session_state.time_machine = ConversationalTimeMachine()
        st.session_state.conversation_history = []
        st.session_state.initialized = False
    
    # Introduction section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### About This Experience")
        st.write("""
        This application uses advanced AI to simulate a conversation with J. Robert Oppenheimer (1904-1967), 
        the theoretical physicist who led the Manhattan Project. Through a combination of:
        
        - **RAG (Retrieval-Augmented Generation)**: Grounded in historical facts from his biography, quotes, and letters
        - **Persona-Driven AI**: Responds in Oppenheimer's characteristic speaking style and perspective
        - **Voice Synthesis**: Uses Google Cloud TTS to approximate his voice characteristics
        
        Ask about his life, the Manhattan Project, his thoughts on nuclear weapons, or his philosophical views.
        """)
    
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/JROppenheimer-LosAlamos.jpg/256px-JROppenheimer-LosAlamos.jpg", 
                caption="J. Robert Oppenheimer at Los Alamos", width=200)
    
    # Get Oppenheimer's introduction if not already done
    if not st.session_state.initialized:
        with st.spinner("Initializing conversation with Dr. Oppenheimer..."):
            intro = st.session_state.time_machine.persona.get_introduction()
            st.session_state.conversation_history.append({
                'type': 'oppenheimer',
                'content': intro,
                'timestamp': datetime.now()
            })
            st.session_state.initialized = True
    
    # Display conversation history
    st.markdown("### Conversation")
    
    for message in st.session_state.conversation_history:
        if message['type'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="oppenheimer-message">
                <strong>Dr. Oppenheimer:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Display audio player if available
            if 'audio_path' in message and message['audio_path'] and os.path.exists(message['audio_path']):
                st.audio(message['audio_path'], format='audio/wav')
    
    # User input
    st.markdown("### Ask Dr. Oppenheimer")
    
    # Sample questions
    st.markdown("**Suggested questions:**")
    sample_questions = [
        "What do you remember about the Trinity test?",
        "Do you regret creating the atomic bomb?",
        "Tell me about your time at Los Alamos",
        "What did the Bhagavad Gita mean to you?",
        "What was your relationship with Einstein like?"
    ]
    
    cols = st.columns(len(sample_questions))
    for i, question in enumerate(sample_questions):
        with cols[i]:
            if st.button(f"💭 {question[:30]}...", key=f"sample_{i}"):
                st.session_state.user_input = question
    
    # Text input
    user_input = st.text_area(
        "Your question to Dr. Oppenheimer:",
        value=st.session_state.get('user_input', ''),
        height=100,
        placeholder="Ask about his life, the Manhattan Project, nuclear physics, or his philosophical views..."
    )
    
    # Submit button
    if st.button("🎙️ Ask Dr. Oppenheimer", type="primary"):
        if user_input.strip():
            # Add user message to history
            st.session_state.conversation_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Process the conversation
            with st.spinner("Dr. Oppenheimer is formulating his response..."):
                try:
                    text_response, audio_path, cost_info = st.session_state.time_machine.process_conversation(user_input)
                    
                    # Add Oppenheimer's response to history
                    response_data = {
                        'type': 'oppenheimer',
                        'content': text_response,
                        'audio_path': audio_path,
                        'timestamp': datetime.now(),
                        'cost_info': cost_info
                    }
                    st.session_state.conversation_history.append(response_data)
                    
                    # Show cost info if TTS was skipped
                    if not cost_info.get('tts_enabled', True) and not cost_info.get('error'):
                        optimization_source = response_data.get('cost_info', {}).get('optimization_source', 'unknown')
                        st.info(f"🔇 Audio synthesis skipped for cost optimization "
                               f"({cost_info['text_length']} chars, ${cost_info['estimated_cost']:.4f}) "
                               f"[{optimization_source}]")
                    
                    # Clear input
                    st.session_state.user_input = ''
                    
                    # Rerun to update display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question or comment.")
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### About J. Robert Oppenheimer")
        st.markdown("""
        **Born:** April 22, 1904, New York City  
        **Died:** February 18, 1967, Princeton, NJ  
        
        **Key Roles:**
        - Scientific Director, Manhattan Project
        - Director, Institute for Advanced Study
        - Professor, UC Berkeley
        
        **Famous For:**
        - Leading development of atomic bomb
        - Trinity test (July 16, 1945)
        - "Now I am become Death" quote
        - Post-war nuclear policy advocacy
        """)
        
        st.markdown("### Historical Context")
        st.markdown("""
        This AI responds from Oppenheimer's historical perspective (1904-1967):
        - World War II and Manhattan Project
        - Early nuclear age and Cold War
        - McCarthyism and security hearing (1954)
        - Nuclear proliferation concerns
        """)
        
        st.markdown("### Technology")
        st.markdown("""
        - **LLM:** Google Gemini 1.5 Flash
        - **Knowledge Base:** RAG with ChromaDB
        - **Voice:** Google Cloud TTS
        - **Interface:** Streamlit
        """)
        
        # Cost monitoring dashboard
        if 'time_machine' in st.session_state:
            st.markdown("### 💰 Cost Monitor")
            optimizer = st.session_state.time_machine.persona.optimizer
            
            daily_usage = optimizer.daily_usage
            max_chars = optimizer.max_daily_chars
            usage_percent = (daily_usage / max_chars) * 100
            
            st.progress(usage_percent / 100)
            st.caption(f"Daily usage: {daily_usage:,}/{max_chars:,} chars ({usage_percent:.1f}%)")
            st.caption(f"Estimated cost: ${daily_usage * optimizer.cost_per_char:.4f}")
            
            # Response type breakdown
            if st.session_state.conversation_history:
                response_types = {}
                total_cost = 0
                for msg in st.session_state.conversation_history:
                    if msg['type'] == 'oppenheimer' and 'cost_info' in msg:
                        cost_info = msg['cost_info']
                        if 'estimated_cost' in cost_info:
                            total_cost += cost_info['estimated_cost']
                
                st.caption(f"Session cost: ${total_cost:.4f}")
        
        # Clear conversation button
        if st.button("🔄 Start New Conversation"):
            st.session_state.conversation_history = []
            st.session_state.initialized = False
            st.rerun()

if __name__ == "__main__":
    main()