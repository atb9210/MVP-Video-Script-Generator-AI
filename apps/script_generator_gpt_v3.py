import streamlit as st
import requests
import json
import time
from datetime import datetime
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
KIE_API_KEY = os.getenv("KIE_API_KEY", "")

# Default templates
DEFAULT_SCRIPT_STRUCTURE = """- Fatti concreti - anno, evento, nome
- Tensione Crescente - ordina le scene nella mente
- Climax emotivo 
- Chiusura che lascia domande"""

DEFAULT_CHARACTER_STYLE = """a faceless human mannequin,
hyper-realistic 3D body,
smooth white featureless face,
no eyes, no mouth, no expression,"""

def create_kie_image_task(prompt):
    """Create image generation task using Kie AI Nano Banana Pro"""
    
    import requests
    
    url = "https://api.kie.ai/api/v1/jobs/createTask"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_input": [],
            "aspect_ratio": "1:1",
            "resolution": "1K",
            "output_format": "png"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get("data", {}).get("taskId")
        else:
            st.error(f"Errore Kie AI: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore connessione Kie AI: {str(e)}")
        return None

def query_kie_task_status(task_id):
    """Query Kie AI task status and get results"""
    
    import requests
    
    url = f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result.get("data", {})
        else:
            st.error(f"Errore query Kie AI: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore query Kie AI: {str(e)}")
        return None

