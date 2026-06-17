"""NSApplicationDelegate for Alpha3Stone Transcribe."""

import objc
from Foundation import NSObject, NSMakeRect, NSMakeSize
from AppKit import (
    NSWindow, NSView, NSButton, NSBox, NSBoxSeparator, NSFont,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSBackingStoreBuffered, NSBezelStyleRounded, NSBezelBorder,
    NSLayoutAttributeTrailing, NSLayoutRelationEqual,
    NSViewMinXMargin,
)
from .views.drop_zone_view import DropZoneView
from .views.file_table_view import FileTableView
from .views.settings_view import SettingsView
from .views.progress_view import ProgressView
from .controllers.transcription_controller import TranscriptionController

import AppKit


def _pin_h(view, content, m):
    """Pin view horizontally with margin m."""
    vs = {"v": view}
    content.addConstraints_(
        AppKit.NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
            "H:|-m-[v]-m-|", 0, {"m": m}, vs
        )
    )


class AppDelegate(NSObject):
    """Application delegate - creates and manages the main window."""

    def applicationDidFinishLaunching_(self, notification):
        style = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                 NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(200, 200, 580, 580),
            style,
            NSBackingStoreBuffered,
            False,
        )
        self.window.setTitle_("Alpha3Stone Transcribe")
        self.window.setMinSize_(NSMakeSize(500, 500))

        self.controller = TranscriptionController.alloc().init()
        content = self.window.contentView()
        m = 12

        # --- Drop zone ---
        drop_zone = DropZoneView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 560, 80), self.controller
        )
        drop_zone.setTranslatesAutoresizingMaskIntoConstraints_(False)
        content.addSubview_(drop_zone)
        _pin_h(drop_zone, content, m)

        # --- Button bar (清空 / 移除) ---
        btn_bar = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 28))
        btn_bar.setTranslatesAutoresizingMaskIntoConstraints_(False)

        clear_btn = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 70, 24))
        clear_btn.setTitle_("清空")
        clear_btn.setBezelStyle_(NSBezelStyleRounded)
        clear_btn.setTranslatesAutoresizingMaskIntoConstraints_(False)
        clear_btn.setTarget_(self.controller)
        clear_btn.setAction_("clearAllFiles:")
        btn_bar.addSubview_(clear_btn)

        remove_btn = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 70, 24))
        remove_btn.setTitle_("移除")
        remove_btn.setBezelStyle_(NSBezelStyleRounded)
        remove_btn.setTranslatesAutoresizingMaskIntoConstraints_(False)
        remove_btn.setTarget_(self.controller)
        remove_btn.setAction_("removeSelectedFiles:")
        btn_bar.addSubview_(remove_btn)

        # Pin buttons to right side of btn_bar
        bvs = {"c": clear_btn, "r": remove_btn}
        btn_bar.addConstraints_(
            AppKit.NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                "H:[c(70)]-8-[r(70)]-0-|", 0, None, bvs
            )
        )
        btn_bar.addConstraints_(
            AppKit.NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                "V:|-0-[c(24)]-0-|", 0, None, bvs
            )
        )
        btn_bar.addConstraints_(
            AppKit.NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                "V:|-0-[r(24)]-0-|", 0, None, bvs
            )
        )

        content.addSubview_(btn_bar)
        _pin_h(btn_bar, content, m)

        # --- File table ---
        file_table = FileTableView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 560, 180), self.controller
        )
        file_table.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setTableView_(file_table)
        content.addSubview_(file_table)
        _pin_h(file_table, content, m)

        # --- Separator ---
        sep = NSBox.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 1))
        sep.setBoxType_(NSBoxSeparator)
        sep.setTranslatesAutoresizingMaskIntoConstraints_(False)
        content.addSubview_(sep)
        _pin_h(sep, content, m)

        # --- Settings ---
        settings_view = SettingsView.alloc().initWithFrame_controller_(
            NSMakeRect(0, 0, 560, 84), self.controller
        )
        settings_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setSettingsView_(settings_view)
        content.addSubview_(settings_view)
        _pin_h(settings_view, content, m)

        # --- Start button ---
        start_button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 32))
        start_button.setTitle_("\U0001F680 开始转录")
        start_button.setBezelStyle_(NSBezelBorder)
        start_button.setTranslatesAutoresizingMaskIntoConstraints_(False)
        start_button.setTarget_(self.controller)
        start_button.setAction_(objc.selector(self.controller.startTranscription_, signature=b"v@:@"))
        self.controller.setStartButton_(start_button)
        content.addSubview_(start_button)
        _pin_h(start_button, content, m)

        # --- Progress ---
        progress_view = ProgressView.alloc().initWithFrame_(NSMakeRect(0, 0, 560, 40))
        progress_view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        self.controller.setProgressView_(progress_view)
        content.addSubview_(progress_view)
        _pin_h(progress_view, content, m)

        # --- Vertical layout ---
        vs = {
            "dz": drop_zone,
            "bb": btn_bar,
            "ft": file_table,
            "s1": sep,
            "sv": settings_view,
            "btn": start_button,
            "pv": progress_view,
        }
        metrics = {"m": m, "sp": 8}
        vfl = "V:|-m-[dz(80)]-sp-[bb(28)]-sp-[ft(>=120)]-sp-[s1(1)]-sp-[sv(84)]-sp-[btn(32)]-sp-[pv(40)]-m-|"
        content.addConstraints_(
            AppKit.NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(vfl, 0, metrics, vs)
        )

        self.window.makeKeyAndOrderFront_(None)

    def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
        return True
