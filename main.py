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
    
    # Modern minimalistic CSS with dark/light theme support
    st.markdown("""
    <style>
        /* Import Inter font for modern look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        /* Enhanced light theme with more visual appeal */
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --bg-subtle: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --border-color: #e2e8f0;
            --border-light: #f1f5f9;
            --accent-color: #3b82f6;
            --accent-hover: #2563eb;
            --accent-light: #dbeafe;
            --user-bg: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            --user-border: #3b82f6;
            --user-text: #1e40af;
            --assistant-bg: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            --assistant-border: #d97706;
            --assistant-text: #92400e;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            --glow: 0 0 20px rgba(59, 130, 246, 0.3);
        }
        
        /* Override Streamlit's automatic dark theme detection - force light theme */
        html, body, .stApp {
            background-color: #ffffff !important;
            color: #1e293b !important;
        }
        
        /* Dark theme only when explicitly set by user */
        .stApp[data-theme="dark"] {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --border-color: #475569;
            --user-bg: #1e3a8a;
            --user-border: #3b82f6;
            --assistant-bg: #422006;
            --assistant-border: #f59e0b;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        }
        
        /* Global app styling */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Enhanced header with visual appeal */
        .app-header {
            position: relative;
            text-align: center;
            padding: 4rem 2rem 3rem 2rem;
            margin-bottom: 3rem;
            background: var(--bg-gradient);
            background-size: 200% 200%;
            animation: gradientShift 8s ease infinite;
            border-radius: 0 0 2rem 2rem;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
        }
        
        .app-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            pointer-events: none;
        }
        
        .app-title {
            font-size: 3.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
            letter-spacing: -0.03em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            z-index: 2;
        }
        
        .app-subtitle {
            font-size: 1.25rem;
            color: rgba(255,255,255,0.9);
            font-weight: 400;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.7;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            position: relative;
            z-index: 2;
        }
        
        /* Decorative elements */
        .app-header::after {
            content: '⚛';
            position: absolute;
            top: 1rem;
            right: 2rem;
            font-size: 2rem;
            opacity: 0.3;
            animation: float 3s ease-in-out infinite;
        }
        
        /* Enhanced chat container */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
        }
        
        /* Enhanced message styling */
        .message {
            margin-bottom: 2rem;
            opacity: 0;
            animation: fadeInUp 0.6s ease forwards;
            position: relative;
        }
        
        .message-user {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
        }
        
        .message-assistant {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 2.5rem;
            position: relative;
        }
        
        .message-assistant::before {
            content: 'Dr. Oppenheimer';
            position: absolute;
            top: -1.5rem;
            left: 0;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--assistant-text);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .message-user::before {
            content: 'You';
            position: absolute;
            top: -1.5rem;
            right: 0;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--user-text);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .message-content {
            max-width: 80%;
            padding: 1.5rem 2rem;
            border-radius: 1.5rem;
            font-size: 1rem;
            line-height: 1.7;
            box-shadow: var(--shadow-md);
            position: relative;
            backdrop-filter: blur(10px);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .message-content:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .message-user .message-content {
            background: var(--user-bg);
            border-color: var(--user-border);
            color: var(--user-text);
            border-bottom-right-radius: 0.5rem;
            position: relative;
        }
        
        .message-user .message-content::after {
            content: '';
            position: absolute;
            bottom: 0;
            right: -8px;
            width: 0;
            height: 0;
            border: 8px solid transparent;
            border-top-color: var(--user-border);
            border-left-color: var(--user-border);
        }
        
        .message-assistant .message-content {
            background: var(--assistant-bg);
            border-color: var(--assistant-border);
            color: var(--assistant-text);
            border-bottom-left-radius: 0.5rem;
            position: relative;
        }
        
        .message-assistant .message-content::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: -8px;
            width: 0;
            height: 0;
            border: 8px solid transparent;
            border-top-color: var(--assistant-border);
            border-right-color: var(--assistant-border);
        }
        
        .message-label {
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Input section styling */
        
        /* Textarea styling */
        .stTextArea > div > div > textarea {
            background: var(--bg-secondary) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 1rem !important;
            color: var(--text-primary) !important;
            font-family: inherit !important;
            font-size: 1rem !important;
            padding: 1rem 1.5rem !important;
            resize: none !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow) !important;
            outline: none !important;
        }
        
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-color) !important;
            background: var(--bg-primary) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), var(--shadow) !important;
            outline: none !important;
        }
        
        .stTextArea > div > div > textarea::placeholder {
            color: var(--text-muted) !important;
            font-style: italic;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 1rem !important;
            padding: 1rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow-md) !important;
            height: auto !important;
            min-height: 56px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-lg), var(--glow) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Enhanced loading states */
        .loading-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            color: var(--text-secondary);
            font-size: 0.95rem;
            padding: 2rem;
            margin: 2rem 0;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%);
            border-radius: 1rem;
            border: 1px solid var(--accent-light);
            backdrop-filter: blur(10px);
        }
        
        .typing-dots {
            display: flex;
            gap: 0.5rem;
        }
        
        .typing-dots span {
            width: 10px;
            height: 10px;
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--accent-hover) 100%);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
            box-shadow: var(--shadow-sm);
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }
        
        /* Enhanced audio player styling */
        .stAudio {
            margin-top: 1rem;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 1rem;
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-light);
        }
        
        .stAudio > div {
            background: transparent !important;
            border: none !important;
            border-radius: 1rem !important;
        }
        
        /* Enhanced animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes typing {
            0%, 80%, 100% { 
                transform: scale(0.6); 
                opacity: 0.4; 
            }
            40% { 
                transform: scale(1.2); 
                opacity: 1; 
            }
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-10px) rotate(180deg); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .app-title { font-size: 2rem; }
            .app-subtitle { font-size: 1rem; }
            .message-content { max-width: 95%; }
            .input-section { padding: 1rem; }
        }
        
        /* Streamlit element overrides for light theme */
        .stTextArea > div > div > textarea::placeholder {
            color: #94a3b8 !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg { 
            background: #f8fafc !important; 
        }
        .css-1d391kg .css-1v0mbdj { 
            color: #1e293b !important; 
        }
        
        /* Spinner styling */
        .stSpinner > div {
            border-color: #e2e8f0 #3b82f6 #e2e8f0 #e2e8f0 !important;
        }
        
        /* Override any dark theme elements */
        .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: var(--text-primary) !important;
        }
        
        /* Audio player styling */
        .stAudio > div {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
        }
        
        /* Container backgrounds */
        .block-container {
            background: transparent !important;
        }
        
        /* Ensure all text is visible in light theme */
        * {
            color: inherit;
        }
        
        /* Force light theme for all Streamlit components */
        .stSelectbox > div > div {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }
        
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state first
    if 'time_machine' not in st.session_state:
        st.session_state.time_machine = ConversationalTimeMachine()
        st.session_state.conversation_history = []
        st.session_state.audio_job = None
        st.session_state.initialized = False
        st.session_state.user_input = ""  # For clearing input after submit
    
    # Add JavaScript for enter-to-send functionality
    st.markdown("""
    <script>
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const buttons = document.querySelectorAll('[data-testid="stButton"] button');
                if (buttons.length > 0) {
                    buttons[0].click();
                }
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Modern header with smart copy
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">The Oppenheimer Conversations</h1>
        <p class="app-subtitle">
            Step into history and engage with the mind that changed the world forever. 
            Ask J. Robert Oppenheimer about science, philosophy, moral responsibility, 
            and the weight of discovery.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate introduction on first run
    if not st.session_state.initialized:
        with st.spinner("Awakening the consciousness of history..."):
            intro = st.session_state.time_machine.persona.get_introduction()
            st.session_state.conversation_history.append({
                'id': 'msg_intro', 'type': 'oppenheimer', 'content': intro, 'audio_path': None
            })
            st.session_state.initialized = True
            st.rerun()

    # --- Clean conversation display ---
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for i, message in enumerate(st.session_state.conversation_history):
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="message message-user">
                    <div class="message-content">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:  # Oppenheimer's message
                st.markdown(f"""
                <div class="message message-assistant">
                    <div class="message-content">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show audio player if audio exists
                audio_path = message.get('audio_path')
                if audio_path and audio_path != 'pending' and os.path.exists(audio_path):
                    st.audio(audio_path, format='audio/wav')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Input section ---
    st.markdown("### Ask Dr. Oppenheimer")
    
    input_col1, input_col2 = st.columns([4, 1])
    
    with input_col1:
        user_input = st.text_area(
            "Your question:", 
            value=st.session_state.user_input,
            key="user_input_box", 
            placeholder="Ask about the Trinity test, quantum mechanics, or his philosophical reflections...", 
            height=100,
            label_visibility="collapsed"
        )
    
    with input_col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Handle input submission
    if send_button and user_input.strip():
        # Add user message to history
        st.session_state.conversation_history.append({'type': 'user', 'content': user_input.strip()})
        
        # Clear the input field for next message
        st.session_state.user_input = ""
        
        # Show loading state while generating response
        with st.spinner("Dr. Oppenheimer is contemplating your question..."):
            # Generate text response
            text_response = st.session_state.time_machine.persona.generate_response(user_input.strip())
            
            # Add response to history with pending audio
            response_message = {
                'type': 'oppenheimer', 
                'content': text_response, 
                'audio_path': 'pending',
                'id': f"msg_{len(st.session_state.conversation_history)}"
            }
            st.session_state.conversation_history.append(response_message)
        
        # Rerun to show the text response immediately
        st.rerun()

    # Handle audio synthesis for pending messages
    for message in st.session_state.conversation_history:
        if message['type'] == 'oppenheimer' and message.get('audio_path') == 'pending':
            # Generate audio in background
            audio_file = f"oppenheimer_response_{message['id']}.wav"
            try:
                with st.spinner("Synthesizing voice..."):
                    audio_path = st.session_state.time_machine.tts.synthesize(message['content'], audio_file)
                    message['audio_path'] = audio_path if audio_path else None
                st.rerun()
            except Exception as e:
                logger.error(f"Audio synthesis failed: {e}")
                message['audio_path'] = None
    
    # --- Enhanced Sidebar ---
    with st.sidebar:
        st.markdown("## About")
        st.markdown("""
        Experience history through conversation. This AI recreates J. Robert Oppenheimer's 
        voice, knowledge, and perspective from his lifetime (1904-1967).
        
        **What to explore:**
        - The Trinity test and Manhattan Project
        - Nuclear physics and quantum mechanics  
        - Moral philosophy and responsibility
        - Relationships with Einstein, Bohr, and other scientists
        - The security hearing and its aftermath
        - Sanskrit literature and the Bhagavad Gita
        """)
        
        st.markdown("---")
        
        if st.button("Start Fresh Conversation", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <small>
        <strong>Technical Details:</strong><br>
        • AI Model: Google Gemini 2.5 Flash<br>
        • Voice: Coqui TTS with voice cloning<br>
        • Knowledge: RAG with historical documents<br>
        • Response optimization for cost and quality
        </small>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()