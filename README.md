# The Conversational Time Machine: J. Robert Oppenheimer

An AI-powered interactive application that allows users to have voice-based conversations with J. Robert Oppenheimer, the "Father of the Atomic Bomb." This project combines advanced natural language processing, retrieval-augmented generation (RAG), and text-to-speech synthesis to create an immersive historical conversation experience.

## 🎯 Project Overview

This application creates a believable and engaging persona of J. Robert Oppenheimer that can answer questions based on historical context. Users can interact with the AI through text input and receive both written and spoken responses in a voice that approximates Oppenheimer's characteristics.

### Key Features

- **Historical Accuracy**: Knowledge base grounded in Oppenheimer's actual biography, quotes, and historical context
- **Authentic Persona**: AI responds in Oppenheimer's characteristic speaking style and from his historical perspective (1904-1967)
- **Voice Synthesis**: Uses Google Cloud TTS with voice cloning to approximate Oppenheimer's voice characteristics
- **Interactive Interface**: Clean, user-friendly Streamlit web application
- **RAG Architecture**: Retrieval-Augmented Generation ensures factually grounded responses

## 🏗️ Architecture

### Components

1. **Knowledge Base (`knowledge_base/`)**
   - `oppenheimer_biography.txt`: Comprehensive biographical information
   - `oppenheimer_quotes.txt`: Collection of famous quotes and speeches
   - `historical_context.txt`: World War II, Manhattan Project, and Cold War context

2. **RAG System (`rag_system.py`)**
   - ChromaDB vector database for semantic search
   - Sentence transformers for embeddings
   - Context retrieval and relevance ranking

3. **Persona Engine (`oppenheimer_persona.py`)**
   - Google Gemini 1.5 Flash for response generation
   - Sophisticated prompt engineering for authentic persona
   - Conversation history management

4. **TTS Service (`tts_service.py`)**
   - Google Cloud Text-to-Speech API
   - Voice cloning configuration for Oppenheimer's characteristics
   - Audio formatting and style optimization

5. **Main Application (`main.py`)**
   - Streamlit web interface
   - Conversation management
   - Audio playback integration

## 🚀 Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud account with TTS API enabled
- Gemini API key

### Step 1: Clone and Install Dependencies

```bash
# Create project directory
mkdir oppenheimer-time-machine
cd oppenheimer-time-machine

# Install required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Project ID
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
```

### Step 3: Set Up Google Cloud Authentication

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### Step 4: Initialize the Knowledge Base

```bash
# Run the RAG system to build the vector database
python rag_system.py
```

## 🎮 Usage

### Running the Application

```bash
# Start the Streamlit application
streamlit run main.py
```

The application will open in your web browser at `http://localhost:8501`.

### Interacting with Oppenheimer

1. **Ask Questions**: Type questions about Oppenheimer's life, the Manhattan Project, nuclear physics, or his philosophical views
2. **Listen to Responses**: Each response includes both text and synthesized speech
3. **Explore History**: Ask about specific events, relationships, or his thoughts on various topics

### Sample Questions

- "What do you remember about the Trinity test?"
- "Do you regret creating the atomic bomb?"
- "Tell me about your time at Los Alamos"
- "What did the Bhagavad Gita mean to you?"
- "What was your relationship with Einstein like?"
- "How do you feel about nuclear proliferation?"

## 🧠 Technical Details

### Knowledge Grounding

The AI's responses are grounded in factual information from:
- Comprehensive biographical data
- Historical quotes and speeches
- Manhattan Project documentation
- Post-war interviews and writings
- Security hearing transcripts

### Persona Engineering

The persona is designed to:
- Speak from Oppenheimer's first-person perspective
- Reference his actual experiences and relationships
- Maintain his characteristic speaking style (formal, philosophical, literary)
- Express his complex feelings about nuclear weapons
- Stay within his historical knowledge (pre-1967)

### Voice Characteristics

The TTS system is configured to match Oppenheimer's voice:
- Mature, authoritative male voice
- Slightly slower speaking rate for gravitas
- Lower pitch for deeper tone
- Emphasis on scientific terminology
- Pauses for philosophical reflection

## 📁 Project Structure

```
oppenheimer-time-machine/
├── knowledge_base/
│   ├── oppenheimer_biography.txt
│   ├── oppenheimer_quotes.txt
│   └── historical_context.txt
├── chroma_db/                    # Vector database (auto-generated)
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── rag_system.py                # RAG implementation
├── tts_service.py               # Text-to-speech service
├── oppenheimer_persona.py       # AI persona engine
├── main.py                      # Streamlit application
└── README.md                    # This file
```

## 🔧 Testing

### Test Individual Components

```bash
# Test RAG system
python rag_system.py

# Test TTS service
python tts_service.py

# Test persona engine
python oppenheimer_persona.py
```

### Test Questions for Validation

- Historical accuracy: Ask about specific dates, events, people
- Persona consistency: Check speaking style and personality
- Knowledge boundaries: Ask about post-1967 events (should decline)
- Technical accuracy: Questions about nuclear physics and the Manhattan Project

## 🎨 Customization

### Modifying the Voice

Edit `tts_service.py` to change voice characteristics:

```python
self.voice_config = {
    "languageCode": "en-US",
    "name": "en-US-Chirp3-HD-Algieba",  # Change voice model
    "voiceClone": {}
}

self.audio_config = {
    "speakingRate": 0.9,  # Adjust speaking speed
    "pitch": -2.0,        # Adjust pitch
    # ... other settings
}
```

### Expanding the Knowledge Base

Add new text files to the `knowledge_base/` directory and run:

```bash
python rag_system.py
```

### Adjusting the Persona

Modify the system prompt in `oppenheimer_persona.py` to change personality traits, speaking style, or focus areas.

## 🚨 Known Limitations

1. **Voice Cloning**: Uses approximation rather than true voice cloning due to limited historical audio
2. **Response Time**: TTS generation may take several seconds for longer responses
3. **Historical Knowledge**: Limited to documented historical information
4. **Emotional Range**: AI may not fully capture the emotional complexity of the historical figure

## 🔒 Security and Privacy

- API keys should be kept secure and not committed to version control
- Audio files are temporarily stored locally and can be automatically cleaned up
- No user data is transmitted beyond the necessary API calls

## 📜 License and Ethics

This project is for educational and historical purposes. It aims to:
- Preserve historical knowledge and perspective
- Educate users about nuclear history and scientific responsibility
- Demonstrate advanced AI applications in historical simulation

The project respects the memory and legacy of J. Robert Oppenheimer while acknowledging the complex moral questions surrounding nuclear weapons.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📚 References

- [J. Robert Oppenheimer - Wikipedia](https://en.wikipedia.org/wiki/J._Robert_Oppenheimer)
- [Atomic Heritage Foundation](https://ahf.nuclearmuseum.org/)
- [The Manhattan Project](https://www.manhattanprojectvoices.org/)
- [Google Cloud Text-to-Speech API](https://cloud.google.com/text-to-speech)
- [Google Gemini API](https://ai.google.dev/)

## 🔗 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all API keys and permissions are correctly configured
4. Test individual components to isolate issues