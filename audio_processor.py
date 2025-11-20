"""
Audio Processor Module

Handles audio extraction from MP4 files and audio chunking using FFmpeg.
"""

import os
import subprocess
from typing import List


def get_file_size_mb(file_path: str) -> float:
    """
    Calculate file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: File size in megabytes
    """
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return size_mb


def get_audio_duration(audio_path: str) -> float:
    """
    Get the duration of an audio file in seconds using FFmpeg.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        float: Duration in seconds
        
    Raises:
        RuntimeError: If FFmpeg is not installed or fails to get duration
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed. Please install FFmpeg to use this script.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get audio duration: {e.stderr}")
    except ValueError as e:
        raise RuntimeError(f"Failed to parse audio duration: {e}")


def extract_audio(mp4_path: str, output_path: str) -> str:
    """
    Extract audio from MP4 file and save as MP3.
    
    Args:
        mp4_path: Path to the input MP4 file
        output_path: Path where the extracted audio should be saved
        
    Returns:
        str: Path to the extracted audio file
        
    Raises:
        RuntimeError: If FFmpeg is not installed or extraction fails
    """
    try:
        cmd = [
            'ffmpeg',
            '-i', mp4_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # MP3 codec
            '-q:a', '2',  # High quality
            '-y',  # Overwrite output file
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed. Please install FFmpeg to use this script.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract audio from MP4: {e.stderr}")


def calculate_chunk_duration(file_size_mb: float, duration_seconds: float, max_size_mb: float = 24) -> float:
    """
    Calculate the optimal chunk duration to keep chunks under the size limit.
    
    Args:
        file_size_mb: Total file size in megabytes
        duration_seconds: Total duration in seconds
        max_size_mb: Maximum chunk size in megabytes (default: 24 MB)
        
    Returns:
        float: Chunk duration in seconds
    """
    if file_size_mb <= max_size_mb:
        return duration_seconds
    
    # Calculate how many chunks we need
    num_chunks = (file_size_mb / max_size_mb)
    chunk_duration = duration_seconds / num_chunks
    
    return chunk_duration


def split_audio(audio_path: str, chunk_duration: float, output_dir: str) -> List[str]:
    """
    Split audio file into chunks of specified duration.
    
    Args:
        audio_path: Path to the audio file to split
        chunk_duration: Duration of each chunk in seconds
        output_dir: Directory where chunks should be saved
        
    Returns:
        List[str]: List of paths to the created chunk files
        
    Raises:
        RuntimeError: If FFmpeg is not installed or splitting fails
    """
    try:
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d.mp3")
        
        cmd = [
            'ffmpeg',
            '-i', audio_path,
            '-f', 'segment',
            '-segment_time', str(chunk_duration),
            '-c', 'copy',
            '-y',
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Collect all created chunk files
        chunk_files = []
        for filename in sorted(os.listdir(output_dir)):
            if filename.startswith(f"{base_name}_chunk_") and filename.endswith('.mp3'):
                chunk_files.append(os.path.join(output_dir, filename))
        
        return chunk_files
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed. Please install FFmpeg to use this script.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to split audio: {e.stderr}")
