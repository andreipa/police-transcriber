# Police Transcriber

[![Version](https://img.shields.io/badge/version-v1.0.0--beta-blue)](https://github.com/andreipa/police-transcriber/releases)
[![Run Unit Tests](https://github.com/andreipa/police-transcriber/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/andreipa/police-transcriber/actions/workflows/tests.yaml)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/andreipa/police-transcriber/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-beta-orange)](https://github.com/andreipa/police-transcriber)

Police Transcriber is a standalone, offline audio transcription tool designed for investigative and forensic environments. It detects and logs sensitive or illicit language in .mp3 files using AI-powered transcription via the Whisper model.

## 🚀 Features

- 🎙️ Transcribe .mp3 audio files locally
- 🔍 Detect and log sensitive keywords
- ⏱️ Real-time progress and timestamp tracking
- 📂 Supports individual files
- 💾 Offline-first: No internet connection required after model download
- 🧠 Powered by Faster-Whisper

## 📷 Screenshots

| <img src="/assets/images/screenshot-splash.png" width="300" title="Police Transcriber Application Loading Screen" alt="A dark-themed loading screen for the Police Transcriber application, displaying the official seal of the Polícia Civil of Rio Grande do Sul at the top center. Below the seal, bold text reads “Police Transcriber” followed by the subtitle “Automatic Detection of Illicit Conversations with AI.” The version number “v1.0.0-beta” is shown in smaller text. A blue progress bar below indicates 59% completion with the message “Baixando modelo large-v2…” (Downloading large-v2 model in Portuguese)." /> | <img src="/assets/images/screenshot-main.png" width="300" title="Transcriber Main Interface" alt="Main window of the Police Transcriber application with a dark interface. The header instructs the user to select a .mp3 file or a folder for transcription. Two prominent blue buttons labeled “Selecionar Arquivo” and “Selecionar Pasta” allow file or folder selection. Below, there is a large empty text area for displaying transcriptions. Beneath it, the current file status reads “Arquivo atual: Nenhum.” Two disabled buttons, “Iniciar Transcrição” and “Parar,” are shown. At the bottom, a progress bar is at 0%, with duration displayed as 00:00:00. The loaded model is indicated as “large-v2.”" /> | <img src="/assets/images/screenshot-word.png" width="300" title="Words Editor Window" alt="A dark-themed popup titled “Editar Palavras Sensíveis” (Edit Sensitive Words). It shows a text area labeled “Palavras Sensíveis Atuais” (Current Sensitive Words), which is currently empty, displaying the placeholder “(nenhuma palavra cadastrada)” (no word registered). Below the list are three action buttons: “Adicionar” (Add) in blue, “Editar” (Edit) in blue, and “Remover” (Remove) in red. At the bottom, there are two larger buttons: “Salvar” (Save) in blue and “Cancelar” (Cancel) in grey." /> | <img src="/assets/images/screenshot-about.png" width="300" title="About Police Transcriber" alt="A dark modal window titled “Sobre” (About) displaying the emblem of Polícia Civil of Rio Grande do Sul centered at the top. Below the emblem, the text reads “Police Transcriber” in bold white font. Underneath, the version is shown as “Versão: v1.0.0-beta” followed by the developer information: “Developed by TechDev Andrade Ltda.”" /> |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/andreipa/police-transcriber.git
   cd police-transcriber
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application** to automatically download the Whisper large-v2 model to `models/large-v2/`:
   ```bash
   python main.py
   ```

## ▶️ Running the Application

```bash
python main.py
```

## 📂 Folder Structure

```
.
├── assets/
│   ├── icons/
│   ├── images/
│   └── styles/
├── config.json
├── config.py
├── core/
├── data/
├── gui/
├── logs/
├── models/
├── output/
├── tests/
├── requirements.txt
├── main.py
└── README.md
```

## 🤝 Contributing

Pull requests and improvements are welcome! Please submit issues or feature requests via [GitHub Issues](https://github.com/andreipa/police-transcriber/issues). Note that modifications to the software require prior permission; contact contact@techdevandrade.com.

## 📄 License

MIT License – see [LICENSE](LICENSE) file for details. Usage is permitted without modification. For permission to modify or create derivative works, contact contact@techdevandrade.com.

## 🔗 Help

Need help? Visit the **Help** menu in the app or explore our user manuals in the GitHub Wiki: [English User Manual](https://github.com/andreipa/police-transcriber/wiki/User-Manual) | [Manual do Usuário (Português)](https://github.com/andreipa/police-transcriber/wiki/Manual-do-Usu%C3%A1rio). For
additional support, check out [GitHub Discussions](https://github.com/andreipa/police-transcriber/discussions).

## 🆙 Version

Current version: **v1.0.3-beta**