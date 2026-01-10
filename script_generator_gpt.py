import streamlit as st
import requests
import json
import time
from datetime import datetime
import openai
import os

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Default templates
DEFAULT_SCRIPT_STRUCTURE = """- Fatti concreti - anno, evento, nome
- Tensione Crescente - ordina le scene nella mente
- Climax emotivo 
- Chiusura che lascia domande"""

DEFAULT_CHARACTER_STYLE = """a faceless human mannequin,
hyper-realistic 3D body,
smooth white featureless face,
no eyes, no mouth, no expression,"""

def create_gpt_script_request(content, style, character_style, duration_minutes, model):
    """Create the request for script generation using OpenAI GPT"""
    
    total_seconds = duration_minutes * 60
    
    # Direct JSON creation - no 2-step process
    user_prompt = f"""Crea un video script professionale di ESATTAMENTE {duration_minutes} minuti ({total_seconds} secondi) basato su questa storia: {content}

Stile: {style}
Personaggio: {character_style}

ISTRUZIONI IMPORTANTI:
1. Analizza la storia e crea scene logiche per {duration_minutes} minuti
2. Decidi tu il numero ottimale di scene (1-6 scene a seconda della durata)
3. La somma delle durate deve essere esattamente {total_seconds} secondi
4. Crea image prompts MOLTO DETTAGLIATI con contesto specifico

PER OGNI SCENA GENERA:
- number: numero progressivo
- title: titolo significativo basato sulla scena
- duration_seconds: durata in secondi (somma = {total_seconds})
- image_prompt: DESCRIZIONE MOLTO DETTAGLIATA per AI image generation
- animation_prompt: descrizione animazioni e movimenti
- caption: testo caption per la scena
- sound_effect: effetti sonori specifici

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
{{"scenes": [{{"number": 1, "title": "titolo scena", "duration_seconds": 60, "image_prompt": "descrizione dettagliata con contesto, angolazione, elementi ambientali", "animation_prompt": "animazione scena", "caption": "caption scena", "sound_effect": "suoni scena"}}, {{"number": 2, "title": "titolo scena", "duration_seconds": 30, "image_prompt": "descrizione dettagliata con contesto, angolazione, elementi ambientali", "animation_prompt": "animazione scena", "caption": "caption scena", "sound_effect": "suoni scena"}}]}}

CRITICO: La somma delle duration_seconds deve essere {total_seconds}. Adatta il numero di scene e le durate di conseguenza.

Rispondi solo con JSON valido, niente altro testo."""

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Check if model uses max_completion_tokens (new models) or max_tokens (old models)
        new_models = ['gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5-pro', 'gpt-4.1', 'gpt-4.1-mini']
        
        kwargs = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        # Add appropriate token parameter based on model
        if any(model.startswith(new_model) for new_model in new_models):
            kwargs["max_completion_tokens"] = 3000  # Aumento token per prompt dettagliati
        else:
            kwargs["max_tokens"] = 3000
        
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Errore API OpenAI: {str(e)}")
        return None

def parse_gpt_response(response_text):
    """Parse JSON response from GPT"""
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
        page_title="Video Script Generator (GPT)",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Video Script Generator (GPT Edition)")
    st.markdown("Crea script video professionali con scene complete usando OpenAI GPT")
    
    # Initialize session state
    if 'generated_scenes' not in st.session_state:
        st.session_state.generated_scenes = []
    if 'generation_info' not in st.session_state:
        st.session_state.generation_info = {}
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🤖 Configurazione GPT")
        
        # Model selection
        model = st.selectbox(
            "Modello GPT",
            options=[
                "gpt-5.1",  # Nuovissimo flagship
                "gpt-5",  # Nuovo flagship
                "gpt-5-pro",  # Versione pro
                "gpt-5.2",  # Ultimissimo
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
            help="Scegli il modello GPT. gpt-5.1 è il più recente e potente."
        )
        
        st.header("📝 Input Parameters")
        
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
        
        with st.spinner(f"🤖 Sto generando lo script con {model}..."):
            # Call GPT API
            response = create_gpt_script_request(
                content, video_style, character_style, duration_minutes, model
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
