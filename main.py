import streamlit as st
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import our custom modules
from oppenheimer_persona import OppenheimerPersona
from local_tts_service import LocalTTS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Acts as a container for our initialized services
class ConversationalTimeMachine:
    def __init__(self):
        self.persona = OppenheimerPersona()
        self.tts = LocalTTS()

def main():
    """Main Streamlit application with improved response streaming."""
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
    .user-message {
        background: #e3f2fd;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .oppenheimer-message {
        background: #fff3e0;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #ff9800;
    }
    .stSpinner > div > div {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""<div class="main-header">
        <h1>⚛️ The Conversational Time Machine</h1>
        <h2>Speak with J. Robert Oppenheimer</h2>
    </div>""", unsafe_allow_html=True)
    
    # Initialize session state
    if 'time_machine' not in st.session_state:
        st.session_state.time_machine = ConversationalTimeMachine()
        st.session_state.conversation_history = []
        st.session_state.processing_query = None
        st.session_state.audio_job = None
        st.session_state.initialized = False
        st.session_state.placeholders = {}

    # --- Display Logic ---
    st.markdown("### Conversation History")
    for message in st.session_state.conversation_history:
        if message['type'] == 'user':
            st.markdown(f"<div class='user-message'><strong>You:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='oppenheimer-message'><strong>Dr. Oppenheimer:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
            
            audio_path = message.get('audio_path')
            message_id = message.get('id')
            
            if message_id and message_id not in st.session_state.placeholders:
                st.session_state.placeholders[message_id] = st.empty()

            if audio_path == 'pending':
                st.session_state.placeholders[message_id].info("🎙️ Voice synthesis in progress...")
            elif audio_path and os.path.exists(audio_path):
                st.session_state.placeholders[message_id].audio(audio_path, format='audio/wav')

    # --- User Input Logic ---
    user_input = st.text_area("Your question:", "", height=100, placeholder="Ask about his life...")
    if st.button("🎙️ Ask", type="primary"):
        if user_input.strip():
            st.session_state.conversation_history.append({'type': 'user', 'content': user_input})
            st.session_state.processing_query = user_input
            st.rerun()

    # --- Processing State Machine ---
    if query := st.session_state.get('processing_query'):
        with st.spinner("Dr. Oppenheimer is formulating his response..."):
            text_response = st.session_state.time_machine.persona.generate_response(query)
        
        response_id = f"msg_{len(st.session_state.conversation_history)}"
        st.session_state.conversation_history.append({
            'id': response_id,
            'type': 'oppenheimer',
            'content': text_response,
            'audio_path': 'pending'
        })
        
        st.session_state.audio_job = {'id': response_id, 'text': text_response}
        st.session_state.processing_query = None
        st.rerun()

    if job := st.session_state.get('audio_job'):
        audio_file = f"oppenheimer_response_{job['id']}.wav"
        audio_path = st.session_state.time_machine.tts.synthesize(job['text'], audio_file)

        for msg in st.session_state.conversation_history:
            if msg.get('id') == job['id']:
                msg['audio_path'] = audio_path
                break
        
        st.session_state.audio_job = None
        st.rerun()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### About This Experience")
        st.write("An AI-powered conversation with J. Robert Oppenheimer, featuring a locally cloned voice.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/JROppenheimer-LosAlamos.jpg/256px-JROppenheimer-LosAlamos.jpg", caption="J. Robert Oppenheimer")

        if st.button("🔄 Start New Conversation"):
            st.session_state.conversation_history = []
            st.session_state.placeholders = {}
            st.rerun()

if __name__ == "__main__":
    main()