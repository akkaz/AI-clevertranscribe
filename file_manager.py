"""
File Manager Module

Handles temporary file creation, cleanup, and output file generation
for the MP4 transcription script.
"""

import os
import shutil
import tempfile
from pathlib import Path


def create_temp_directory() -> str:
    """
    Create a secure temporary directory for storing audio chunks.
    
    Returns:
        str: Path to the created temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix="mp4_transcription_")
    return temp_dir


def cleanup_temp_files(temp_dir: str) -> None:
    """
    Remove all temporary files and the temporary directory.
    
    Args:
        temp_dir: Path to the temporary directory to clean up
    """
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            # Log the error but don't raise - cleanup is best effort
            print(f"Warning: Failed to clean up temporary directory {temp_dir}: {e}")


def generate_output_filename(input_path: str) -> str:
    """
    Generate output filename based on the input MP4 filename.
    
    The output file will have the same name as the input file but with
    a .txt extension, and will be placed in the same directory as the input.
    
    Args:
        input_path: Path to the input MP4 file
        
    Returns:
        str: Path to the output text file
    """
    input_file = Path(input_path)
    output_filename = input_file.stem + ".txt"
    output_path = input_file.parent / output_filename
    return str(output_path)


def save_transcription(text: str, output_path: str) -> None:
    """
    Save the final transcription text to a file.
    
    Args:
        text: The transcription text to save
        output_path: Path where the transcription should be saved
        
    Raises:
        IOError: If the file cannot be written
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        raise IOError(f"Failed to save transcription to {output_path}: {e}")
