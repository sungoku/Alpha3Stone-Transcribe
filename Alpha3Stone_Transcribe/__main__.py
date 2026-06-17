"""Application entry point."""

import os
import sys

# Ensure ffmpeg is findable in .app bundle
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "")

from AppKit import NSApplication
from .app_delegate import AppDelegate


def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    main()
