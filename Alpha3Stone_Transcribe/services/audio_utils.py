"""Audio file utilities - duration probing via AVFoundation (no ffprobe dependency)."""

import objc
from Foundation import NSURL
from AVFoundation import AVURLAsset


def get_audio_duration(filepath: str) -> float:
    """Get audio duration in seconds using AVFoundation.

    Args:
        filepath: Absolute path to audio file.

    Returns:
        Duration in seconds, or 0.0 if probing fails.
    """
    try:
        url = NSURL.fileURLWithPath_(filepath)
        asset = AVURLAsset.URLAssetWithURL_options_(url, None)
        # CMTimeGetSeconds is not wrapped in pyobjc; use duration.value / duration.timescale
        duration = asset.duration()
        if duration.timescale == 0:
            return 0.0
        return duration.value / duration.timescale
    except Exception:
        return 0.0
