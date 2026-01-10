# Apps Directory

This directory contains the production-ready applications.

## 📱 Applications

### 1. **script_generator_gpt.py** - Main Application
**Status**: ✅ Production Ready  
**API**: OpenAI GPT (GPT-5.1, GPT-5, GPT-4.1)  
**Purpose**: Professional video script generation

**Features**:
- 🤖 Multiple GPT model support
- 🎬 Cinematic image prompts with context
- 📐 Camera angle specifications
- ⏱️ Duration-based scene optimization
- 📤 JSON export functionality
- 🔄 Session state persistence

**Usage**:
```bash
streamlit run apps/script_generator_gpt.py
```

### 2. **script_generator.py** - Alternative Application
**Status**: ✅ Production Ready  
**API**: Z.AI Agent API  
**Purpose**: Script generation using Z.AI

**Features**:
- 🤖 Z.AI Agent API integration
- 📝 Scene parsing and JSON output
- 🎭 Template-based script generation
- 📤 Export functionality

**Usage**:
```bash
streamlit run apps/script_generator.py
```

## 🚀 Quick Start

1. Set up your `.env` file with API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Run the main application: `streamlit run apps/script_generator_gpt.py`

## 🔐 Requirements

Both applications require:
- OpenAI API key (for GPT app)
- Z.AI API key (for Z.AI app)
- Environment variables configured in `.env`

## 📊 Comparison

| Feature | GPT App | Z.AI App |
|---------|---------|----------|
| AI Models | GPT-5.1, GPT-5, GPT-4.1 | Z.AI Agent |
| Image Prompts | ✅ Cinematic with context | ❌ Basic |
| Camera Angles | ✅ Detailed | ❌ Basic |
| Duration Control | ✅ Precise | ❌ Basic |
| JSON Export | ✅ Structured | ✅ Structured |
| Session Persistence | ✅ Full | ❌ Limited |

**Recommendation**: Use `script_generator_gpt.py` for production use.
