# Police Transcriber

![Logo](assets/images/logo-police.png)

**Police Transcriber** is a standalone, offline audio transcription tool designed for investigative and forensic environments. It detects and logs sensitive or illicit language in `.mp3` files using AI-powered transcription via the Whisper model.

---

## 🚀 Features

- 🎙️ Transcribe `.mp3` audio files locally
- 🔍 Detect and log sensitive keywords
- ⏱️ Real-time progress and timestamp tracking
- 📂 Supports individual files and folders
- ✅ Model auto-update checker
- 💾 Offline-first: No internet connection required
- 🧠 Powered by [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)

---

## 📷 Screenshots

> *(Add screenshots in the future)*

---

## 🔧 Installation

1. Clone the repository:

```bash
git clone https://github.com/andreipa/police-transcriber.git
cd police-transcriber
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download the Whisper model manually or let the app do it via **"Check for Model Update"**.

Place it in:

```
models/base/model.bin
```

---

## ▶️ Running the Application

```bash
python main.py
```

---

## 📂 Folder Structure

```
.
├── assets/
│   ├── icons/
│   ├── images/
│   └── styles/
├── config.py
├── core/
├── gui/
├── models/
├── output/
├── requirements.txt
├── main.py
└── README.md
```

---

## 🛠️ Model Update Host

The Whisper model is hosted here:  
👉 [Model Download (base)](https://github.com/your-username/police-transcriber/releases/latest/download/model.bin)

---

## 🤝 Contributing

Pull requests and improvements are welcome!

---

## 📄 License

MIT License – see [LICENSE](LICENSE) file for details.

---

## 🔗 Help

Need help? Visit the Help menu in the app or [GitHub Discussions](https://github.com/your-username/police-transcriber/discussions)
