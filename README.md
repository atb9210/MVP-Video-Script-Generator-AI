# Video Script Generator

Professional video script generation platform with AI integration.

## 📁 Project Structure

```
video-script-generator/
├── apps/                    # Production applications
│   ├── script_generator_gpt.py    # GPT-5.1 powered script generator (MAIN APP)
│   └── script_generator.py        # Z.AI Agent API script generator
├── playground/               # Testing and experimental apps
│   ├── app.py                     # Z.AI Image Generator Playground
│   └── video_app.py               # Z.AI Video Generator Playground
├── docs/                     # Documentation and resources
│   ├── *.md                       # API documentation
│   └── *.png                      # Images and assets
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── requirements.txt          # Python dependencies
```

## 🚀 Main Application

### **GPT-5.1 Script Generator** (`apps/script_generator_gpt.py`)
- **Purpose**: Professional video script generation using OpenAI GPT models
- **Features**:
  - GPT-5.1, GPT-5, GPT-4.1 model support
  - Cinematic image prompts with context and camera angles
  - Scene-based video script structure
  - Duration-based scene optimization
  - JSON export functionality

### **Z.AI Script Generator** (`apps/script_generator.py`)
- **Purpose**: Alternative script generator using Z.AI Agent API
- **Features**:
  - Z.AI Agent API integration
  - Scene parsing and JSON output
  - Template-based script generation

## 🧪 Playground Applications

### **Image Generator** (`playground/app.py`)
- **Purpose**: Test Z.AI CogView-4 image generation API
- **Status**: Experimental/Testing

### **Video Generator** (`playground/video_app.py`)
- **Purpose**: Test Z.AI CogVideoX and Vidu video generation APIs
- **Status**: Experimental/Testing

## 📚 Documentation

Complete API documentation and guides available in `/docs/`:
- API integration guides
- Chat history examples
- File upload instructions
- Retrieval result documentation

## 🔧 Setup

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Add your API keys to `.env`
4. Install dependencies: `pip install -r requirements.txt`
5. Run main app: `streamlit run apps/script_generator_gpt.py`

## 🎯 Usage

The main application (`apps/script_generator_gpt.py`) provides:
- Professional script generation
- Cinematic scene descriptions
- AI-ready image prompts
- Export functionality
- Multiple model support

## 🔒 Security

- Private repository
- Environment variables for API keys
- Git ignore protection for sensitive files
- Secure API key management
