"""Output formatters for transcription results."""

import os


def format_plain_text(result: dict) -> str:
    """Format as plain text (one segment per line)."""
    lines = []
    for seg in result.get("segments", []):
        text = seg.get("text", "").strip()
        if text:
            lines.append(text)
    return "\n".join(lines) + "\n" if lines else ""


def format_timestamped_text(result: dict) -> str:
    """Format as timestamped plain text: [HH:MM:SS --> HH:MM:SS] text"""
    lines = []
    for seg in result.get("segments", []):
        text = seg.get("text", "").strip()
        if not text:
            continue
        start = _fmt_ts(seg.get("start", 0))
        end = _fmt_ts(seg.get("end", 0))
        lines.append(f"[{start} --> {end}] {text}")
    return "\n".join(lines) + "\n" if lines else ""


def format_srt(result: dict) -> str:
    """Format as SRT subtitle file."""
    entries = []
    idx = 0
    for seg in result.get("segments", []):
        text = seg.get("text", "").strip()
        if not text:
            continue
        idx += 1
        start = _fmt_srt_ts(seg.get("start", 0))
        end = _fmt_srt_ts(seg.get("end", 0))
        entries.append(f"{idx}\n{start} --> {end}\n{text}")
    return "\n\n".join(entries) + "\n" if entries else ""


def _fmt_ts(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"


def _fmt_srt_ts(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    total_ms = int(seconds * 1000)
    h = total_ms // 3_600_000
    m = (total_ms % 3_600_000) // 60_000
    s = (total_ms % 60_000) // 1_000
    ms = total_ms % 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def get_output_path(source_path: str, timestamp_mode: bool, output_dir: str = None) -> str:
    """Determine the output file path based on mode."""
    ext = ".srt" if timestamp_mode else ".txt"
    base = os.path.splitext(os.path.basename(source_path))[0]
    if output_dir:
        return os.path.join(output_dir, base + ext)
    return os.path.splitext(source_path)[0] + ext
