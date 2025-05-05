import os
from pathlib import Path

def pwd():
    current_dir = os.getcwd()
    if not os.path.exists(current_dir):
        current_dir = "/"
    return current_dir


def is_path_excluded(path: str, exclude_paths: list[str]) -> bool:
    for exclude_path in exclude_paths:
        if path.startswith(exclude_path):
            return True
    return False


def cleanup_path_list(path_list: list[str]) -> list[str]:
    cleaned_list = []

    if not isinstance(path_list, list):
        raise ValueError("path_list must be a list")

    for path in path_list:
        if not Path(path).exists():
            continue
        cleaned_list.append(Path(path).absolute().as_posix())
    return cleaned_list