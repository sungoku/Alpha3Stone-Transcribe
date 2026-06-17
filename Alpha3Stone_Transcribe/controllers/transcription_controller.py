"""Transcription controller - orchestrates file queue and background processing."""

import os
import time
import threading
import objc
from Foundation import NSObject
from AppKit import NSApplication

from ..models.file_item import FileItem
from ..services.audio_utils import get_audio_duration
from ..services.transcribe_service import transcribe_file


class TranscriptionController(NSObject):
    """Central controller managing the transcription queue and UI updates."""

    # State for main-thread callbacks
    _pending_current = 0
    _pending_total = 0
    _pending_eta = ""

    def init(self):
        self = objc.super(TranscriptionController, self).init()
        if self is None:
            return None
        self.file_items = []
        self.is_running = False
        self._table_view = None
        self._settings_view = None
        self._progress_view = None
        self._start_button = None
        self._existing_paths = set()
        return self

    def setTableView_(self, view):
        self._table_view = view

    def setSettingsView_(self, view):
        self._settings_view = view

    def setProgressView_(self, view):
        self._progress_view = view

    def setStartButton_(self, button):
        self._start_button = button

    def addFiles_(self, filepaths):
        """Add audio files to the queue (called from main thread)."""
        new_items = []
        for fp in filepaths:
            abs_path = os.path.abspath(fp)
            if abs_path in self._existing_paths:
                continue
            self._existing_paths.add(abs_path)
            item = FileItem(abs_path)
            new_items.append(item)

        if not new_items:
            return

        for item in new_items:
            item.duration_seconds = get_audio_duration(item.filepath)

        self.file_items.extend(new_items)
        self._do_refresh_table()

        if self._progress_view:
            total = len(self.file_items)
            # Reset progress bar (clears prior "completed" state), then show added count
            self._progress_view.reset()
            self._progress_view.setStatus_(f"已添加 {len(new_items)} 个文件，共 {total} 个")

    def clearAll(self):
        if self.is_running:
            return
        self.file_items.clear()
        self._existing_paths.clear()
        self._do_refresh_table()
        if self._progress_view:
            self._progress_view.reset()

    # ObjC selectors for button bar
    def clearAllFiles_(self, sender):
        self.clearAll()

    def removeSelectedFiles_(self, sender):
        if self.is_running:
            return
        if self._table_view and self._table_view.table:
            selected = self._table_view.table.selectedRowIndexes()
            if selected.count() > 0:
                self.removeRows_(selected)

    def removeRows_(self, index_set):
        if self.is_running:
            return
        to_remove = []
        idx = index_set.lastIndex()
        while idx != 0x7FFFFFFFFFFFFFFF and idx >= 0:
            if 0 <= idx < len(self.file_items):
                to_remove.append(idx)
            idx = index_set.indexLessThanIndex_(idx)
        for idx in sorted(to_remove, reverse=True):
            removed = self.file_items.pop(idx)
            self._existing_paths.discard(removed.filepath)
        self._do_refresh_table()

    def startTranscription_(self, sender):
        if self.is_running:
            return
        if not self.file_items:
            self._show_alert("没有文件", "请先添加音频文件。")
            return

        settings = self._gather_settings()
        if not settings:
            return

        self.is_running = True
        if self._start_button:
            self._start_button.setEnabled_(False)
            self._start_button.setTitle_("⏳ 转录中...")

        # Reset progress bar from any prior run
        if self._progress_view:
            self._progress_view.reset()
            self._progress_view.setStatus_("准备开始...")

        thread = threading.Thread(target=self._run_queue, args=(settings,), daemon=True)
        thread.start()

    def _gather_settings(self):
        if not self._settings_view:
            return None
        model_path = os.path.expanduser(self._settings_view.get_model_path())
        if not os.path.isdir(model_path):
            self._show_alert("模型未找到",
                f"模型目录不存在:\n{model_path}\n\n请在设置中选择正确的模型路径。")
            return None
        return {
            "language": self._settings_view.get_language(),
            "timestamp_mode": self._settings_view.get_timestamp_mode(),
            "overwrite": self._settings_view.get_overwrite(),
            "model_path": model_path,
            "output_dir": self._settings_view.get_output_dir(),
        }

    def _run_queue(self, settings):
        """Runs in a background thread."""
        total = len(self.file_items)
        done_count = 0
        start_time = time.time()

        for item in self.file_items:
            if item.status in ("done", "skipped") and not settings["overwrite"]:
                done_count += 1
                continue

            item.status = "processing"
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "refreshTableMain:", None, False
            )

            try:
                transcribe_file(
                    item,
                    model_path=settings["model_path"],
                    language=settings["language"],
                    timestamp_mode=settings["timestamp_mode"],
                    overwrite=settings["overwrite"],
                )
            except Exception as e:
                item.status = "error"
                item.error_message = str(e)

            done_count += 1

            # Calculate ETA
            elapsed = time.time() - start_time
            remaining = total - done_count
            if done_count > 0 and remaining > 0:
                avg = elapsed / done_count
                eta_sec = int(avg * remaining)
                if eta_sec >= 3600:
                    eta = f"剩余约 {eta_sec // 3600}h{(eta_sec % 3600) // 60:02d}m"
                elif eta_sec >= 60:
                    eta = f"剩余约 {eta_sec // 60}m{eta_sec % 60:02d}s"
                else:
                    eta = f"剩余约 {eta_sec}s"
            else:
                eta = ""

            self._pending_current = done_count
            self._pending_total = total
            self._pending_eta = eta
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "updateProgressMain:", None, False
            )

        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "finishMain:", None, False
        )

    # --- Main-thread callbacks (must end with _ for ObjC ':' selector) ---

    def refreshTableMain_(self, sender):
        self._do_refresh_table()

    def updateProgressMain_(self, sender):
        if self._progress_view:
            self._progress_view.updateProgress_({
                "current": self._pending_current,
                "total": self._pending_total,
            })
            self._progress_view.setEta_(self._pending_eta)

    def finishMain_(self, sender):
        self.is_running = False
        if self._start_button:
            self._start_button.setEnabled_(True)
            self._start_button.setTitle_("\U0001F680 开始转录")
        self._do_refresh_table()

        done = sum(1 for i in self.file_items if i.status == "done")
        skipped = sum(1 for i in self.file_items if i.status == "skipped")
        errors = sum(1 for i in self.file_items if i.status == "error")
        if self._progress_view:
            if errors > 0:
                self._progress_view.setStatus_(f"完成 {done}, 跳过 {skipped}, 失败 {errors}")
            else:
                self._progress_view.setStatus_(f"全部完成! 成功 {done}, 跳过 {skipped}")

    # --- Plain Python helper (not an ObjC selector) ---

    def _do_refresh_table(self):
        if self._table_view:
            self._table_view.reloadData()

    def _show_alert(self, title, message):
        from AppKit import NSAlert, NSAlertStyleWarning
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(message)
        alert.setAlertStyle_(NSAlertStyleWarning)
        alert.addButtonWithTitle_("确定")
        alert.runModal()
