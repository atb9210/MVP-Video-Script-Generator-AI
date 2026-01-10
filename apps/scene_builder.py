import streamlit as st
import requests
import json
import time
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
KIE_API_KEY = os.getenv("KIE_API_KEY", "")

# Database functions
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('video_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            style TEXT,
            character_style TEXT,
            script_language TEXT,
            duration_minutes INTEGER,
            script_model TEXT,
            image_model TEXT,
            scenes TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_project(name, content, style, character_style, script_language, duration_minutes, script_model, image_model, scenes):
    """Save project to SQLite database"""
    conn = sqlite3.connect('video_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (name, content, style, character_style, script_language, duration_minutes, script_model, image_model, scenes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, content, style, character_style, script_language, duration_minutes, script_model, image_model, json.dumps(scenes)))
    conn.commit()
    conn.close()
    return True

def load_projects():
    """Load all projects from SQLite database"""
    conn = sqlite3.connect('video_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY updated_at DESC')
    projects = cursor.fetchall()
    conn.close()
    return projects

def load_project(project_id):
    """Load specific project from SQLite database"""
    conn = sqlite3.connect('video_projects.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()
    return project

def update_project(project_id, name, content, style, character_style, script_language, duration_minutes, script_model, image_model, scenes):
    """Update existing project"""
    conn = sqlite3.connect('video_projects.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE projects 
        SET name = ?, content = ?, style = ?, character_style = ?, script_language = ?, 
            duration_minutes = ?, script_model = ?, image_model = ?, scenes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (name, content, style, character_style, script_language, duration_minutes, script_model, image_model, json.dumps(scenes), project_id))
    conn.commit()
    conn.close()
    return True

def create_kie_image_task(prompt):
    """Create image generation task using Kie AI Nano Banana Pro"""
    
    import requests
    
    if not KIE_API_KEY:
        st.error("❌ KIE_API_KEY non configurata! Controlla il file .env")
        return None
    
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
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("data", {}).get("taskId")
            if task_id:
                return task_id
            else:
                st.error("❌ Nessun task ID nella risposta")
                return None
        else:
            st.error(f"❌ Errore Kie AI: {response.status_code}")
            st.code(response.text)
            return None
    except requests.exceptions.Timeout:
        st.error("❌ Timeout: la richiesta ha impiegato troppo tempo")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Errore di connessione a Kie AI")
        return None
    except Exception as e:
        st.error(f"❌ Errore connessione Kie AI: {str(e)}")
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
            st.error(f"❌ Errore query Kie AI: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Errore query Kie AI: {str(e)}")
        return None

def main():
    # Initialize database
    init_db()
    
    st.set_page_config(
        page_title="Scene Builder - Video Project Manager",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Scene Builder - Video Project Manager")
    st.markdown("Gestisci progetti video e genera scene con AI")
    st.info("🚀 **Scene Builder**: Carica progetti → Modifica scene → Genera immagini")
    
    # Initialize session state
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    if 'editing_scene_index' not in st.session_state:
        st.session_state.editing_scene_index = None
    
    # Sidebar for project management
    with st.sidebar:
        st.header("📂 Gestione Progetti")
        
        # Load existing projects
        projects = load_projects()
        if projects:
            st.subheader("Progetti Esistenti")
            project_options = [f"{proj[1]} - {proj[10][:10]}" for proj in projects]  # name - created_at
            selected_project = st.selectbox("Seleziona Progetto", [""] + project_options)
            
            if selected_project and selected_project != "":
                project_index = project_options.index(selected_project)
                project_id = projects[project_index][0]
                if st.button("📂 Carica Progetto", key="load_project"):
                    project_data = load_project(project_id)
                    if project_data:
                        st.session_state.current_project = {
                            'id': project_data[0],
                            'name': project_data[1],
                            'content': project_data[2],
                            'style': project_data[3],
                            'character_style': project_data[4],
                            'script_language': project_data[5],
                            'duration_minutes': project_data[6],
                            'script_model': project_data[7],
                            'image_model': project_data[8],
                            'scenes': json.loads(project_data[9])
                        }
                        st.success(f"✅ Progetto '{project_data[1]}' caricato!")
                        st.rerun()
    
    # Main content area
    if st.session_state.current_project:
        project = st.session_state.current_project
        
        # Project header
        st.header(f"📋 {project['name']}")
        
        # Project settings (editable)
        with st.expander("⚙️ Impostazioni Progetto", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                project['name'] = st.text_input("Nome Progetto", value=project['name'])
                project['style'] = st.text_input("Stile Video", value=project.get('style', 'cinematic professional'))
                project['character_style'] = st.text_area("Stile Personaggio", value=project.get('character_style', ''), height=100)
            
            with col2:
                project['script_language'] = st.selectbox("Lingua", ["italiano", "English"], index=["italiano", "English"].index(project.get('script_language', 'italiano')))
                project['duration_minutes'] = st.number_input("Durata (minuti)", value=project.get('duration_minutes', 5), min_value=1, max_value=30)
                project['script_model'] = st.selectbox("Modello Script", ["gpt-4", "gpt-3.5-turbo"], index=0)
                project['image_model'] = st.selectbox("Modello Immagini", ["nanobanapro (Kie)"], index=0)
            
            if st.button("💾 Salva Modifiche Progetto"):
                update_project(
                    project['id'], project['name'], project['content'], project['style'], 
                    project['character_style'], project['script_language'], project['duration_minutes'],
                    project['script_model'], project['image_model'], project['scenes']
                )
                st.success("✅ Progetto aggiornato!")
        
        # Scene grid
        st.header("🎬 Scene Grid")
        
        # Add new scene button
        if st.button("➕ Aggiungi Scena"):
            new_scene = {
                'number': len(project['scenes']) + 1,
                'title': f"Scena {len(project['scenes']) + 1}",
                'duration_seconds': 6,
                'image_prompt': "",
                'animation_prompt': "",
                'caption': "",
                'sound_effect': ""
            }
            project['scenes'].append(new_scene)
            st.success("✅ Nuova scena aggiunta!")
            st.rerun()
        
        # Display scenes in grid
        scenes_per_row = 3
        for i in range(0, len(project['scenes']), scenes_per_row):
            cols = st.columns(scenes_per_row)
            for j, scene in enumerate(project['scenes'][i:i+scenes_per_row]):
                with cols[j]:
                    scene_index = i + j
                    
                    # Scene card
                    with st.container():
                        st.markdown(f"### 🎬 Scena {scene['number']}")
                        st.markdown(f"**{scene['title']}**")
                        
                        # Edit scene button
                        if st.button(f"✏️ Modifica", key=f"edit_{scene_index}"):
                            st.session_state.editing_scene_index = scene_index
                            st.rerun()
                        
                        # Generate image button
                        if scene.get('image_prompt'):
                            if st.button(f"🎨 Genera Immagine", key=f"gen_img_{scene_index}"):
                                with st.spinner(f"🎨 Generando immagine per scena {scene['number']}..."):
                                    task_id = create_kie_image_task(scene['image_prompt'])
                                    if task_id:
                                        st.info(f"⏳ Task creato: {task_id}")
                                        
                                        # Poll for result
                                        for attempt in range(30):
                                            result = query_kie_task_status(task_id)
                                            if result:
                                                state = result.get('state')
                                                if state == 'success':
                                                    result_json = result.get('resultJson', '{}')
                                                    result_data = json.loads(result_json)
                                                    urls = result_data.get('resultUrls', [])
                                                    if urls:
                                                        scene['generated_image'] = urls[0]
                                                        st.image(urls[0], caption=f"Scena {scene['number']}")
                                                        st.success("🎉 Immagine generata!")
                                                    break
                                                elif state == 'fail':
                                                    st.error(f"❌ Errore: {result.get('failMsg', 'Errore')}")
                                                    break
                                            time.sleep(2)
                                        else:
                                            st.warning("⏱️ Timeout generazione")
                        
                        # Display generated image if exists
                        if scene.get('generated_image'):
                            st.image(scene['generated_image'], caption=f"Scena {scene['number']}", use_column_width=True)
                        
                        st.divider()
        
        # Scene editor modal
        if st.session_state.editing_scene_index is not None:
            scene_idx = st.session_state.editing_scene_index
            scene = project['scenes'][scene_idx]
            
            st.header(f"✏️ Modifica Scena {scene['number']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                scene['title'] = st.text_input("Titolo", value=scene['title'])
                scene['duration_seconds'] = st.number_input("Durata (secondi)", value=scene['duration_seconds'], min_value=1)
                scene['caption'] = st.text_area("Caption", value=scene['caption'], height=100)
                scene['sound_effect'] = st.text_input("Sound Effect", value=scene['sound_effect'])
            
            with col2:
                scene['image_prompt'] = st.text_area("Image Prompt", value=scene['image_prompt'], height=150)
                scene['animation_prompt'] = st.text_area("Animation Prompt", value=scene['animation_prompt'], height=150)
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 Salva Scena", type="primary"):
                    st.session_state.editing_scene_index = None
                    st.success("✅ Scena salvata!")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Annulla"):
                    st.session_state.editing_scene_index = None
                    st.rerun()
        
        # Save project button
        st.divider()
        if st.button("💾 Salva Progetto Completo", type="primary"):
            update_project(
                project['id'], project['name'], project['content'], project['style'], 
                project['character_style'], project['script_language'], project['duration_minutes'],
                project['script_model'], project['image_model'], project['scenes']
            )
            st.success("✅ Progetto salvato completamente!")
    
    else:
        st.info("👈 Seleziona un progetto dalla sidebar per iniziare")
        
        # Show database info
        if projects:
            st.subheader(f"📊 Database: {len(projects)} progetti disponibili")
        else:
            st.warning("⚠️ Nessun progetto nel database. Prima genera uno script con Script Generator!")

if __name__ == "__main__":
    main()
