# server.py
from os import curdir
from mcp.server.fastmcp import FastMCP
from utils import FileSearchTool, return_message
from config import BASE_DIR, EXCLUDE_PATHS, HIDE_HIDDEN_FILES, DEFAULT_TIME_LIMIT
from typing import Optional

file_search_tools = FileSearchTool(BASE_DIR, EXCLUDE_PATHS, HIDE_HIDDEN_FILES, DEFAULT_TIME_LIMIT)

# Create an MCP server
mcp = FastMCP(
    name="File Search Tool",
    host="0.0.0.0",
    port=8000,
)



@mcp.tool()
def get_current_dir() -> dict:
    """
    Get the current directory. Equivalent to `pwd`.

    Args:
        None

    Returns:
        dict: A dictionary with the following keys:
            - results (str): Current directory path
            - success (bool): True if the operation was successful
            - response_message (str): A message indicating the result of the operation
    """
    current_dir = file_search_tools.get_current_dir()
    if not current_dir:
        return return_message(
            results=None,
            success=False,
            response_message="Failed to get current directory.",
        )
    return return_message(
        results=current_dir,
        success=True,
        response_message="Current directory retrieved successfully.",
    )


@mcp.tool()
def change_dir(path: Optional[str] = None) -> dict:
    """
    Change the current directory. Equivalent to `cd`.

    Args:
        path (str): Path to change to. Set to None to revert to the initial directory.

    Returns:
        dict: A dictionary with the following keys:
            - results (str): Current directory path
            - success (bool): True if the operation was successful
            - response_message (str): A message indicating the result of the operation
    """
    if not path:
        path = file_search_tools._INIT_DIR
    try:
        new_dir = file_search_tools.change_dir(path)
        return return_message(results=new_dir, success=True, response_message="Changed directory.")
    except FileNotFoundError:
        return return_message(results=file_search_tools.base_dir, success=False, response_message=f"Path not found. Reverting back to `{file_search_tools.base_dir}`.")
    except PermissionError:
        return return_message(results=file_search_tools.base_dir, success=False, response_message=f"Permission denied. Reverting back to `{file_search_tools.base_dir}`.")
    except NotADirectoryError:
        return return_message(results=file_search_tools.base_dir, success=False, response_message=f"Path is not a directory. Reverting back to `{file_search_tools.base_dir}`.")
    except Exception as e:
        return return_message(results=file_search_tools.base_dir, success=False, response_message=f"Failed to change directory. Reverting back to `{file_search_tools.base_dir}`. Error: {str(e)}")

@mcp.tool()
def get_path_type(paths: list[str]) -> dict:
    """
    Get the type of the given path.

    Args:
        paths (list[str]): List of paths or a single path to get the type of.

    Returns:
        dict: A dictionary with the following keys:
            - results (list[tuple[str, str]]): List of tuples of (path, type).
            - success (bool): True if the operation was successful
            - response_message (str): A message indicating the result of the operation
    """
    try:
        path_type = file_search_tools.get_path_type(paths)
        return return_message(results=path_type, success=True, response_message=f"{len(paths)} path type{'s' if len(paths) > 1 else ''} retrieved successfully.")
    except Exception as e:
        return return_message(results=None, success=False, response_message=str(e))

@mcp.tool()
def list_file_paths(
    base_dir: str = None,
    show_hidden: Optional[bool] = None,
    limit: int = -1,
    time_limit: Optional[float] = None,
    max_nested_level: int = 1,
    search_mode: str = "bfs",
    start_from: int = 0,
    abs_path: bool = False,
    file_only: bool = False,
) -> dict:
    """
    List file paths in the given directory, including directories and symbolic links. Equivalent to `ls`.

    Args:
        base_dir (str): Base directory to start the search from.
        show_hidden (bool): Include hidden files (those starting with '.'). Can be overridden by the user.
        limit (int): Maximum number of files to return. Set to -1 for no limit.
        time_limit (Optional[float]): Seconds after which to abort (-1 = no limit, None = default).
        max_nested_level (int): Depth to recurse: 0 = only root, 1 = root+its subdirs, -1 = unlimited.
        search_mode (str): Search mode: "bfs" (recommended) or "dfs".
        start_from (int): Starting index of files to return.
        abs_path (bool): If true, return absolute paths.
        file_only (bool): If true, only return files.

    Returns:
        dict: A dictionary with the following keys:
            - results (list[str]): List of files. Sorted alphabetically.
            - time_elapsed (float): Time elapsed in seconds.
            - response_message (str): A message indicating the result of the operation
    """
    try:
        query_result = file_search_tools.list_file_paths(
            base_dir=base_dir,
            show_hidden=show_hidden,
            limit=limit,
            time_limit=time_limit,
            max_nested_level=max_nested_level,
            search_mode=search_mode,
            start_from=start_from,
            abs_path=abs_path,
            file_only=file_only,
        )
        results = query_result['results']
        response_message = ""
        is_limit_exceeded = query_result['is_limit_exceeded']
        
        if is_limit_exceeded:
            response_message = f"File limit exceeded."

        response_message += f"{len(results)} file path{'s' if len(results) > 1 else ''} retrieved successfully."

        return return_message(results=results, success=True, response_message=response_message)
    except Exception as e:
        return return_message(results=None, success=False, response_message=str(e))


