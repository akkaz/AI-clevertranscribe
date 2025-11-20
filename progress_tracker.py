"""
Progress Tracker Module

Provides user feedback during transcription processing.
"""


def display_status(message: str) -> None:
    """
    Display a status message to the user.
    
    Args:
        message: Status message to display
    """
    print(f"[STATUS] {message}")


def display_progress(current: int, total: int, message: str = "") -> None:
    """
    Display progress information for chunk processing.
    
    Args:
        current: Current chunk number (1-indexed)
        total: Total number of chunks
        message: Optional additional message
    """
    percentage = (current / total) * 100
    progress_bar = "=" * int(percentage / 5) + ">" + " " * (20 - int(percentage / 5))
    
    output = f"[{progress_bar}] {percentage:.1f}% ({current}/{total})"
    if message:
        output += f" - {message}"
    
    print(output)


def display_summary(total_time: float, output_file: str) -> None:
    """
    Display final processing summary.
    
    Args:
        total_time: Total processing time in seconds
        output_file: Path to the output transcription file
    """
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    print("\n" + "=" * 60)
    print("TRANSCRIPTION COMPLETE")
    print("=" * 60)
    print(f"Total processing time: {minutes}m {seconds}s")
    print(f"Output saved to: {output_file}")
    print("=" * 60)
