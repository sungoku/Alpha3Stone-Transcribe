"""py2app build configuration for Alpha3Stone Transcribe.

Build:  python setup.py py2app
Output: dist/Alpha3Stone Transcribe.app
"""

import sys
import os
import site
# py2app's modulegraph recurses deeply through scipy/numba ASTs
sys.setrecursionlimit(10000)

from setuptools import setup

# Auto-detect site-packages: prefer the first writable path in current env
SITE = site.getsitepackages()[0] if site.getsitepackages() else os.path.join(sys.prefix, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")

# Find conda dynamic libraries needed by _ctypes / ssl
def _find_conda_libs():
    """Locate libffi, libssl, libcrypto from the current conda env."""
    # sys.prefix points to the active conda env root
    for base in (sys.prefix, os.path.dirname(sys.prefix)):
        lib = os.path.join(base, "lib")
        candidates = [
            os.path.join(lib, "libffi.8.dylib"),
            os.path.join(lib, "libssl.3.dylib"),
            os.path.join(lib, "libcrypto.3.dylib"),
        ]
        if all(os.path.isfile(f) for f in candidates):
            return candidates
    # Fallback: use conda show / CONDA_PREFIX
    conda_prefix = os.environ.get("CONDA_PREFIX", "")
    if conda_prefix:
        lib = os.path.join(conda_prefix, "lib")
        candidates = [
            os.path.join(lib, "libffi.8.dylib"),
            os.path.join(lib, "libssl.3.dylib"),
            os.path.join(lib, "libcrypto.3.dylib"),
        ]
        if all(os.path.isfile(f) for f in candidates):
            return candidates
    # Last resort: search lib*.{8,3}.dylib in sys.prefix/lib
    lib = os.path.join(sys.prefix, "lib")
    result = []
    for name in ("libffi.8.dylib", "libssl.3.dylib", "libcrypto.3.dylib"):
        path = os.path.join(lib, name)
        if os.path.isfile(path):
            result.append(path)
    return result

FRAMEWORKS = _find_conda_libs()

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
    "frameworks": FRAMEWORKS,
}

setup(
    app=APP,
    name="Alpha3Stone Transcribe",
    data_files=DATA_FILES + [(".", [ICNS_ICON])],
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
