import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# Configuration
API_KEY = "1b86194b06d2434491ff6895c8aa8a87.iEy5dom8ooEzPWQj"
AGENT_API_URL = "https://api.z.ai/api/v1/agents"
AGENT_RESULT_URL = "https://api.z.ai/api/v1/agents/async-result"

# Default templates
DEFAULT_SCRIPT_STRUCTURE = """- Fatti concreti - anno, evento, nome
- Tensione Crescente - ordina le scene nella mente
- Climax emotivo 
- Chiusura che lascia domande"""

DEFAULT_CHARACTER_STYLE = """a faceless human mannequin,
hyper-realistic 3D body,
smooth white featureless face,
no eyes, no mouth, no expression,"""

def create_script_generation_request(content, style, character_style, duration_minutes):
    """Create the request for script generation using Z.AI Agent API"""
    
    prompt = f"""Crea {max(2, duration_minutes)} scene video basate su questa storia:

{content}

Requisiti:
- Durata totale: {duration_minutes * 60} secondi
- Stile: {style}
- Personaggio: {character_style}

Per ogni scena genera: titolo, durata in secondi, prompt immagine, animazione, caption, sound effects.

Rispondi solo con JSON valido in questo formato:
{{"scenes": [{{"number": 1, "title": "...", "duration_seconds": 45, "image_prompt": "...", "animation_prompt": "...", "caption": "...", "sound_effect": "..."}}, {{"number": 2, "title": "...", "duration_seconds": 15, "image_prompt": "...", "animation_prompt": "...", "caption": "...", "sound_effect": "..."}}]}}

Solo JSON, niente altro."""

    payload = {
        "agent_id": "general_translation",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "custom_variables": {
            "source_lang": "it",
            "target_lang": "it",
            "strategy": "general"
        }
    }
    
    return payload

