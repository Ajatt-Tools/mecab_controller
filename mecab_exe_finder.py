# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import functools
import os
import pathlib
import shutil
import sys
from collections.abc import Sequence

IS_MAC = sys.platform.startswith("darwin")
IS_WIN = sys.platform.startswith("win32")
SUPPORT_DIR = pathlib.Path(__file__).parent.joinpath("support").resolve()
assert SUPPORT_DIR.is_dir(), "bundled support dir must be present"


@functools.cache
def default_hardcoded_paths() -> Sequence[pathlib.Path]:
    """Return common executable directories."""
    return (
        pathlib.Path("/usr/bin"),
        pathlib.Path("/opt/homebrew/bin"),
        pathlib.Path("/usr/local/bin"),
        pathlib.Path("/bin"),
        pathlib.Path.home() / ".local" / "bin",
    )


@functools.cache
def support_exe_suffix() -> str:
    """
    The mecab executable file in the "support" dir has a different suffix depending on the platform.
    """
    if IS_WIN:
        return ".exe"
    elif IS_MAC:
        return ".mac"
    else:
        return ".lin"


def get_bundled_executable(name: str) -> str:
    """
    Get path to executable in the bundled "support" folder.
    Used to provide 'mecab' on computers where it is not installed system-wide or can't be found.
    """
    path_to_exe = SUPPORT_DIR.joinpath(name + support_exe_suffix())
    assert path_to_exe.is_file(), f"{path_to_exe} doesn't exist. Can't recover."
    if not IS_WIN:
        os.chmod(path_to_exe, 0o755)
    return str(path_to_exe.resolve())


def is_executable_file(path: pathlib.Path) -> bool:
    """Return True if path points to an executable file."""
    return path.is_file() and os.access(path, os.X_OK)


def find_executable_hardcoded(name: str) -> str | None:
    """Search for an executable by name in a list of common installation directories."""
    for path_to_dir in default_hardcoded_paths():
        if is_executable_file(path_to_exe := path_to_dir / name):
            return str(path_to_exe.resolve())
    return None


@functools.cache
def find_executable(name: str) -> str:
    """
    Return a system executable, then a standard fallback path, then the bundled executable.

    macOS GUI applications commonly omit Homebrew from PATH, so inspect its
    standard install location before falling back to the bundled executable.
    """
    return shutil.which(name) or find_executable_hardcoded(name) or get_bundled_executable(name)
