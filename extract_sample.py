#!/usr/bin/env python3
"""
Extract Sample Video

Creates a short sample from the beginning of a video file for testing purposes.
"""

import argparse
import subprocess
import sys
import os


def extract_sample(input_file: str, duration_minutes: float = 2.0, output_file: str = None) -> str:
    """
    Extract the first N minutes from a video file.
    
    Args:
        input_file: Path to the input video file
        duration_minutes: Duration to extract in minutes (default: 2.0)
        output_file: Optional output filename (default: input_sample.mp4)
        
    Returns:
        str: Path to the created sample file
    """
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)
    
    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_sample.mp4"
    
    # Convert minutes to seconds
    duration_seconds = duration_minutes * 60
    
    print(f"Extracting first {duration_minutes} minute(s) from '{input_file}'...")
    print(f"Output will be saved to: '{output_file}'")
    
    try:
        # Use FFmpeg to extract the sample
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-t', str(duration_seconds),  # Duration to extract
            '-c', 'copy',  # Copy streams without re-encoding (fast)
            '-y',  # Overwrite output file if exists
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"\n✓ Sample created successfully: {output_file}")
        
        # Show file sizes for comparison
        original_size = os.path.getsize(input_file) / (1024 * 1024)
        sample_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\nOriginal file: {original_size:.2f} MB")
        print(f"Sample file: {sample_size:.2f} MB")
        
        return output_file
        
    except FileNotFoundError:
        print("Error: FFmpeg is not installed. Please install FFmpeg first.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to extract sample: {e.stderr}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Extract a short sample from the beginning of a video file for testing'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input video file'
    )
    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=2.0,
        help='Duration to extract in minutes (default: 2.0)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output filename (default: input_sample.mp4)'
    )
    
    args = parser.parse_args()
    
    sample_file = extract_sample(args.input_file, args.duration, args.output)
    
    print(f"\nYou can now test with: python transcribe_mp4.py {sample_file}")


if __name__ == "__main__":
    main()