def call_agent_api(payload):
    """Call Z.AI Agent API for script generation"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(AGENT_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            try:
                error_data = response.json()
                st.error("Error Details:")
                st.json(error_data)
            except:
                st.error(f"Raw Response: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def parse_json_response(response_text):
    """Parse JSON response from AI"""
    try:
        # Try to extract JSON from response - look for the last JSON object
        import re
        
        # Find all JSON objects in the text
        json_matches = re.findall(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', response_text, re.DOTALL)
        
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if 'scenes' in data and data['scenes']:
                    return data['scenes']
            except:
                continue
        
        # Try more aggressive pattern matching
        json_pattern = r'\{[\s\S]*"scenes"[\s\S]*\[[\s\S]*\][\s\S]*\}'
        json_match = re.search(json_pattern, response_text)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            if 'scenes' in data:
                return data['scenes']
        
        # If still no luck, try parsing the whole response
        try:
            data = json.loads(response_text)
            if 'scenes' in data:
                return data['scenes']
        except:
            pass
        
        return []
        
    except Exception as e:
        st.error(f"Errore durante il parsing: {e}")
        st.error("Risposta ricevuta:")
        st.code(response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        return []

def main():
    st.set_page_config(
        page_title="Video Script Generator",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Video Script Generator")
    st.markdown("Crea script video professionali con scene complete usando AI")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📝 Input Parameters")
        
        # Content input
        content = st.text_area(
            "Contenuto Base",
            placeholder="Incolla qui la storia, trascrizione video YouTube, o qualsiasi contenuto da cui vu creare uno script...",
            height=200
        )
        
        # Duration input
        duration_minutes = st.number_input(
            "Durata Video (minuti)",
            min_value=1,
            max_value=30,
            value=5,
            step=1
        )
        
        # Style input with default
        st.subheader("Struttura Script")
        script_structure = st.text_area(
            "Struttura Script",
            value=DEFAULT_SCRIPT_STRUCTURE,
            height=100,
            help="Template per la struttura dello script"
        )
        
        # Character style with default
        st.subheader("Stile Personaggio")
        character_style = st.text_area(
            "Stile Personaggio Principale",
            value=DEFAULT_CHARACTER_STYLE,
            height=80,
            help="Descrizione del personaggio principale"
        )
        
        # Additional style
        video_style = st.text_input(
            "Stile Video",
            placeholder="es: cinematic, documentario, animazione, etc...",
            value="cinematic professional"
        )
        
        # Generate button
        generate_button = st.button("🚀 Genera Script", type="primary")
    
    # Main content area
    if generate_button:
        if not content.strip():
            st.error("Per favore inserisci del contenuto da cui generare lo script!")
            return
        
        with st.spinner("🤖 Sto generando lo script video..."):
            # Create API request
            payload = create_script_generation_request(
                content, video_style, character_style, duration_minutes
            )
            
            # Call API
            response = call_agent_api(payload)
            
            if response:
                # Extract the script content
                if 'choices' in response and len(response['choices']) > 0:
                    script_content = response['choices'][0]['messages'][0]['content']['text']
                    
                    # Parse JSON response
                    scenes = parse_json_response(script_content)
                    
                    if not scenes:
                        st.error("⚠️ Nessuna scena generata. Controlla la risposta dell'AI sopra.")
                        return
                    
                    # Display results
                    st.success(f"✅ Script generato con {len(scenes)} scene!")
                    
                    # Summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Scene Totali", len(scenes))
                    with col2:
                        total_duration = sum(scene.get('duration_seconds', 0) for scene in scenes)
                        st.metric("Durata Totale", f"{total_duration} secondi")
                    with col3:
                        st.metric("Target", f"{duration_minutes} minuti")
                    
                    # Display each scene
                    st.header("📋 Scene Generate")
                    
                    for i, scene in enumerate(scenes, 1):
                        with st.expander(f"🎬 Scena {scene.get('number', i)}: {scene.get('title', f'Scena {i}')}", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if scene.get('duration_seconds'):
                                    st.info(f"⏱️ Durata: {scene['duration_seconds']} secondi")
                                
                                if scene.get('image_prompt'):
                                    st.subheader("🖼️ Prompt Immagine")
                                    st.code(scene['image_prompt'], language='text')
                                    st.button(f"📋 Copia Prompt Immagine {i}", key=f"img_{i}")
                                
                                if scene.get('animation_prompt'):
                                    st.subheader("🎭 Prompt Animazione")
                                    st.code(scene['animation_prompt'], language='text')
                                    st.button(f"📋 Copia Animazione {i}", key=f"anim_{i}")
                            
                            with col2:
                                if scene.get('caption'):
                                    st.subheader("💬 Caption")
                                    st.write(scene['caption'])
                                    st.button(f"📋 Copia Caption {i}", key=f"cap_{i}")
                                
                                if scene.get('sound_effect'):
                                    st.subheader("🔊 Sound Effect")
                                    st.write(scene['sound_effect'])
                                    st.button(f"📋 Copia Sound {i}", key=f"sound_{i}")
                    
                    # Export options
                    st.header("💾 Esporta Script")
                    
                    # JSON export
                    script_json = json.dumps(scenes, indent=2, ensure_ascii=False)
                    st.download_button(
                        "📥 Download JSON",
                        script_json,
                        f"video_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json"
                    )
                    
                    # Text export
                    script_text = script_content
                    st.download_button(
                        "📥 Download Testo",
                        script_text,
                        f"video_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        "text/plain"
                    )
                
                else:
                    st.error("Formato risposta non valido")
                    st.json(response)
    
    # Instructions
    with st.expander("📖 Istruzioni", expanded=False):
        st.markdown("""
        ### Come usare questo tool:
        
        1. **Inserisci il contenuto**: Incolla la storia, trascrizione o qualsiasi testo
        2. **Imposta la durata**: Scegli quanti minuti deve durare il video
        3. **Personalizza lo stile**: Modifica la struttura e il personaggio se necessario
        4. **Genera**: Clicca il pulsante per creare lo script completo
        
        ### Cosa viene generato:
        - Scene numerate con durata specifica
        - Prompt per immagini AI
        - Istruzioni per animazioni
        - Caption quando necessario
        - Sound effects per atmosfera
        
        ### Export:
        - Formato JSON per integrazione con altri tool
        - Formato testo per lettura facile
        """)

if __name__ == "__main__":
    main()