@mcp.tool()
def search_file_name(
    regex_pattern: list[str],
    exclude_regex_patterns: list[str] = None,
    base_path: str = None,
    time_limit: Optional[float] = None,
    max_nested_level: int = 1,
    search_mode: str = "bfs",
) -> dict:
    """
    Search for files whose **path** match the given regex, level‑by‑level.

    Args:
        regex_pattern (list[str]): A list of **regex** pattern to match against filenames. Be sure to escape special characters.
        exclude_regex_patterns (list[str]): a list of **regex** patterns to exclude.
        base_path (str): Directory to start from (defaults to base_dir).
        time_limit (Optional[float]): Seconds after which to abort (-1 = no limit, None = default).
        max_nested_level (int): Depth to recurse: 0 = only root, 1 = root+its subdirs, -1 = unlimited.
        search_mode (str): Search mode: "bfs" (recommended) or "dfs".

    Returns:
        dict[str, list[str] | None]: Dict with
            - 'results': List of files matching regex. Sorted alphabetically.
            - 'success': True if the operation was successful
            - 'time_elapsed': Time elapsed in seconds.
            - 'response_message': A message indicating the result of the operation
    """
    try:
        query_result = file_search_tools.search_file_name(
            regex_pattern=regex_pattern,
            exclude_regex_patterns=exclude_regex_patterns,
            base_path=base_path,
            time_limit=time_limit,
            max_nested_level=max_nested_level,
            search_mode=search_mode,
        )
        results = query_result['results']
        response_message = ""
        time_elapsed = query_result['time_elapsed']
        is_time_limit_exceeded = query_result['is_time_limit_exceeded']
        
        response_message = ""
        if is_time_limit_exceeded:
            response_message = f"Time limit exceeded."

        response_message += f"{len(results)} file path{'s' if len(results) > 1 else ''} retrieved successfully."

        return return_message(results=results, success=True, time_elapsed=time_elapsed, response_message=response_message)
    except Exception as e:
        return return_message(results=None, success=False, time_elapsed=None, response_message=str(e))

@mcp.tool()
def read_files(file_paths: list[str]) -> dict:
    """
    Read the contents of the given files using `open()` function. Cannot read PDFs.

    Args:
        file_paths (list[str]): List of file paths to read.

    Returns:
        dict[str, list[str] | None]: Dict with:
            - 'results': Dict with file paths as keys and file contents as values.
            - 'time_elapsed': Time elapsed in seconds.
            - 'response_message': A message indicating the result of the operation
    """
    try:
        query_result = file_search_tools.read_files(file_paths)
        results = query_result['results']
        time_elapsed = query_result['time_elapsed']
        
        return return_message(results=results, success=True, time_elapsed=time_elapsed, response_message=f"Successfully read {len(results)} file{'s' if len(results) > 1 else ''}.")
    except Exception as e:
        return return_message(results=None, success=False, time_elapsed=None, response_message=str(e))


@mcp.tool()
def search_file_contents(
    file_paths: list[str], 
    regex_patterns: list[str], 
    context_lines: int = 0, 
    time_limit: Optional[float] = None, 
) -> dict[str, list[list[str]] | str]:
    """
    Search each file in `file_paths` list for lines matching ANY of `regex_patterns`,
    Returns, for each file that matches, a list of line‑blocks (each block is
    up to `context_lines` before/after the match). If a file cannot be read,
    its value is an error string.

    Args:
        file_paths (list[str]): List of file paths to search.
        regex_patterns (list[str]): List of regex strings to match lines against.
        context_lines (int): Number of context lines before and after each match.
        time_limit (Optional[float]): Seconds after which to abort early (−1 = no limit, None = default).

    Returns:
        Dict with:
            - 'results': Dict with file paths as keys and lists of line blocks as values.
            - 'time_elapsed': Time elapsed in seconds.
            - 'response_message': A message indicating the result of the operation
    """
    try:
        query_result = file_search_tools.search_file_contents(file_paths, regex_patterns, context_lines, time_limit)
        results = query_result['results']
        time_elapsed = query_result['time_elapsed']
        is_time_limit_exceeded = query_result['is_time_limit_exceeded']
        
        response_message = ""
        if is_time_limit_exceeded:
            response_message = f"Time limit exceeded."

        response_message += f"{len(results)} file path{'s' if len(results) > 1 else ''} retrieved successfully."

        return return_message(results=results, success=True, time_elapsed=time_elapsed, response_message=response_message)
    except Exception as e:
        return return_message(results=None, success=False, time_elapsed=None, response_message=str(e))



if __name__ == "__main__":
    mcp.run()