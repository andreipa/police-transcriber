Police Transcriber

Police Transcriber is a standalone, offline audio transcription tool designed for investigative and forensic environments. It detects and logs sensitive or illicit language in .mp3 files using AI-powered transcription via the Whisper model.

🚀 Features

🎙️ Transcribe .mp3 audio files locally
🔍 Detect and log sensitive keywords
⏱️ Real-time progress and timestamp tracking
📂 Supports individual files
💾 Offline-first: No internet connection required after model download
🧠 Powered by Faster-Whisper

📷 Screenshots

(Add screenshots in the future)

🔧 Installation

Clone the repository:

git clone https://github.com/andreipa/police-transcriber.git
cd police-transcriber

Set up a virtual environment:

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

Install dependencies:

pip install -r requirements.txt

Run the application to automatically download the Whisper large-v2 model to models/large-v2/.

▶️ Running the Application
python main.py

📂 Folder Structure
.
├── assets/
│   ├── icons/
│   ├── images/
│   └── styles/
├── config.json
├── config.py
├── core/
├── gui/
├── logs/
├── models/
├── output/
├── requirements.txt
├── main.py
└── README.md

🤝 Contributing
Pull requests and improvements are welcome!

📄 License
MIT License – see LICENSE file for details.

🔗 Help
Need help? Visit the Help menu in the app or GitHub Discussions
