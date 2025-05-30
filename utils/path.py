import os
from pathlib import Path
from typing import List
import ctypes

def pwd() -> str:
    current_dir = os.getcwd()
    if not os.path.exists(current_dir):
        current_dir = "/"
    return current_dir


def path_startswith(base: str, target: str) -> bool:
    """
    Checks whether 'target' path is inside or equal to 'base' path.

    Handles:
    - Windows drive letters (case-insensitive)
    - Normalization
    - Symlink resolution (if needed)
    """
    try:
        base_path = Path(base).resolve(strict=False).absolute()
        target_path = Path(target).resolve(strict=False).absolute()

        # Convert to string and normalize (handle case-insensitive on Windows)
        base_str = str(base_path)
        target_str = str(target_path)

        if os.name == "nt":  # Windows
            base_str = base_str.lower()
            target_str = target_str.lower()

        # Add trailing slash to prevent partial matches (e.g., /foo vs /foobar)
        base_str = base_str.rstrip("\\/") + os.sep
        target_str = target_str.rstrip("\\/") + os.sep

        return target_str.startswith(base_str)
    except Exception:
        return False


def is_path_excluded(path: str, exclude_paths: List[str]) -> bool:
    for exclude_path in exclude_paths:
        if path_startswith(exclude_path, path):
            return True
    return False


def cleanup_path_list(path_list: List[str]) -> List[str]:
    cleaned_list = []

    if not isinstance(path_list, list):
        raise ValueError("path_list must be a list")

    for path in path_list:
        if not Path(path).exists():
            continue
        cleaned_list.append(str(Path(path).resolve()))
    return cleaned_list


def is_hidden(filepath: str) -> bool:
    if os.name == 'nt':  # Windows
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
        except Exception:
            return False
    else:
        return os.path.basename(filepath).startswith(".")