"""Data model for a queued audio file."""


class FileItem:
    """Represents a single audio file queued for transcription."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
        self.duration_seconds = 0.0
        self.status = "waiting"  # waiting | processing | done | error | skipped
        self.output_path = ""
        self.error_message = ""
        self.elapsed_seconds = 0.0

    @property
    def duration_display(self) -> str:
        """Format duration as MM:SS or HH:MM:SS."""
        s = int(self.duration_seconds)
        if s >= 3600:
            return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"
        return f"{s // 60}:{s % 60:02d}"

    @property
    def status_display(self) -> str:
        """Human-readable status."""
        return {
            "waiting": "等待",
            "processing": "处理中",
            "done": "完成",
            "error": "失败",
            "skipped": "跳过",
        }.get(self.status, self.status)

    def __repr__(self):
        return f"FileItem({self.filename!r}, status={self.status!r})"
