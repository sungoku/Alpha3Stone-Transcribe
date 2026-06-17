"""Progress bar and status text view."""

import objc
from AppKit import (
    NSView, NSProgressIndicator, NSTextField,
    NSFont, NSRightTextAlignment,
    NSViewWidthSizable, NSViewMinXMargin,
)
from Foundation import NSMakeRect


class ProgressView(NSView):
    """Progress bar with status text. Frame height ~40pt."""

    def initWithFrame_(self, frame):
        self = objc.super(ProgressView, self).initWithFrame_(frame)
        if self is None:
            return None

        W = frame.size.width
        H = frame.size.height

        # Progress bar (top)
        self.progress = NSProgressIndicator.alloc().initWithFrame_(
            NSMakeRect(0, H - 16, W, 12)
        )
        self.progress.setStyle_(0)  # Bar style
        self.progress.setMinValue_(0)
        self.progress.setMaxValue_(1)
        self.progress.setDoubleValue_(0)
        self.progress.setIndeterminate_(False)
        self.progress.setAutoresizingMask_(NSViewWidthSizable)
        self.addSubview_(self.progress)

        # Status label (bottom-left)
        self.status_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 18))
        self.status_label.setStringValue_("就绪")
        self.status_label.setFont_(NSFont.systemFontOfSize_(11))
        self.status_label.setBezeled_(False)
        self.status_label.setDrawsBackground_(False)
        self.status_label.setEditable_(False)
        self.status_label.setSelectable_(False)
        self.addSubview_(self.status_label)

        # ETA label (bottom-right)
        self.eta_label = NSTextField.alloc().initWithFrame_(NSMakeRect(W - 200, 0, 200, 18))
        self.eta_label.setStringValue_("")
        self.eta_label.setFont_(NSFont.systemFontOfSize_(11))
        self.eta_label.setAlignment_(NSRightTextAlignment)
        self.eta_label.setBezeled_(False)
        self.eta_label.setDrawsBackground_(False)
        self.eta_label.setEditable_(False)
        self.eta_label.setSelectable_(False)
        self.eta_label.setAutoresizingMask_(NSViewMinXMargin)
        self.addSubview_(self.eta_label)

        return self

    def updateProgress_(self, data):
        """Update progress bar and status text. data = {'current': int, 'total': int}"""
        current = data.get("current", 0)
        total = data.get("total", 0)
        if total > 0:
            self.progress.setMaxValue_(float(total))
            self.progress.setDoubleValue_(float(current))
            self.status_label.setStringValue_(f"{current}/{total} 文件")
        else:
            self.progress.setDoubleValue_(0)
            self.status_label.setStringValue_("就绪")

    def setEta_(self, text):
        self.eta_label.setStringValue_(text or "")

    def setStatus_(self, text):
        self.status_label.setStringValue_(text)

    def reset(self):
        self.progress.setDoubleValue_(0)
        self.progress.setMaxValue_(1)
        self.status_label.setStringValue_("就绪")
        self.eta_label.setStringValue_("")
