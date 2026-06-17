"""py2app entry point for Alpha3Stone Transcribe.

Uses absolute imports so it works both as a script (py2app) and via -m.
"""

import os
import sys

# Ensure ffmpeg/ffprobe are findable inside the .app bundle (limited PATH)
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "")

# When running from a py2app bundle, mlx & mlx_whisper are vendored under
# Contents/Resources/vendor (they don't survive py2app's normal scanning
# because mlx is a namespace package with C extensions + Metal libs).
def _add_vendor_path():
    # In a bundle, this file lives in Contents/Resources; sys.path[0] covers it.
    for base in sys.path[:]:
        vendor = os.path.join(base, "vendor")
        if os.path.isdir(os.path.join(vendor, "mlx")):
            if vendor not in sys.path:
                sys.path.insert(0, vendor)
            return
    # Fallback: relative to this file (Resources dir)
    here = os.path.dirname(os.path.abspath(__file__))
    vendor = os.path.join(here, "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(0, vendor)


_add_vendor_path()

from AppKit import NSApplication
from Alpha3Stone_Transcribe.app_delegate import AppDelegate


def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.activateIgnoringOtherApps_(True)
    app.run()


if __name__ == "__main__":
    main()
