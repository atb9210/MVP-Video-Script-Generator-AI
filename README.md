# Z.AI Image Generator Playground

Interfaccia Streamlit per testare l'API di generazione immagini Z.AI CogView-4.

## Setup

1. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

2. Avvia l'applicazione:
```bash
streamlit run app.py
```

## Funzionalità

- **Generazione immagini** tramite API Z.AI CogView-4
- **Configurazione parametri**: modello, qualità, dimensioni
- **Anteprima immediata** delle immagini generate
- **Metadata display** con informazioni sulla richiesta
- **Esempi pre-configurati** per test rapidi

## Parametri Supportati

- **Model**: cogview-4-250304
- **Quality**: standard (5-10s) o hd (~20s)
- **Size**: Varie dimensioni fino a 2048x2048
- **User ID**: Opzionale per content filtering (6-128 caratteri)

## Note

- Le URL delle immagini scadono dopo 30 giorni
- Salvare localmente le immagini importanti
- API key già configurata nel codice
