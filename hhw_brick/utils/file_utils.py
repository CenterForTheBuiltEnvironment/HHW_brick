"""
File and directory utilities for HHW Brick


Author: Mingchen Li
"""

import shutil
from pathlib import Path
from typing import List, Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create if it doesn't

    Args:
        path: Directory path

    Returns:
        Path object of the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_list(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """
    Get list of files in a directory

    Args:
        directory: Directory path
        pattern: Glob pattern for file matching (default: "*")
        recursive: If True, search recursively (default: False)

    Returns:
        List of Path objects for matching files
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return []

    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))

    # Filter to only include files (not directories)
    return [f for f in files if f.is_file()]


def copy_file(
    src: Union[str, Path],
    dst: Union[str, Path],
    create_dirs: bool = True
) -> Path:
    """
    Copy a file from source to destination

    Args:
        src: Source file path
        dst: Destination file path
        create_dirs: If True, create destination directory if it doesn't exist

    Returns:
        Path object of the destination file

    Raises:
        FileNotFoundError: If source file doesn't exist
    """
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    if create_dirs:
        dst_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(src_path, dst_path)
    return dst_path

