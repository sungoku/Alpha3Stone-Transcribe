"""Main window layout using NSStackView."""

import objc
from AppKit import (
    NSWindow, NSView, NSStackView, NSButton, NSTextField,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSBackingStoreBuffered, NSBezelBorder, NSCenterTextAlignment,
    NSFont, NSColor, NSBox, NSBoxSeparator,
    NSLayoutConstraint, NSLayoutAttributeHeight, NSLayoutRelationGreaterThanOrEqual,
)
from Foundation import NSMakeRect, NSMakeSize, NSObject
from .views.drop_zone_view import DropZoneView
from .views.file_table_view import FileTableView
from .views.settings_view import SettingsView
from .views.progress_view import ProgressView
from .controllers.transcription_controller import TranscriptionController


class MainWindow(NSWindow):
    """Main application window."""

    def initWithContentRect_styleMask_backing_defer_(self, rect, style, backing, defer):
        self = objc.super(MainWindow, self).initWithContentRect_styleMask_backing_defer_(
            rect, style, backing, defer,
        )
        if self is None:
            return None
        self._setupUI()
        return self

    def _setupUI(self):
        self.setTitle_("Alpha3Stone Transcribe")
        self.setMinSize_(NSMakeSize(480, 420))

        # Controller
        self.controller = TranscriptionController.alloc().init()

        # Build UI
        content = self.contentView()
        stack = NSStackView.alloc().initWithFrame_(content.bounds())
        stack.setOrientation_(0)  # vertical
        stack.setSpacing_(8)
        stack.setTranslatesAutoresizingMaskIntoConstraints_(False)

        # Drop zone
        self.drop_zone = DropZoneView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 540, 100), self.controller
        )
        self.drop_zone.setTranslatesAutoresizingMaskIntoConstraints_(False)

        # File table
        self.file_table = FileTableView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 540, 180), self.controller
        )
        self.file_table.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setTableView_(self.file_table)

        # Settings
        self.settings_view = SettingsView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 540, 110), self.controller
        )
        self.settings_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setSettingsView_(self.settings_view)

        # Separator
        separator1 = NSBox.alloc().initWithFrame_(NSMakeRect(0, 0, 540, 1))
        separator1.setBoxType_(NSBoxSeparator)

        # Start button
        self.start_button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 540, 36))
        self.start_button.setTitle_("\U0001F680 开始转录")
        self.start_button.setBezelStyle_(NSBezelBorder)
        self.start_button.setTarget_(self.controller)
        self.start_button.setAction_(objc.selector(self.controller.startTranscription_, signature=b"v@:@"))
        self.controller.setStartButton_(self.start_button)

        # Progress view
        self.progress_view = ProgressView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 540, 30)
        )
        self.progress_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setProgressView_(self.progress_view)

        # Add views to stack
        stack.addArrangedSubview_(self.drop_zone)
        stack.addArrangedSubview_(self.file_table)
        stack.addArrangedSubview_(separator1)
        stack.addArrangedSubview_(self.settings_view)
        stack.addArrangedSubview_(self.start_button)
        stack.addArrangedSubview_(self.progress_view)

        # Set hugging priorities to control resizing
        stack.setCustomSpacing_afterView_(12, self.drop_zone)
        stack.setCustomSpacing_afterView_(12, self.file_table)
        stack.setCustomSpacing_afterView_(8, separator1)
        stack.setCustomSpacing_afterView_(8, self.settings_view)
        stack.setCustomSpacing_afterView_(12, self.start_button)

        # Pin drop zone height
        height_constraint = NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
            self.drop_zone, NSLayoutAttributeHeight,
            NSLayoutRelationGreaterThanOrEqual,
            None, 0, 1.0, 80
        )
        self.drop_zone.addConstraint_(height_constraint)

        content.addSubview_(stack)

        # Pin stack to content view edges
        views = {"stack": stack}
        content.addConstraints_(
            NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                "H:|-0-[stack]-0-|", 0, None, views
            )
        )
        content.addConstraints_(
            NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                "V:|-0-[stack]-0-|", 0, None, views
            )
        )

    def show_(self, sender):
        self.makeKeyAndOrderFront_(None)
