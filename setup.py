"""py2app build configuration for Alpha3Stone Transcribe.

Build:  ./../transcription_venv/bin/python setup.py py2app
Output: dist/Alpha3Stone Transcribe.app
"""

import sys
import os
import glob
# py2app's modulegraph recurses deeply through scipy/numba ASTs
sys.setrecursionlimit(10000)

from setuptools import setup

SITE = "../transcription_venv/lib/python3.10/site-packages"

# mlx is a namespace package with C extensions + Metal libs that py2app's
# automatic scanning copies incompletely. Bundle the whole dir as a resource
# and prepend it to sys.path at runtime (see main.py).
def tree(src_rel):
    """Collect (dest_dir, [files]) tuples for a directory tree, for data_files."""
    src = os.path.join(SITE, src_rel)
    result = []
    for root, _dirs, files in os.walk(src):
        if "__pycache__" in root:
            continue
        rel = os.path.relpath(root, SITE)
        paths = [os.path.join(root, f) for f in files if not f.endswith(".pyc")]
        if paths:
            result.append((os.path.join("vendor", rel), paths))
    return result

APP = ["main.py"]
DATA_FILES = tree("mlx")
ICNS_ICON = "icons/icon.icns"

OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Alpha3Stone Transcribe",
        "CFBundleDisplayName": "Alpha3Stone Transcribe",
        "CFBundleIdentifier": "com.alpha3stone.transcribe",
        "CFBundleVersion": "0.2.0",
        "CFBundleShortVersionString": "0.2.0",
        "NSHighResolutionCapable": True,
        "CFBundleIconFile": "icon.icns",
        "LSMinimumSystemVersion": "13.0",
        # Foreground GUI app with a Dock icon
        "LSUIElement": False,
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "Audio File",
                "CFBundleTypeExtensions": ["m4a", "mp3", "wav", "flac"],
                "CFBundleTypeRole": "Viewer",
            }
        ],
    },
    "packages": [
        "Alpha3Stone_Transcribe",
        "mlx_whisper",
        "numpy",
        "tiktoken",
        "tqdm",
        "numba",
        "scipy",
        "huggingface_hub",
    ],
    "includes": [
        "objc",
        "AppKit",
        "Foundation",
        "CoreFoundation",
    ],
    "excludes": [
        "matplotlib",
        "PIL",
        "tkinter",
        "pytest",
        "setuptools",
        # torch is only reached via mlx_whisper/torch_whisper.py, which nothing
        # imports on the MLX inference path. huggingface_hub's torch imports are
        # all guarded. Dropping torch + its deps cuts ~407MB from the bundle.
        "torch",
        "torchgen",
        "torchvision",
        "torchaudio",
        "functorch",
        "sympy",
    ],
    # Bundle conda's libffi (conda Python links _ctypes against @rpath/libffi.8.dylib)
    "frameworks": [
        os.path.expanduser("~/miniforge3/lib/libffi.8.dylib"),
        os.path.expanduser("~/miniforge3/lib/libssl.3.dylib"),
        os.path.expanduser("~/miniforge3/lib/libcrypto.3.dylib"),
    ],
}

setup(
    app=APP,
    name="Alpha3Stone Transcribe",
    data_files=DATA_FILES + [(".", [ICNS_ICON])],
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
