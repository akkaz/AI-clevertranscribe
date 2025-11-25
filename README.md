# AI Transcriber

A powerful, modern web application for transcribing and analyzing audio/video files using OpenAI's Whisper and GPT models.

![AI Transcriber UI](https://via.placeholder.com/800x450.png?text=AI+Transcriber+Dashboard)

## 🚀 Features

### Core Capabilities
- **🎙️ High-Accuracy Transcription**: Uses OpenAI's **Whisper-1** model for state-of-the-art speech-to-text conversion.
- **🧠 AI Analysis**: Automatically generates summaries, action items, and key takeaways using **GPT-4o** or **GPT-3.5**.
- **🏷️ Semantic Titles**: AI automatically generates concise, context-aware titles for your transcriptions (e.g., "Weekly Team Sync" instead of "recording_001.mp3").
- **📂 File Support**: Handles `.mp3`, `.mp4`, and `.mpeg` files with automatic audio extraction and chunking for large files.

### Modern UI/UX
- **✨ Sleek Interface**: Dark-themed, responsive design with glassmorphism effects.
- **📊 Activity Log**: Real-time status updates with color-coded indicators for uploads, processing, and errors.
- **📝 Interactive Editor**: 
  - Read-only view for transcriptions to preserve integrity.
  - Fully editable Analysis Reports.
  - **Dynamic To-Do Lists**: Add, edit, delete, and check off tasks directly in the UI.
- **📅 Smart History**: Jobs are automatically grouped by date (Today, Yesterday, This Week, etc.).

### Management & Settings
- **👥 Client Management**: Organize transcriptions by client.
- **⚙️ Customizable Settings**:
  - Choose between **GPT-4o** (Best Quality) and **GPT-3.5** (Faster/Cheaper).
  - Add custom prompts to guide the AI analysis.
  - Toggle language settings (Italian, English, Spanish, French, German).

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy (SQLite), OpenAI API.
- **Frontend**: HTML5, Vanilla CSS3 (Variables, Flexbox/Grid), Vanilla JavaScript (ES6+).
- **Processing**: FFmpeg for audio extraction and manipulation.

## 📋 Prerequisites

- **Python 3.8+**
- **FFmpeg**: Must be installed and available in your system PATH.
  - Ubuntu: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)
- **OpenAI API Key**: You need a valid API key with access to Whisper and GPT models.

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd transcribe
   ```

2. **Set up the environment**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Run the startup script**
   This script sets up the virtual environment, installs dependencies, and starts the server.
   ```bash
   ./start.sh
   ```
   
   *Alternatively, manually:*
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```

4. **Access the App**
   Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage Guide

1. **Upload**: Drag & drop a file or click to select. Choose language, client, and AI model.
2. **Process**: Click "Start Processing". Watch the **Activity Log** for real-time updates.
3. **Review**: Once complete, click the job in the sidebar history.
4. **Edit**: 
   - Click the **✏️ Edit** button to modify the report or manage to-do items.
   - Click **💾 Save** to persist changes.
5. **Manage**: Use the sidebar to filter by client or delete old transcriptions.

## 📂 Project Structure

```
transcribe/
├── backend/
│   ├── api/             # FastAPI routes
│   ├── services/        # Business logic (Transcription, Analysis)
│   ├── database.py      # SQLite models & connection
│   ├── main.py          # App entry point
│   └── ...
├── frontend/
│   ├── css/             # Styles (style.css)
│   ├── js/              # Logic (app.js)
│   └── index.html       # Main UI
├── uploads/             # Temp storage for uploads
├── outputs/             # Generated files
├── transcribe.db        # SQLite database
├── requirements.txt     # Python dependencies
└── start.sh             # Startup script
```

## ⚠️ Troubleshooting

- **FFmpeg Error**: Ensure FFmpeg is installed and in your PATH.
- **API Errors**: Check your API key in `.env` and ensure you have OpenAI credits.
- **Database Issues**: If you encounter schema errors, delete `transcribe.db` and restart the app to regenerate it.

## 📄 License

MIT License - feel free to use and modify for your own projects.
