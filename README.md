# Police Transcriber

[![Version](https://img.shields.io/badge/version-v1.0.0--beta-blue)](https://github.com/andreipa/police-transcriber/releases)
[![Run Unit Tests](https://github.com/andreipa/police-transcriber/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/andreipa/police-transcriber/actions/workflows/tests.yaml)
[![Coverage](https://andreipa.github.io/police-transcriber/badges.svg)](https://github.com/andreipa/police-transcriber/actions/workflows/tests.yml)
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

(Add screenshots in the future)

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

Current version: **v1.0.0-beta**