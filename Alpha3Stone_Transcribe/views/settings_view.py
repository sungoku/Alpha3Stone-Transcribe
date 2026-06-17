"""Settings panel with language, timestamp mode, model path, and output directory."""

import os
import objc
from AppKit import (
    NSView, NSPopUpButton, NSButton, NSTextField,
    NSFont, NSBezelStyleRounded, NSSwitchButton,
    NSOpenPanel, NSModalResponseOK,
    NSViewWidthSizable, NSViewMinYMargin,
)
from Foundation import NSMakeRect, NSObject


DEFAULT_MODEL_PATH = "~/.lmstudio/models/mlx-community/whisper-large-v3-turbo"


class SettingsView(NSView):
    """Inline settings panel for transcription options.

    Uses absolute positioning with autoresizing masks. The view is 84pt tall
    with three rows of 24pt each.
    """

    def initWithFrame_controller_(self, frame, controller):
        self = objc.super(SettingsView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.controller = controller

        W = frame.size.width
        H = frame.size.height

        # --- Row 1 (top): Language + Timestamp + Overwrite ---
        y1 = H - 26

        lang_label = self._make_label("语言:", NSMakeRect(0, y1, 36, 22))
        self.addSubview_(lang_label)

        self.lang_popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(40, y1, 110, 24))
        self.lang_popup.addItemsWithTitles_(["中文 (zh)", "English (en)", "自动检测"])
        self.lang_popup.setAutoresizingMask_(NSViewMinYMargin)
        self.addSubview_(self.lang_popup)

        self.timestamp_check = NSButton.alloc().initWithFrame_(NSMakeRect(160, y1, 110, 22))
        self.timestamp_check.setButtonType_(NSSwitchButton)
        self.timestamp_check.setTitle_("带时间戳")
        self.timestamp_check.setAutoresizingMask_(NSViewMinYMargin)
        self.addSubview_(self.timestamp_check)

        self.overwrite_check = NSButton.alloc().initWithFrame_(NSMakeRect(280, y1, 130, 22))
        self.overwrite_check.setButtonType_(NSSwitchButton)
        self.overwrite_check.setTitle_("覆盖已有文件")
        self.overwrite_check.setAutoresizingMask_(NSViewMinYMargin)
        self.addSubview_(self.overwrite_check)

        # --- Row 2 (middle): Model path ---
        y2 = H - 53

        model_label = self._make_label("模型:", NSMakeRect(0, y2, 36, 22))
        self.addSubview_(model_label)

        self.model_field = NSTextField.alloc().initWithFrame_(NSMakeRect(40, y2, W - 130, 22))
        self.model_field.setStringValue_(DEFAULT_MODEL_PATH)
        self.model_field.setEditable_(False)
        self.model_field.setFont_(NSFont.systemFontOfSize_(11))
        self.model_field.setAutoresizingMask_(NSViewWidthSizable | NSViewMinYMargin)
        self.addSubview_(self.model_field)

        self.model_btn = NSButton.alloc().initWithFrame_(NSMakeRect(W - 84, y2, 80, 24))
        self.model_btn.setTitle_("更改...")
        self.model_btn.setBezelStyle_(NSBezelStyleRounded)
        self.model_btn.setTarget_(self)
        self.model_btn.setAction_("chooseModel:")
        self.model_btn.setAutoresizingMask_(NSViewMinYMargin)
        self.addSubview_(self.model_btn)

        # --- Row 3 (bottom): Output directory ---
        y3 = H - 80

        out_label = self._make_label("输出:", NSMakeRect(0, y3, 36, 22))
        self.addSubview_(out_label)

        self.output_field = NSTextField.alloc().initWithFrame_(NSMakeRect(40, y3, W - 130, 22))
        self.output_field.setStringValue_("与源文件相同目录")
        self.output_field.setEditable_(False)
        self.output_field.setFont_(NSFont.systemFontOfSize_(11))
        self.output_field.setAutoresizingMask_(NSViewWidthSizable | NSViewMinYMargin)
        self.addSubview_(self.output_field)

        self.output_btn = NSButton.alloc().initWithFrame_(NSMakeRect(W - 84, y3, 80, 24))
        self.output_btn.setTitle_("选择...")
        self.output_btn.setBezelStyle_(NSBezelStyleRounded)
        self.output_btn.setTarget_(self)
        self.output_btn.setAction_("chooseOutput:")
        self.output_btn.setAutoresizingMask_(NSViewMinYMargin)
        self.addSubview_(self.output_btn)

        return self

    def _make_label(self, text, frame):
        label = NSTextField.alloc().initWithFrame_(frame)
        label.setStringValue_(text)
        label.setFont_(NSFont.systemFontOfSize_(12))
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        label.setEditable_(False)
        label.setSelectable_(False)
        label.setAutoresizingMask_(NSViewMinYMargin)
        return label

    # --- Getters ---

    def get_language(self):
        idx = self.lang_popup.indexOfSelectedItem()
        if idx == 0:
            return "zh"
        elif idx == 1:
            return "en"
        return None

    def get_timestamp_mode(self):
        return self.timestamp_check.state() == 1

    def get_overwrite(self):
        return self.overwrite_check.state() == 1

    def get_model_path(self):
        return self.model_field.stringValue()

    def get_output_dir(self):
        val = self.output_field.stringValue()
        if val == "与源文件相同目录":
            return None
        return val

    # --- Button actions (end with _ for ObjC ':' selector) ---

    def chooseModel_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        panel.setTitle_("选择 Whisper 模型目录")
        if panel.runModal() == NSModalResponseOK:
            url = panel.URL()
            if url:
                self.model_field.setStringValue_(url.path())

    def chooseOutput_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        panel.setTitle_("选择输出目录")
        if panel.runModal() == NSModalResponseOK:
            url = panel.URL()
            if url:
                self.output_field.setStringValue_(url.path())
