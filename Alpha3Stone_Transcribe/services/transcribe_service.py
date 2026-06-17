"""Transcription service wrapping mlx_whisper."""

import os
import time

from .output_formatter import format_plain_text, format_timestamped_text, format_srt, get_output_path


def transcribe_file(item, model_path: str, language: str = None,
                    timestamp_mode: bool = False, overwrite: bool = False):
    """Transcribe a single audio file.

    Args:
        item: FileItem instance.
        model_path: Path to Whisper model directory.
        language: Language code (zh/en) or None for auto-detect.
        timestamp_mode: If True, output with timestamps (.srt).
        overwrite: If True, overwrite existing output files.

    Returns:
        Updated FileItem with status, output_path, and elapsed_seconds set.

    Raises:
        Exception: If transcription fails (caller should catch).
    """
    # Determine output path
    ext = ".srt" if timestamp_mode else ".txt"
    output_path = os.path.splitext(item.filepath)[0] + ext

    # Skip existing files unless overwrite
    if not overwrite and os.path.exists(output_path):
        item.status = "skipped"
        item.output_path = output_path
        return item

    # Lazy import to avoid slow startup
    import mlx_whisper

    # Run transcription
    start_time = time.time()
    result = mlx_whisper.transcribe(
        audio=item.filepath,
        path_or_hf_repo=model_path,
        language=language,
    )

    # Format output
    if timestamp_mode:
        content = format_srt(result)
    else:
        content = format_plain_text(result)

    # Clean trailing whitespace
    content = content.rstrip() + "\n" if content.strip() else ""

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    item.output_path = output_path
    item.elapsed_seconds = time.time() - start_time
    item.status = "done"
    return item
