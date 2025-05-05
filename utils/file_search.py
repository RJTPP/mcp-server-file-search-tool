from pathlib import Path
from typing import Optional, Union, Literal
import os
from datetime import datetime
from collections import deque
import re


from .path import pwd, cleanup_path_list, is_path_excluded, is_hidden


class FileSearchTool:
    def __init__(self, init_dir: str, exclude_paths: list[str], hide_hidden: bool = True, default_time_limit: int = 10):
        self.root_path = Path(pwd()).root
        self._INIT_DIR = str(Path(init_dir).resolve()) if init_dir else pwd()
        self._SHOW_HIDDEN = not hide_hidden
        self._DEFAULT_TIME_LIMIT = default_time_limit        
        self.base_dir = self._INIT_DIR
        self.exclude_paths = cleanup_path_list(exclude_paths)

    def _resolve_path(self, rel_path: str) -> str:
        p = Path(rel_path).expanduser()
        # 1) If the user passed an absolute path, trust it:
        if p.is_absolute():
            return str(p.resolve(strict=False))
        # 2) Otherwise, interpret it *inside* your base_dir:
        return str((Path(self.base_dir) / p).resolve(strict=False))

    def get_current_dir(self) -> str:
        return self.base_dir


    # MARK: TEMPORARY TEST FUNCTION
    def get_exclude_paths(self) -> dict[str, list[str]]:
        return { "exclude_paths": self.exclude_paths}


    def change_dir(self, path: str) -> str:
        """
        Change the current directory. Equivalent to `cd`.
        """
        resolved = self._resolve_path(path)

        # 1) Check existence on the resolved path
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Path `{resolved}` does not exist.")

        # 2) Check if it's a directory
        if not os.path.isdir(resolved):
            raise NotADirectoryError(f"`{resolved}` is not a directory.")

        # 3) Check exclusion on the same canonical path
        if is_path_excluded(resolved, self.exclude_paths):
            raise PermissionError(f"Permission denied for `{resolved}`.")

        # 4) Update base_dir to the resolved path
        self.base_dir = resolved
        return self.base_dir
        

    def get_path_type(self, paths: list[str]) -> list[tuple[str, str]]:
        """
        Get the type of the given path.

        Args:
            paths (list[str]): List of paths or a single path to get the type of.

        Returns:
            list[tuple[str, str]]: List of tuples of (path, type).
        """
        def _sub_get_path_type(path: str) -> str:
            if not os.path.exists(path):
                return "not found"
            file_type = "unknown"
            if os.path.isdir(path):
                file_type = "directory"
            elif os.path.islink(path):
                file_type = "symbolic link"
            elif os.path.isfile(path):
                file_type = "file"
            return file_type
        
        return [(p, _sub_get_path_type(p)) for p in paths]


    def list_file_paths(
        self,
        base_dir: Optional[str] = None,
        show_hidden: bool = False,
        limit: int = -1,
        time_limit: Optional[float] = None,
        max_nested_level: int = 1,
        search_mode: Literal["bfs", "dfs"] = "bfs",
        start_from: int = 0,
        abs_path: bool = False,
        file_only: bool = False,
    ) -> dict[str, Union[list[str], float, bool]]:
        """
        List file paths in the given directory, including directories and symbolic links.

        Args:
            base_dir (str): Base directory to start the search from.
            show_hidden (bool): Include hidden files (those starting with '.'). Can be overridden by the user.
            limit (int): Maximum number of files to return. Set to -1 for no limit.
            time_limit (Optional[float]): Seconds after which to abort (-1 = no limit, None = default).
            max_nested_level (int): Depth to recurse: 0 = only root, 1 = root+its subdirs, -1 = unlimited.
            search_mode (Literal["bfs", "dfs"]): Search mode: "bfs" (recommended) or "dfs".
            start_from (int): Starting index of files to return.
            abs_path (bool): If true, return absolute paths.
            file_only (bool): If true, only return files.

        Returns:
            dict[str, list[str] | None]: Dict with:
                - 'results': List of files. Sorted alphabetically.
                - 'time_elapsed': Time elapsed in seconds.
                - 'is_limit_exceeded': True if the limit was exceeded.
                - 'is_time_limit_exceeded': True if the time limit was exceeded.
        """
        if not self._SHOW_HIDDEN:
            show_hidden = False
        
        if time_limit is None:
            time_limit = self._DEFAULT_TIME_LIMIT

        if base_dir in [None, ""]:
            base_dir = self.base_dir
        
        base_dir = os.path.abspath(base_dir) if base_dir else self.base_dir
        start_time = datetime.now()
        results, count = [], 0
        is_limit_exceeded = False
        is_time_limit_exceeded = False

        # Initialize a queue or stack for BFS/DFS
        # Each item is (directory_path, current_depth)
        queue = deque([(base_dir, 0)])

        while queue:
            # Pop according to mode
            current_dir, depth = (
                queue.popleft() if search_mode == "bfs" else queue.pop()
            )

            # Respect depth limit (-1 means unlimited)
            if max_nested_level >= 0 and depth > max_nested_level:
                continue

            try:
                entries = os.listdir(current_dir)
            except (PermissionError, FileNotFoundError):
                continue

            # Optionally skip hidden
            entries = [e for e in entries if show_hidden or not is_hidden(e)]
            entries.sort()

            # Apply start_from only at the root level
            if current_dir == base_dir and start_from > 0:
                entries = entries[start_from:]

            for name in entries:
                full = os.path.join(current_dir, name)
                if is_path_excluded(full, self.exclude_paths):
                    continue

                # If it’s a directory, enqueue for further traversal
                if os.path.isdir(full):
                    if max_nested_level < 0 or depth < max_nested_level:
                        queue.append((full, depth + 1))
                    # If you only want files, skip adding dirs to results
                    if file_only:
                        continue

                # If file_only is set, only include files
                if file_only and not os.path.isfile(full):
                    continue

                results.append(full if abs_path else os.path.relpath(full, base_dir))
                count += 1

                if limit >= 0 and count >= limit:
                    is_limit_exceeded = True
                    break

                if time_limit != -1 and (datetime.now() - start_time).total_seconds() > time_limit:
                    is_time_limit_exceeded = True
                    break
            if is_limit_exceeded or is_time_limit_exceeded:
                break

        results.sort()

        return {
            "results": results,
            "time_elapsed": (datetime.now() - start_time).total_seconds(),
            "is_limit_exceeded": is_limit_exceeded,
            "is_time_limit_exceeded": is_time_limit_exceeded,
        }


    def search_file_name(
        self,
        regex_pattern: list[str],
        exclude_regex_patterns: Optional[list[str]] = None,
        base_path: Optional[str] = None,
        show_hidden: bool = False,
        time_limit: Optional[float] = None,
        max_nested_level: int = 1,
        search_mode: Literal["bfs", "dfs"] = "bfs",
    ) -> dict[str, list[str] | None]:
        """
        Search for files whose **path** match the given regex, level‑by‑level.

        Args:
            regex_pattern (list[str]): A list of **regex** pattern to match against filenames. Be sure to escape special characters.
            exclude_regex_patterns (list[str]): a list of **regex** patterns to exclude.
            base_path (str): Directory to start from (defaults to base_dir).
            show_hidden (bool): Include hidden files (those starting with '.'). Can be overridden by the user.
            time_limit (int): Seconds after which to abort (-1 = no limit, None = default).
            max_nested_level (int): Depth to recurse: 0 = only root, 1 = root+its subdirs, -1 = unlimited.
            search_mode (Literal["bfs", "dfs"]): Search mode: "bfs" (recommended) or "dfs".

        Returns:
            dict[str, list[str] | None]: Dict with
                - 'results': List of files matching regex. Sorted alphabetically.
                - 'time_elapsed': Time elapsed in seconds.
                - 'is_time_limit_exceeded': True if the time limit was exceeded.
        """
        if time_limit is None:
            time_limit = self._DEFAULT_TIME_LIMIT

        if base_path in [None, ""]:
            base_path = self.base_dir
        
        if not self._SHOW_HIDDEN:
            show_hidden = False

        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Path `{base_path}` does not exist.")
        if exclude_regex_patterns is None:
            exclude_regex_patterns = []
        
        try:
            pat = [re.compile(p) for p in regex_pattern]
        except re.error as e:
            raise ValueError(f"Invalid regex pattern in `regex_pattern`: {e}")

        try:
            ex_pat = [re.compile(p) for p in exclude_regex_patterns]
        except re.error as e:
            raise ValueError(f"Invalid regex pattern in `exclude_regex_patterns`: {e}")

        root = os.path.abspath(base_path or self.base_dir)
        
        start_time = datetime.now()
        
        results: list[str] = []
        queue = deque([(root, 0)]) if search_mode == "bfs" else [(root, 0)]  # (directory, current_level)
        
        while queue:
            current_dir, level = queue.popleft() if search_mode == "bfs" else queue.pop()
            
            if any(p.search(current_dir) for p in ex_pat) or is_path_excluded(current_dir, self.exclude_paths):
                continue  # skips everything for this directory
            
            # time‑quit check
            if time_limit != -1 and (datetime.now() - start_time).total_seconds() > time_limit:
                return {
                    "results": results,
                    "time_elapsed": (datetime.now() - start_time).total_seconds(),
                    "is_time_limit_exceeded": True,
                }
            
            try:
                entries = os.listdir(current_dir)
            except (PermissionError, FileNotFoundError):
                continue
            
            
            for name in entries:
                full_path = os.path.join(current_dir, name)
                
                # If it’s a file and matches, record it

                if not os.path.isdir(full_path):
                    for p in pat:
                        if not show_hidden and is_hidden(name):
                            continue
                        if p.search(name):
                            results.append(full_path)
                            break
                
                # If it’s a directory and we haven’t hit max_nested_level, enqueue its contents
                if os.path.isdir(full_path):
                    if max_nested_level < 0 or level < max_nested_level:
                        queue.append((full_path, level + 1))
                        
        
        results.sort()
        
        return {
            "results": results,
            "time_elapsed": (datetime.now() - start_time).total_seconds(),
            "is_time_limit_exceeded": False,
        }
    
    
    def read_files(self, file_paths: list[str]) -> dict[str, list[str] | None]:
        """
        Read the contents of the given files using `open()` function. Cannot read PDFs.

        Args:
            file_paths (list[str]): List of file paths to read.

        Returns:
            dict[str, list[str] | None]: Dict with:
                - 'results': Dict with file paths as keys and file contents as values.
                - 'time_elapsed': Time elapsed in seconds.
            
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        start_time = datetime.now()

        results = {}
        for file_path in file_paths:
            file_path = self._resolve_path(file_path)

            if is_path_excluded(file_path, self.exclude_paths):
                results[file_path] = "[Excluded]"
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    results[file_path] = file.read()
            except FileNotFoundError:
                results[file_path] = "[File not found]"
            except PermissionError:
                results[file_path] = "[Permission denied]"
            except Exception as e:
                results[file_path] = f"[Error: {e}]"
                
                
        return {
            "results": results,
            "time_elapsed": (datetime.now() - start_time).total_seconds(),
        }


    def search_file_contents(
        self, 
        file_paths: list[str], 
        regex_patterns: list[str], 
        context_lines: int = 0, 
        time_limit: Optional[float] = None, 
    ) -> dict[str, Union[list[list[str]], str, bool, float]]:
        """
        Search each file in `file_paths` list for lines matching ANY of `regex_patterns`,
        Returns, for each file that matches, a list of line‑blocks (each block is
        up to `context_lines` before/after the match). If a file cannot be read,
        its value is an error string.

        Args:
            file_paths (list[str]): List of file paths to search.
            regex_patterns (list[str]): List of regex strings to match lines against.
            context_lines (int): Number of context lines before and after each match.
            time_limit (float): Seconds after which to abort early (−1 = no limit, None = default).

        Returns:
            Dict with:
                - 'results': Dict with file paths as keys and lists of line blocks as values.
                - 'time_elapsed': Time elapsed in seconds.
                - 'is_time_limit_exceeded': True if the time limit was exceeded.
        """
        if time_limit is None:
            time_limit = self._DEFAULT_TIME_LIMIT

        start_time = datetime.now()
        try:
            include_re = [re.compile(p) for p in regex_patterns]
        except re.error as e:
            raise ValueError(f"Invalid regex pattern in `regex_pattern`: {e}")
        
        results: dict[str, list[list[str]] | str] = {}

        for rel_path in file_paths:
            # --- Time limit check ---
            if time_limit >= 0 and (datetime.now() - start_time).total_seconds() > time_limit:
                # emit final status

                return {
                    "results": results,
                    "time_elapsed": (datetime.now() - start_time).total_seconds(),
                    "is_time_limit_exceeded": True,
                }

            abs_path = self._resolve_path(rel_path)
            # --- Emit status per file ---


            # --- Read file ---
            matches = []
            
            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()

                for idx, line in enumerate(lines):
                    if any(r.search(line) for r in include_re):
                        start = max(0, idx - context_lines)
                        end = min(len(lines), idx + context_lines + 1)
                        block = "".join(lines[start:end])
                        matches.append(block)
                        
            except FileNotFoundError:
                results[abs_path] = "[File not found]"
                continue
            except PermissionError:
                results[abs_path] = "[Permission denied]"
                continue
            except IsADirectoryError:
                results[abs_path] = "[Error: Is a directory. Please provide a file path.]"
                continue
            except Exception as e:
                results[abs_path] = f"[Error: {e}]"
                continue

            if matches:
                results[abs_path] = matches

        # --- Final status emit ---



        return {
            "results": results,
            "time_elapsed": (datetime.now() - start_time).total_seconds(),
            "is_time_limit_exceeded": False,
        }
        