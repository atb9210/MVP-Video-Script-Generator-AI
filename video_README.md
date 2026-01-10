# Z.AI Video Generator Playground

Interfaccia Streamlit per testare le API di generazione video Z.AI CogVideoX e Vidu.

## Setup

1. Installa le dipendenze (già installate dall'app immagini):
```bash
pip install -r requirements.txt
```

2. Avvia l'applicazione video:
```bash
streamlit run video_app.py
```

## Modelli Supportati

### CogVideoX-3
- **Text to Video**: Genera video da descrizioni testuali
- **Image to Video**: Genera video da immagini (1 immagine)
- **First & Last Frame**: Genera video tra due fotogrammi
- **Parametri**: quality/speed, audio, dimensioni, FPS, durata

### Vidu Models
- **Text to Video** (`viduq1-text`): Solo testo, stile general/anime
- **Image to Video** (`viduq1-image`): Da immagine a video
- **First & Last Frame** (`viduq1-start-end`): Tra due fotogrammi
- **Reference to Video** (`vidu2-reference`): Da 1-3 immagini di riferimento

## Funzionalità

- **Generazione asincrona** con polling automatico
- **Tracking task ID** per monitorare lo stato
- **Visualizzazione video** e cover image
- **Metadata display** completo
- **Auto-refresh** opzionale ogni 10 secondi
- **Esempi pre-configurati** per test rapidi

## Workflow

1. **Configura** il modello e i parametri
2. **Invia** la richiesta di generazione
3. **Monitora** lo stato con polling manuale o automatico
4. **Visualizza** il video quando completato

## Note

- La generazione video richiede **diversi minuti**
- I task ID vengono salvati in session state
- Supporta URL immagini e Base64 (dove specificato)
- API key già configurata nel codice