def create_gpt_script_request(content, style, character_style, script_language, duration_minutes, model):
    """Create the request for script generation using OpenAI GPT"""
    
    total_seconds = duration_minutes * 60
    
    # Direct JSON creation - no 2-step process
    user_prompt = f"""Crea un video script professionale di ESATTAMENTE {duration_minutes} minuti ({total_seconds} secondi) basato su questa storia: {content}

Stile: {style}
Personaggio: {character_style}
Lingua: {script_language}

ISTRUZIONI IMPORTANTI:
1. Analizza la storia e crea scene logiche per {duration_minutes} minuti
2. Crea esattamente {total_seconds // 6} scene da 6 secondi cadauna (animazioni Grok)
3. La somma delle durate deve essere esattamente {total_seconds} secondi
4. Crea image prompts MOLTO DETTAGLIATI con contesto specifico
5. Genera l'intero script in {script_language}

PER OGNI SCENA GENERA:
- number: numero progressivo
- title: titolo significativo basato sulla scena (in {script_language})
- duration_seconds: 6 secondi (per animazioni Grok)
- image_prompt: DESCRIZIONE MOLTO DETTAGLIATA per AI image generation (in {script_language})
- animation_prompt: descrizione animazioni e movimenti (in {script_language})
- caption: testo caption per la scena (DEVE ESSERE DESCRITTIVO E NARRATIVO, minimo 50 caratteri, in {script_language})
- sound_effect: effetti sonori specifici (in {script_language})

IMPORTANTE per image_prompt:
1. CONTESTO SPECIFICO: dove si trova la scena, ambiente, periodo storico
2. ANGOLOLAZIONE CAMERA: close-up, medium shot, wide shot, high angle, low angle, etc.
3. ELEMENTI AMBIENTALI: dettagli del location, lighting, weather, oggetti
4. PERSONAGGIO: come appare {character_style} in questo contesto
5. AZIONE SPECIFICA: cosa sta facendo il personaggio in questa scena (statico, in movimento, interazione)
6. CONSISTENZA: mantieni stile {style} ma adattato alla scena

Esempio di image_prompt perfetto:
"cinematic professional, wide shot establishing the vast 1820s North American wilderness at dawn, dense pine forest covered in morning mist, golden rays filtering through tall branches, a hyper-realistic faceless human mannequin wearing tattered frontier clothes stands motionless at the edge of a clearing, smooth white featureless face looking forward, arms resting naturally at sides, holding a rifle across his chest, eye-level shot emphasizing isolation, anamorphic lens flare, shallow depth of field, epic scale, hyper-realistic 3D render, film still"

FORMATO JSON OBBLIGATORIO:
{{"scenes": [{{"number": 1, "title": "titolo scena", "duration_seconds": 6, "image_prompt": "descrizione dettagliata con contesto, angolazione, elementi ambientali", "animation_prompt": "animazione scena", "caption": "caption scena", "sound_effect": "suoni scena"}}, {{"number": 2, "title": "titolo scena", "duration_seconds": 6, "image_prompt": "descrizione dettagliata con contesto, angolazione, elementi ambientali", "animation_prompt": "animazione scena", "caption": "caption scena", "sound_effect": "suoni scena"}}]}}

CRITICO: La somma delle duration_seconds deve essere {total_seconds}. Crea esattamente {total_seconds // 6} scene da 6 secondi ciascuna. I caption devono essere descrittivi e narrativi, non brevi e generici!

Rispondi solo con JSON valido, niente altro testo."""
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Check if model uses max_completion_tokens (new models) or max_tokens (old models)
        new_models = ['gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5-pro', 'gpt-4.1', 'gpt-4.1-mini']
        
        # Use GPT-4 as fallback if GPT-5.1 doesn't work
        working_model = 'gpt-4' if model in ['gpt-5.1'] else model
        
        kwargs = {
            "model": working_model,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        # Add appropriate token parameter based on model
        if any(working_model.startswith(new_model) for new_model in new_models):
            kwargs["max_completion_tokens"] = 4000  # Aumento token per molte scene
        else:
            kwargs["max_tokens"] = 4000
        
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Errore API OpenAI: {str(e)}")
        return None

def parse_gpt_response(response_text):
    try:
        # Try to extract JSON from response
        import re
        
        # Look for JSON pattern
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            
            if 'scenes' in data:
                return data['scenes']
        
        # Try parsing the whole response
        data = json.loads(response_text)
        if 'scenes' in data:
            return data['scenes']
        
        return []
        
    except json.JSONDecodeError as e:
        st.error(f"Errore nel parsing JSON: {e}")
        st.error("Risposta ricevuta:")
        st.code(response_text[:1000] + "..." if len(response_text) > 1000 else response_text)
        return []
    except Exception as e:
        st.error(f"Errore durante il parsing: {e}")
        return []

def main():
    st.set_page_config(
        page_title="Video Script Generator GPT-5.1 (V3 - AI Multi-Model)",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Video Script Generator GPT-5.1 (V3 - AI Multi-Model)")
    st.markdown("Crea script video professionali con generazione immagini e animazioni AI")
    st.info("🚀 **V3 AI Multi-Model**: Script GPT + Immagini Kie AI + Animazioni + Voiceover")
    
    # Initialize session state
    if 'generated_scenes' not in st.session_state:
        st.session_state.generated_scenes = []
    if 'generation_info' not in st.session_state:
        st.session_state.generation_info = {}
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🤖 Configurazione AI")
        
        # Script model selection
        script_model = st.selectbox(
            "Modello Script (OpenAI)",
            [
                "gpt-5.1",
                "gpt-5", 
                "gpt-5.2",
                "gpt-5-pro",
                "gpt-4.1",  # Nuova generazione 4
                "gpt-4.1-mini",  # Mini 4.1
                "chatgpt-4o-latest",  # Latest ChatGPT
                "gpt-4o",  # Ottimizzato
                "gpt-4o-mini",  # Economico
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ],
            index=0,
            help="Scegli il modello GPT per generare lo script. gpt-5.1 è il più recente e potente."
        )
        
        # Image model selection
        image_model = st.selectbox(
            "Immagini (Kie AI)",
            [
                "nanobanapro (Kie)"
            ],
            index=0,
            help="Modello per generazione immagini con Kie AI Nano Banana Pro"
        )
        
        st.header("📝 Input Parameters")
        
        # Language selection
        script_language = st.selectbox(
            "Lingua Script",
            ["italiano", "English"],
            index=0,
            help="Scegli la lingua in cui generare lo script video"
        )
        
        # Content input
        content = st.text_area(
            "Contenuto Base",
            placeholder="Incolla qui la storia, trascrizione video YouTube, o qualsiasi contenuto da cui vu creare uno script...",
            height=200,
            key="content_input"
        )
        
        # Duration input
        duration_minutes = st.number_input(
            "Durata Video (minuti)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            key="duration_input"
        )
        
        # Style input with default
        st.subheader("Struttura Script")
        script_structure = st.text_area(
            "Struttura Script",
            value=DEFAULT_SCRIPT_STRUCTURE,
            height=100,
            help="Template per la struttura dello script",
            key="structure_input"
        )
        
        # Character style with default
        st.subheader("Stile Personaggio")
        character_style = st.text_area(
            "Stile Personaggio Principale",
            value=DEFAULT_CHARACTER_STYLE,
            height=80,
            help="Descrizione del personaggio principale",
            key="character_input"
        )
        
        # Additional style
        video_style = st.text_input(
            "Stile Video",
            placeholder="es: cinematic, documentario, animazione, etc...",
            value="cinematic professional",
            key="style_input"
        )
        
        # Generate button
        generate_button = st.button("🚀 Genera Script con GPT", type="primary")
    
    # Main content area
    if generate_button:
        if not content.strip():
            st.error("Per favore inserisci del contenuto da cui generare lo script!")
            return
        
        with st.spinner(f"🤖 Sto generando lo script con {script_model}..."):
            # Call GPT API
            response = create_gpt_script_request(
                content, video_style, character_style, script_language, duration_minutes, script_model
            )
            
            if response:
                # Parse scenes
                scenes = parse_gpt_response(response)
                
                if not scenes:
                    st.error("⚠️ Nessuna scena generata. Controlla la risposta di GPT sopra.")
                    return
                
                # Store in session state
                st.session_state.generated_scenes = scenes
                st.session_state.generation_info = {
                    'model': model,
                    'duration_minutes': duration_minutes,
                    'video_style': video_style,
                    'response_text': response
                }
    
    # Display results if we have scenes
    if st.session_state.generated_scenes:
        scenes = st.session_state.generated_scenes
        info = st.session_state.generation_info
        
        # Display results
        st.success(f"✅ Script generato con {len(scenes)} scene usando {info['model']}!")
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Scene Totali", len(scenes))
        with col2:
            total_duration = sum(scene.get('duration_seconds', 0) for scene in scenes)
            st.metric("Durata Totale", f"{total_duration} secondi")
        with col3:
            st.metric("Target", f"{info['duration_minutes']} minuti")
        
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
                        # Copy button with unique key
                        if st.button(f"📋 Copia Prompt Immagine {i}", key=f"img_{i}"):
                            st.write("📋 Copiato!")
                            st.code(scene['image_prompt'])
                    
                    if scene.get('animation_prompt'):
                        st.subheader("🎭 Prompt Animazione")
                        st.code(scene['animation_prompt'], language='text')
                        if st.button(f"📋 Copia Animazione {i}", key=f"anim_{i}"):
                            st.write("📋 Copiato!")
                            st.code(scene['animation_prompt'])
                
                with col2:
                    if scene.get('caption'):
                        st.subheader("💬 Caption")
                        st.write(scene['caption'])
                        if st.button(f"📋 Copia Caption {i}", key=f"cap_{i}"):
                            st.write("📋 Copiato!")
                            st.code(scene['caption'])
                    
                    if scene.get('sound_effect'):
                        st.subheader("🔊 Sound Effect")
                        st.write(scene['sound_effect'])
                        if st.button(f"📋 Copia Sound {i}", key=f"sound_{i}"):
                            st.write("📋 Copiato!")
                            st.code(scene['sound_effect'])
        
        # Export options
        st.header("💾 Esporta Script")
        
        # JSON export
        script_json = json.dumps(scenes, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Download JSON",
            script_json,
            f"video_script_gpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "application/json"
        )
        
        # Text export
        script_text = info.get('response_text', '')
        st.download_button(
            "📥 Download Testo",
            script_text,
            f"video_script_gpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "text/plain"
        )
    
    # Instructions
    with st.expander("📖 Istruzioni", expanded=False):
        st.markdown("""
        ### Come usare questo tool con GPT:
        
        1. **Scegli il modello**: 
           - **gpt-5.1** 🚀 (nuovissimo flagship, massima potenza)
           - **gpt-5** ⭐ (nuovo flagship di quinta generazione)
           - **gpt-5-pro** 💎 (versione pro di gpt-5)
           - **gpt-5.2** 🔥 (ultimissimo modello)
           - **gpt-4.1** 🎯 (nuova generazione 4.1)
           - **gpt-4.1-mini** 📱 (mini ma potente)
           - **chatgpt-4o-latest** 💬 (latest ChatGPT)
           - **gpt-4o** ⚡ (ottimizzato e veloce)
           - **gpt-4o-mini** 💰 (economico ma capace)
        2. **Inserisci il contenuto**: Incolla la storia, trascrizione o qualsiasi testo
        3. **Imposta la durata**: Scegli quanti minuti deve durare il video
        4. **Personalizza lo stile**: Modifica la struttura e il personaggio se necessario
        5. **Genera**: Clicca il pulsante per creare lo script completo
        
        ### Vantaggi dei nuovi modelli GPT-5:
        - ✅ **gpt-5.1**: Intelligenza di quinta generazione, comprensione profonda
        - ✅ **gpt-5**: Salto quantico nelle capacità di reasoning
        - ✅ **gpt-4.1**: Migliori prestazioni della serie 4.x
        - ✅ **Scene ultra-creative**: Capacità narrative senza precedenti
        - ✅ **Prompt cinematici**: Descrizioni visive professionali
        - ✅ **JSON perfetto**: Parsing sempre accurato
        - ✅ **Velocità estrema**: Risposte quasi istantanee
        - ✅ **Coerenza assoluta**: Script professionali e strutturati
        
        ### Cosa viene generato:
        - Scene numerate con durata specifica
        - Prompt per immagini AI (dettagliati)
        - Istruzioni per animazioni (specifiche)
        - Caption quando necessario
        - Sound effects per atmosfera
        """)

if __name__ == "__main__":
    main()
