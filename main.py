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
    """Main Streamlit application with a robust streaming response implementation."""
    st.set_page_config(
        page_title="The Conversational Time Machine: J. Robert Oppenheimer",
        page_icon="⚛️",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
    <style>
        .main-header { text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 10px; margin-bottom: 2rem; }
        .user-message { background: #e3f2fd; padding: 0.5rem 1rem; border-radius: 10px; margin: 0.5rem 0; text-align: right; }
        .oppenheimer-message { background: #fff3e0; padding: 0.5rem 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 3px solid #ff9800; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="main-header"><h1>⚛️ The Conversational Time Machine</h1><h2>Speak with J. Robert Oppenheimer</h2></div>', unsafe_allow_html=True)

    # Initialize session state
    if 'time_machine' not in st.session_state:
        st.session_state.time_machine = ConversationalTimeMachine()
        st.session_state.conversation_history = []
        st.session_state.audio_job = None
        st.session_state.initialized = False

    # Generate introduction on first run
    if not st.session_state.initialized:
        with st.spinner("Initializing conversation..."):
            intro = st.session_state.time_machine.persona.get_introduction()
            st.session_state.conversation_history.append({
                'id': 'msg_intro', 'type': 'oppenheimer', 'content': intro, 'audio_path': None
            })
            st.session_state.initialized = True
            st.rerun()

    # --- Display conversation history and audio placeholders ---
    st.markdown("### Conversation History")
    placeholders = {}
    for i, message in enumerate(st.session_state.conversation_history):
        if message['type'] == 'user':
            st.markdown(f"<div class='user-message'><strong>You:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
        else: # Oppenheimer's message
            st.markdown(f"<div class='oppenheimer-message'><strong>Dr. Oppenheimer:</strong><br>{message['content']}</div>", unsafe_allow_html=True)
            
            # Create a placeholder for the audio player for this specific message
            placeholders[i] = st.empty()

    # --- User input section ---
    user_input = st.text_area("Your question:", key="user_input_box", placeholder="Ask about his life, the Manhattan Project...", height=100)
    if st.button("🎙️ Ask", type="primary"):
        if user_input:
            st.session_state.conversation_history.append({'type': 'user', 'content': user_input})
            
            # Trigger the text generation step
            with st.spinner("Dr. Oppenheimer is formulating his response..."):
                text_response = st.session_state.time_machine.persona.generate_response(user_input)
            
            # Add the text response and set up the audio job
            response_id = f"msg_{len(st.session_state.conversation_history)}"
            st.session_state.conversation_history.append({
                'id': response_id, 'type': 'oppenheimer', 'content': text_response, 'audio_path': 'pending'
            })
            st.session_state.audio_job = {'id': response_id, 'text': text_response}
            st.rerun()

    # --- Handle audio synthesis and update placeholders ---
    # This section runs after the main UI has been drawn
    for i, message in enumerate(st.session_state.conversation_history):
        if message['type'] == 'oppenheimer':
            audio_path = message.get('audio_path')
            
            # If this message is the one we need to synthesize
            if st.session_state.audio_job and st.session_state.audio_job['id'] == message.get('id'):
                with placeholders[i]:
                    with st.spinner("🎙️ Synthesizing voice..."):
                        audio_file = f"oppenheimer_response_{st.session_state.audio_job['id']}.wav"
                        new_audio_path = st.session_state.time_machine.tts.synthesize(st.session_state.audio_job['text'], audio_file)
                        
                        # Update the history and clear the job
                        message['audio_path'] = new_audio_path
                        st.session_state.audio_job = None
                        st.rerun()

            # If audio is ready, display it in the placeholder
            elif audio_path and os.path.exists(audio_path):
                with placeholders[i]:
                    st.audio(audio_path, format='audio/wav')

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### About This Experience")
        st.write("An AI-powered conversation with J. Robert Oppenheimer, featuring a locally cloned voice.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/JROppenheimer-LosAlamos.jpg/256px-JROppenheimer-LosAlamos.jpg", caption="J. Robert Oppenheimer")

        if st.button("🔄 Start New Conversation"):
            # A more robust way to clear state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()