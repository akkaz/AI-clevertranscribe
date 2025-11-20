"""
Data Models

Dataclass definitions for maintaining state throughout the transcription process.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AudioChunk:
    """Represents a chunk of audio extracted from the original file."""
    path: str
    index: int
    duration: float
    size_mb: float


@dataclass
class TranscriptionResult:
    """Represents the transcription result for a single audio chunk."""
    chunk_index: int
    text: str
    processing_time: float


@dataclass
class ProcessingContext:
    """Maintains state throughout the entire transcription process."""
    input_file: str
    temp_dir: str
    audio_file: str
    chunks: List[AudioChunk] = field(default_factory=list)
    results: List[TranscriptionResult] = field(default_factory=list)
    start_time: float = 0.0
