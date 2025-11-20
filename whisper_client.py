"""
Whisper API Client Module

Handles communication with OpenAI's Whisper API for audio transcription.
"""

import os
import time
from typing import Optional
from openai import OpenAI, AuthenticationError, APIError, RateLimitError
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def _get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client with API key from environment.
    
    Returns:
        OpenAI: Configured OpenAI client
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    return OpenAI(api_key=api_key)


def transcribe_audio(audio_path: str, language: str = "it") -> str:
    """
    Transcribe an audio file using OpenAI's Whisper API.
    
    Args:
        audio_path: Path to the audio file to transcribe
        language: Language code for transcription (default: "it" for Italian)
        
    Returns:
        str: Transcribed text
        
    Raises:
        ValueError: If API key is not configured
        AuthenticationError: If API authentication fails
        APIError: If API request fails
    """
    client = _get_openai_client()
    
    with open(audio_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )
    
    return response.text


def transcribe_with_retry(
    audio_path: str,
    language: str = "it",
    max_retries: int = 3
) -> str:
    """
    Transcribe audio with exponential backoff retry logic.
    
    Args:
        audio_path: Path to the audio file to transcribe
        language: Language code for transcription (default: "it" for Italian)
        max_retries: Maximum number of retry attempts (default: 3)
        
    Returns:
        str: Transcribed text
        
    Raises:
        ValueError: If API key is not configured
        AuthenticationError: If API authentication fails (no retry)
        APIError: If all retry attempts fail
    """
    last_error: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            return transcribe_audio(audio_path, language)
        except AuthenticationError:
            # Don't retry authentication errors
            raise
        except (APIError, RateLimitError, Exception) as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                print(f"API request failed (attempt {attempt + 1}/{max_retries}). "
                      f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Last attempt failed
                raise APIError(
                    f"Failed to transcribe audio after {max_retries} attempts: {last_error}"
                )
    
    # Should never reach here, but just in case
    raise APIError(f"Transcription failed: {last_error}")
