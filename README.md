# doc2voice

A fully local macOS project to convert documents (PDF, DOCX, TXT) into natural, expressive speech using personalized voice cloning via Coqui XTTS-v2.

## ✨ Key Features

- **Local Voice Cloning**: Use your own voice (or any reference WAV) for zero-shot text-to-speech.
- **Multi-Format Support**: Extract text from PDF, DOCX, and plain TXT files.
- **Modern GUI**: Sleek macOS-native interface built with `customtkinter`.
- **Advanced CLI**: Powerful command-line interface for automation and bulk processing.
- **Expressiveness Controls**: Fine-tune `temperature` and `top_p` for animated or stable speech.
- **Voice Library**: Managed folder for standard/default voices.
- **Seamless Audio**: Automatic silence trimming and 50ms crossfading between chunks.
- **Apple Silicon Optimized**: Uses MPS (Metal Performance Shaders) for GPU acceleration.

## 🚀 Setup Instructions

### 1. Prerequisites
- **Python 3.10** (Recommended)
- **Homebrew** (For FFmpeg and Tkinter)

### 2. Install System Dependencies
```bash
# Required for audio merging
brew install ffmpeg

# Required for GUI support on Homebrew Python
brew install python-tk@3.10
```

### 3. Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 4. Install Python Packages
```bash
pip install -r requirements.txt
```

## 🎙️ Usage

### Option 1: Modern GUI
The easiest way to use the project:
```bash
python gui.py
```
- Select your document and voice reference.
- Adjust expressiveness sliders.
- Track real-time progress via the progress bar.

### Option 2: Command Line (CLI)
For batch processing or advanced usage:
```bash
python main.py --input path/to/doc.pdf --voice path/to/voice.wav --lang en --out output.wav
```
**Arguments:**
- `--input`: Path to PDF, TXT, or DOCX.
- `--voice`: Path to a 6-10s WAV voice sample (or multiple samples separated by commas for voice blending).
- `--lang`: Language code (e.g., `en`, `de`, `fr`, `es`).
- `--temperature`: 0.1 - 1.0 (default 0.75).
- `--top-p`: 0.1 - 1.0 (default 0.85).

## 📁 Voice Library
Manage your favorite voices by dropping WAV files into the `/voices` directory. They will automatically appear in the GUI's library dropdown.

## 🛠️ Troubleshooting

- **BeamSearchScorer Error**: Ensure you run `pip install transformers==4.33.0`.
- **Weights Only Load Failed**: Fixed in code; ensures PyTorch 2.6+ compatibility.
- **TorchCodec Error**: Ensure you run `pip install torchcodec`.
- **_tkinter Module Missing**: Run `brew install python-tk@3.10`.

## 📄 Licensing
This project uses **Coqui XTTS-v2** under the **Coqui Public Model License (CPML)**. It is intended for strictly **personal / non-commercial** purposes. Commercial use requires verification of licensing terms from Coqui.

---
*Created with ❤️ for high-quality local TTS.*
