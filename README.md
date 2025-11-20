# MP4 Transcription Script

A Python command-line tool that transcribes Italian audio from MP4 video files using OpenAI's Whisper API. The script automatically handles large files by intelligently splitting them into chunks that comply with the Whisper API's 25 MB file size limit.

## Features

- 🎯 **Automatic chunking**: Handles files of any size by splitting large audio into manageable chunks
- 🇮🇹 **Italian language support**: Optimized for Italian audio transcription
- 🔄 **Retry logic**: Automatic retry with exponential backoff for API failures
- 📊 **Progress tracking**: Real-time progress updates during processing
- 🧹 **Automatic cleanup**: Removes temporary files even if processing fails
- ⚡ **Efficient processing**: Uses MP3 format for optimal file sizes

## Prerequisites

### System Requirements

- Python 3.8 or higher
- FFmpeg 4.0 or higher

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

Verify installation:
```bash
ffmpeg -version
```

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your OpenAI API key:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```
   - Get your API key from: https://platform.openai.com/api-keys

## Usage

### Basic Usage

```bash
python transcribe_mp4.py path/to/your/video.mp4
```

The script will:
1. Extract audio from the MP4 file
2. Check if the audio needs to be split into chunks
3. Transcribe the audio using OpenAI's Whisper API
4. Save the transcription to a text file with the same name as your input

### Output

The transcription will be saved as a `.txt` file in the same directory as your input file:
```
video.mp4 → video.txt
```

### Example

```bash
$ python transcribe_mp4.py meeting_recording.mp4

[STATUS] Validating input file...
[STATUS] Created temporary directory: /tmp/mp4_transcription_xyz123
[STATUS] Extracting audio from MP4...
[STATUS] Audio extraction complete
[STATUS] Audio file size: 45.32 MB
[STATUS] File exceeds size limit. Splitting into chunks...
[STATUS] Created 2 chunks
[STATUS] Starting transcription of 2 chunk(s)...
[====================] 100.0% (2/2) - Transcribing chunk 2
[STATUS] Combining transcription results...
[STATUS] Cleaning up temporary files...

============================================================
TRANSCRIPTION COMPLETE
============================================================
Total processing time: 3m 45s
Output saved to: meeting_recording.txt
============================================================
```

## How It Works

1. **Audio Extraction**: Extracts audio from MP4 using FFmpeg and converts to MP3 format
2. **Size Check**: Determines if the audio file exceeds the 25 MB API limit
3. **Chunking** (if needed): Splits large audio files into time-based chunks under 24 MB each
4. **Transcription**: Sends each chunk to OpenAI's Whisper API with Italian language specification
5. **Combination**: Merges all transcription results in sequential order
6. **Cleanup**: Removes all temporary files automatically

## Configuration

### Environment Variables

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Constants

You can modify these constants in `transcribe_mp4.py` if needed:

- `MAX_FILE_SIZE_MB = 24`: Target chunk size (leaves 1 MB buffer)
- `WHISPER_API_LIMIT_MB = 25`: Actual Whisper API limit
- `MAX_RETRIES = 3`: Maximum retry attempts for API calls

## Troubleshooting

### FFmpeg Not Found

**Error:** `RuntimeError: FFmpeg is not installed`

**Solution:** Install FFmpeg using the instructions in the Prerequisites section and ensure it's in your system PATH.

### API Key Not Found

**Error:** `OPENAI_API_KEY not found in environment variables`

**Solution:** 
1. Ensure you have a `.env` file in the project directory
2. Verify the file contains: `OPENAI_API_KEY=your_actual_key`
3. Check that your API key is valid at https://platform.openai.com/api-keys

### Authentication Failed

**Error:** `AuthenticationError`

**Solution:**
1. Verify your API key is correct and active
2. Check that you have credits available in your OpenAI account
3. Ensure there are no extra spaces or quotes around the API key in `.env`

### File Not Found

**Error:** `Error: File 'video.mp4' does not exist`

**Solution:** 
- Check the file path is correct
- Use absolute paths if relative paths aren't working
- Ensure the file has a `.mp4` extension

### Rate Limiting

**Error:** `RateLimitError`

**Solution:** The script automatically retries with exponential backoff. If the problem persists:
- Wait a few minutes before trying again
- Check your OpenAI API rate limits
- Consider upgrading your OpenAI plan for higher limits

### Disk Space Issues

**Error:** `IOError` or disk space errors

**Solution:**
- Ensure you have enough free disk space (at least 2x the size of your input file)
- The script uses `/tmp` for temporary files - ensure this partition has space
- Temporary files are automatically cleaned up after processing

### Interrupted Processing

If you interrupt the script (Ctrl+C), temporary files will still be cleaned up automatically.

## API Costs

This script uses OpenAI's Whisper API, which charges based on audio duration:
- Current pricing: $0.006 per minute of audio
- Example: A 1-hour video costs approximately $0.36

Check current pricing at: https://openai.com/pricing

## Limitations

- **Input format**: Only MP4 files are supported
- **Language**: Optimized for Italian (can be modified in `whisper_client.py`)
- **File size**: No upper limit, but very large files will take longer to process
- **Internet required**: Requires active internet connection for API calls

## Project Structure

```
.
├── transcribe_mp4.py      # Main orchestration script
├── audio_processor.py     # Audio extraction and chunking
├── whisper_client.py      # OpenAI Whisper API integration
├── file_manager.py        # File and directory management
├── progress_tracker.py    # User feedback and progress display
├── models.py              # Data models
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
└── README.md             # This file
```

## License

This project is provided as-is for educational and practical use.

## Support

For issues related to:
- **This script**: Check the Troubleshooting section above
- **FFmpeg**: Visit https://ffmpeg.org/
- **OpenAI API**: Visit https://platform.openai.com/docs/
- **Whisper API**: Visit https://platform.openai.com/docs/guides/speech-to-text
