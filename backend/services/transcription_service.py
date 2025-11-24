import sys
import os
import time
from typing import List

# Add root directory to sys.path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from audio_processor import (
    extract_audio,
    get_file_size_mb,
    get_audio_duration,
    calculate_chunk_duration,
    split_audio
)
from whisper_client import transcribe_with_retry
from file_manager import create_temp_directory, cleanup_temp_files
from models import AudioChunk, TranscriptionResult

MAX_FILE_SIZE_MB = 24

class TranscriptionService:
    def process_file(self, file_path: str, language: str = "it") -> str:
        temp_dir = None
        try:
            temp_dir = create_temp_directory()
            
            # Determine if it's video or audio
            ext = os.path.splitext(file_path)[1].lower()
            audio_file = file_path
            
            if ext in ['.mp4', '.mpeg']:
                audio_file = os.path.join(temp_dir, "extracted_audio.mp3")
                extract_audio(file_path, audio_file)
            
            # Check size and chunk if needed
            audio_size_mb = get_file_size_mb(audio_file)
            chunks: List[AudioChunk] = []
            
            if audio_size_mb > MAX_FILE_SIZE_MB:
                duration = get_audio_duration(audio_file)
                chunk_duration = calculate_chunk_duration(audio_size_mb, duration, MAX_FILE_SIZE_MB)
                chunk_paths = split_audio(audio_file, chunk_duration, temp_dir)
                
                for idx, chunk_path in enumerate(chunk_paths):
                    chunks.append(AudioChunk(
                        path=chunk_path,
                        index=idx,
                        duration=chunk_duration,
                        size_mb=get_file_size_mb(chunk_path)
                    ))
            else:
                chunks.append(AudioChunk(
                    path=audio_file,
                    index=0,
                    duration=0.0,
                    size_mb=audio_size_mb
                ))
            
            # Transcribe
            results = []
            for chunk in chunks:
                text = transcribe_with_retry(chunk.path, language=language)
                results.append(TranscriptionResult(
                    chunk_index=chunk.index,
                    text=text,
                    processing_time=0
                ))
            
            results.sort(key=lambda r: r.chunk_index)
            combined_text = "\n".join(result.text for result in results)
            
            return combined_text
            
        finally:
            if temp_dir:
                cleanup_temp_files(temp_dir)
