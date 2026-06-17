"""Path and file utility functions."""

import os


SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".flac", ".ogg", ".wma", ".aac"}


def is_audio_file(filepath: str) -> bool:
    """Check if a file has a supported audio extension."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in SUPPORTED_EXTENSIONS


def scan_for_audio_files(path: str, extensions: set = None) -> list:
    """Scan a directory recursively for audio files.

    Args:
        path: File or directory path.
        extensions: Set of extensions to match (default: SUPPORTED_EXTENSIONS).

    Returns:
        List of absolute paths to audio files.
    """
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS

    if os.path.isfile(path):
        if is_audio_file(path):
            return [os.path.abspath(path)]
        return []

    if not os.path.isdir(path):
        return []

    results = []
    for root, _dirs, files in os.walk(path):
        for f in sorted(files):
            _, ext = os.path.splitext(f)
            if ext.lower() in extensions:
                results.append(os.path.join(root, f))
    return results


def deduplicate_paths(paths: list) -> list:
    """Remove duplicate paths (by absolute path)."""
    seen = set()
    result = []
    for p in paths:
        abs_p = os.path.abspath(p)
        if abs_p not in seen:
            seen.add(abs_p)
            result.append(abs_p)
    return result
