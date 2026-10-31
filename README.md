# ZaCh — AI Document Assistant

**ZaCh** is a desktop-based AI document assistant built with Python and PySide6. It helps users interact with their documents through AI-powered conversations in a clean and intuitive interface.

## ✨ Features

- **AI-powered document conversations** — Ask questions and interact with your documents.
- **Retrieval-Augmented Generation (RAG)** — Retrieve relevant document content to provide context-aware answers.
- **Conversation management** — Create, open, and manage multiple conversations.
- **Document-based chat** — Start conversations using selected documents.
- **Modern desktop interface** — Built with PySide6.
- **Light and Dark themes** — Switch between visual themes.
- **Resizable sidebar** — Customize the workspace layout.
- **Configurable AI API** — Configure your own API settings.
- **Local data storage** — Store conversations and application data locally.

## 🖥️ Screenshots

<!-- Add application screenshots here -->

<!--
![ZaCh Home](images/screenshot-home.png)
![ZaCh Chat](images/screenshot-chat.png)
-->

## 🛠️ Tech Stack

- **Python 3.12**
- **PySide6** — Desktop GUI
- **SQLite** — Local database
- **RAG** — Context-aware document retrieval
- **Faster-Whisper** — Speech recognition support
- **QtAwesome** — Application icons
- **PyInstaller** — Application packaging
- **Inno Setup** — Windows installer

## 📦 Installation

### For Windows Users

1. Download the latest `ZaCh_Setup.exe` from the [GitHub Releases](../../releases) page.
2. Run the installer.
3. Follow the installation instructions.
4. Launch ZaCh.
5. Configure your own AI API credentials in the application settings.

No separate Python installation is required to use the packaged Windows version.

## 👨‍💻 Development Setup

### Requirements

- Windows
- Python 3.12
- Git

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ZaCh.git
cd ZaCh
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Environment

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

If the repository includes a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

## 🏗️ Building for Windows

ZaCh uses PyInstaller to package the application.

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --name ZaCh --icon "assets\images\logo.ico" --add-data "assets;assets" --add-data "app\docchat_release.db;app" --collect-all qtawesome --collect-all faster_whisper --collect-all ctranslate2 --collect-all onnxruntime main.py
```

The executable will be generated in:

```text
dist/ZaCh/ZaCh.exe
```

The Windows installer can then be generated using the included Inno Setup script:

```text
installer.iss
```

## 📁 Project Structure

```text
ZaCh/
│
├── app/
│   ├── ui/                 # User interface components
│   ├── database.py         # Database operations
│   ├── config.py           # Application configuration
│   ├── rag.py              # Document retrieval
│   ├── ai_service.py       # AI service integration
│   └── document_reader.py  # Document reading
│
├── assets/
│   └── images/             # Application images and icons
│
├── main.py                 # Application entry point
├── installer.iss          # Inno Setup configuration
└── README.md
```

## 🔐 Privacy & Data Storage

ZaCh stores application data locally on the user's computer.

On Windows, conversation data is stored in:

```text
%APPDATA%\ZaCh\docchat.db
```

Application configuration is stored separately in:

```text
~/.zach/config.json
```

Each user maintains their own local database and API configuration.

**Important:** Do not commit personal API keys, configuration files, private databases, or backup files to the public repository.

## 🚀 Roadmap

- [ ] Expand document format support
- [ ] Improve document retrieval and response quality
- [ ] Enhance application performance
- [ ] Improve the user experience
- [ ] Add more AI provider integrations

## 📄 License

No license has been specified yet.

If you plan to make this project open source, consider adding a `LICENSE` file to clarify how others may use, modify, and distribute your code.

---

**ZaCh — Your AI-powered document assistant.**
