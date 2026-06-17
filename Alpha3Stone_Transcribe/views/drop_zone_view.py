"""Drag-and-drop zone view."""

import os
import objc
from AppKit import (
    NSView, NSColor, NSBezierPath, NSTextField, NSFont,
    NSCenterTextAlignment, NSDragOperationCopy,
    NSOpenPanel, NSModalResponseOK, NSBackingStoreRetained,
)
from Foundation import NSMakeRect, NSMakeSize
from ..services.file_utils import scan_for_audio_files, deduplicate_paths


class DropZoneView(NSView):
    """A drop zone that accepts audio files via drag-and-drop or click-to-browse."""

    def initWithFrame_controller_(self, frame, controller):
        self = objc.super(DropZoneView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.controller = controller
        self._highlighted = False

        # Register for drag types
        self.registerForDraggedTypes_([
            "public.file-url",
            "NSFilenamesPboardType",
        ])

        # Center label
        self.label = NSTextField.alloc().initWithFrame_(
            NSMakeRect(0, 0, frame.size.width, frame.size.height)
        )
        self.label.setStringValue_("📂 拖放 .m4a 文件或文件夹到此处\n或点击选择文件")
        self.label.setFont_(NSFont.systemFontOfSize_(14))
        self.label.setAlignment_(NSCenterTextAlignment)
        self.label.setBezeled_(False)
        self.label.setDrawsBackground_(False)
        self.label.setEditable_(False)
        self.label.setSelectable_(False)
        self.addSubview_(self.label)

        return self

    def drawRect_(self, rect):
        # Background
        if self._highlighted:
            bg_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.5, 0.8, 0.15)
        else:
            bg_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.6, 0.6, 0.6, 0.08)
        bg_color.set()
        NSBezierPath.fillRect_(rect)

        # Dashed border
        border_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.5, 0.5, 0.5)
        if self._highlighted:
            border_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.5, 0.8, 0.8)

        border = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            self.bounds(), 8, 8
        )
        border.setLineWidth_(2)
        border.setLineDash_count_phase_([6, 4], 2, 0)
        border_color.set()
        border.stroke()

    def draggingEntered_(self, sender):
        self._highlighted = True
        self.setNeedsDisplay_(True)
        return NSDragOperationCopy

    def draggingUpdated_(self, sender):
        return NSDragOperationCopy

    def draggingExited_(self, sender):
        self._highlighted = False
        self.setNeedsDisplay_(True)

    def prepareForDragOperation_(self, sender):
        return True

    def performDragOperation_(self, sender):
        self._highlighted = False
        self.setNeedsDisplay_(True)

        pboard = sender.draggingPasteboard()
        paths = []

        # Try NSFilenamesPboardType first
        filenames = pboard.propertyListForType_("NSFilenamesPboardType")
        if filenames:
            paths = list(filenames)
        else:
            # Fallback: read file URLs
            urls = pboard.readObjectsForClasses_options_(
                [objc.lookUpClass("NSURL")],
                {"NSPasteboardURLReadingFileURLsOnlyKey": True}
            )
            if urls:
                paths = [u.path() for u in urls]

        if paths:
            self._add_paths(paths)
        return True

    def mouseDown_(self, event):
        panel = NSOpenPanel.openPanel()
        panel.setAllowsMultipleSelection_(True)
        panel.setCanChooseDirectories_(True)
        panel.setAllowedFileTypes_(["m4a", "mp3", "wav", "flac", "ogg", "aac"])

        if panel.runModal() == NSModalResponseOK:
            urls = panel.URLs()
            paths = [u.path() for u in urls]
            if paths:
                self._add_paths(paths)

    def _add_paths(self, paths):
        """Scan paths for audio files and add to controller."""
        all_files = []
        for p in paths:
            all_files.extend(scan_for_audio_files(p))
        all_files = deduplicate_paths(all_files)

        if all_files:
            self.controller.addFiles_(all_files)
