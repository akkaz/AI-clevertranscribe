#!/usr/bin/env python3
"""
MP4 Transcription Script

Transcribes Italian audio from MP4 video files using OpenAI's Whisper API.
Handles large files by splitting them into chunks that comply with API size limits.
"""

import argparse
import os
import sys
import time
from typing import List

from audio_processor import (
    extract_audio,
    get_file_size_mb,
    get_audio_duration,
    calculate_chunk_duration,
    split_audio
)
from whisper_client import transcribe_with_retry
from file_manager import (
    create_temp_directory,
    cleanup_temp_files,
    generate_output_filename,
    save_transcription
)
from progress_tracker import display_status, display_progress, display_summary
from models import AudioChunk, TranscriptionResult


# Constants
MAX_FILE_SIZE_MB = 24  # Target chunk size (1 MB buffer below API limit)
WHISPER_API_LIMIT_MB = 25  # Actual API limit


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Transcribe Italian audio from MP4 files using OpenAI Whisper API'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input MP4 file'
    )
    return parser.parse_args()


def validate_input_file(input_file: str) -> None:
    """
    Validate that the input file exists and has the correct extension.
    
    Args:
        input_file: Path to the input file
        
    Raises:
        SystemExit: If validation fails
    """
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)
    
    if not input_file.lower().endswith('.mp4'):
        print(f"Error: File '{input_file}' is not an MP4 file.")
        sys.exit(1)
    
    if not os.access(input_file, os.R_OK):
        print(f"Error: File '{input_file}' is not readable.")
        sys.exit(1)


def process_audio_chunks(chunks: List[AudioChunk]) -> List[TranscriptionResult]:
    """
    Process multiple audio chunks through Whisper API.
    
    Args:
        chunks: List of audio chunks to process
        
    Returns:
        List[TranscriptionResult]: Transcription results for all chunks
    """
    results = []
    total_chunks = len(chunks)
    
    for chunk in chunks:
        display_progress(
            chunk.index + 1,
            total_chunks,
            f"Transcribing chunk {chunk.index + 1}"
        )
        
        start_time = time.time()
        text = transcribe_with_retry(chunk.path, language="it")
        processing_time = time.time() - start_time
        
        result = TranscriptionResult(
            chunk_index=chunk.index,
            text=text,
            processing_time=processing_time
        )
        results.append(result)
    
    return results


def main(input_file: str) -> None:
    """
    Main orchestration function for the transcription workflow.
    
    Args:
        input_file: Path to the input MP4 file
    """
    temp_dir = None
    start_time = time.time()
    
    try:
        # Validate input
        display_status("Validating input file...")
        validate_input_file(input_file)
        
        # Create temporary directory
        temp_dir = create_temp_directory()
        display_status(f"Created temporary directory: {temp_dir}")
        
        # Extract audio from MP4
        display_status("Extracting audio from MP4...")
        audio_file = os.path.join(temp_dir, "extracted_audio.mp3")
        extract_audio(input_file, audio_file)
        display_status("Audio extraction complete")
        
        # Check file size and determine if chunking is needed
        audio_size_mb = get_file_size_mb(audio_file)
        display_status(f"Audio file size: {audio_size_mb:.2f} MB")
        
        chunks: List[AudioChunk] = []
        
        if audio_size_mb > MAX_FILE_SIZE_MB:
            # Need to split into chunks
            display_status("File exceeds size limit. Splitting into chunks...")
            
            duration = get_audio_duration(audio_file)
            chunk_duration = calculate_chunk_duration(
                audio_size_mb,
                duration,
                MAX_FILE_SIZE_MB
            )
            
            chunk_paths = split_audio(audio_file, chunk_duration, temp_dir)
            display_status(f"Created {len(chunk_paths)} chunks")
            
            # Create AudioChunk objects
            for idx, chunk_path in enumerate(chunk_paths):
                chunk_size = get_file_size_mb(chunk_path)
                chunks.append(AudioChunk(
                    path=chunk_path,
                    index=idx,
                    duration=chunk_duration,
                    size_mb=chunk_size
                ))
        else:
            # Single file, no chunking needed
            display_status("File size is within limits. No chunking required.")
            chunks.append(AudioChunk(
                path=audio_file,
                index=0,
                duration=0.0,
                size_mb=audio_size_mb
            ))
        
        # Process chunks through Whisper API
        display_status(f"Starting transcription of {len(chunks)} chunk(s)...")
        results = process_audio_chunks(chunks)
        
        # Combine transcription results in sequential order
        display_status("Combining transcription results...")
        results.sort(key=lambda r: r.chunk_index)
        combined_text = "\n".join(result.text for result in results)
        
        # Save transcription to output file
        output_file = generate_output_filename(input_file)
        save_transcription(combined_text, output_file)
        
        # Display summary
        total_time = time.time() - start_time
        display_summary(total_time, output_file)
        
    except KeyboardInterrupt:
        print("\n\nTranscription interrupted by user.")
        sys.exit(130)
    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        sys.exit(3)
    except RuntimeError as e:
        print(f"\nProcessing Error: {e}")
        sys.exit(2)
    except IOError as e:
        print(f"\nFile System Error: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        sys.exit(1)
    finally:
        # Always clean up temporary files
        if temp_dir:
            display_status("Cleaning up temporary files...")
            cleanup_temp_files(temp_dir)


if __name__ == "__main__":
    args = parse_arguments()
    main(args.input_file)
