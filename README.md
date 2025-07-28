# MCP Server - File Search Tool 🗂️

An MCP (Model Context Protocol) server that provides powerful file system search and inspection capabilities via the MCP protocol. Use this tool to list directories, search file names, read file contents (including PDF and DOCX), and perform regex‑based content searches with context.

## Features

- **List file paths**: Breadth‑first or depth‑first listing, with paging and nested‑level control.  
- **Search file names**: Regex‑based file name search.  
- **Read files**: Read text, PDF, and DOCX files with optional character limits.  
- **Search file contents**: Regex‑based content search with configurable context lines.  
- **Allowed paths**: Restrict server to only browse and search within configured directories.  
- **Exclude paths**: Prevent sensitive directories from being accessed.  
- **Hide hidden files**: Optionally ignore files and directories beginning with a dot.  
- **Path masking**: Replace configured path segments with tokens for privacy.  

### Prerequisites

- [Python](https://www.python.org) 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RJTPP/mcp-server-file-search-tool
cd mcp-server-file-search-tool
```

2. Create virtual environment and install dependencies:
```bash
uv sync
```

### Running the Server

Start the server (default port 6277):
```bash
uv run server.py
```

## Claude Desktop Integration

To add this server to Claude Desktop:

```bash
mcp install server.py --name "File Search Tool"
```

Or manually add it to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "File Search Tool": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-sever-file-search-tool/",
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

## Configuration

1. Copy the example configuration:

```bash
   cp config_example.json config.json
   ```

2. Edit config.json to customize:

```json
{
  "DEFAULT_TIME_LIMIT": 10,
  "HIDE_HIDDEN_FILES": true,
  "HOST": "127.0.0.1",
  "PORT": 6277,
  "ALLOWED_PATHS": [
    "/path/to/allowed/directory"
  ],
  "EXCLUDE_PATHS": [
    "/path/to/excluded/directory"
  ],
  "PATH_MASKER": {
    "ENABLED": true,
    "MODE": "segment",
    "MASK_TOKEN": "MASK",
    "LOOK_FOR": [
      "path_to_mask"
    ]
  }
}
```

### Required Fields

- `ALLOWED_PATHS` is **required**. The server will not start unless at least one allowed path is configured.

### Configuration Field Descriptions

| Field                     | Type            | Description                                                                 |
|--------------------------|-----------------|-----------------------------------------------------------------------------|
| `DEFAULT_TIME_LIMIT`     | `int`           | Max execution time for searches (in seconds).                              |
| `HIDE_HIDDEN_FILES`      | `bool`          | If `true`, ignores files and directories that start with `.`               |
| `HOST`                   | `string`        | IP address the server will bind to (e.g., `"127.0.0.1"`).                  |
| `PORT`                   | `int`           | Port number to listen on (e.g., `6277`).                                   |
| `ALLOWED_PATHS`          | `list[string]`  | **Required.** Directories the server is allowed to access and search.      |
| `EXCLUDE_PATHS`          | `list[string]`  | Directories to explicitly block, even if inside allowed paths.             |
| `PATH_MASKER`            | `object`        | Optional masking settings for privacy.                                     |
| `PATH_MASKER.ENABLED`    | `bool`          | Enables or disables path masking.                                          |
| `PATH_MASKER.MODE`       | `"segment"` or `"prefix"` | Masking mode: `"segment"` replaces matching segments; `"prefix"` masks full path prefixes. |
| `PATH_MASKER.MASK_TOKEN` | `string`        | The token to replace matched path segments (e.g., `"MASK"`).               |
| `PATH_MASKER.LOOK_FOR`   | `list[string]`  | List of path segments to be masked when found in full paths.               |


## Security

> [!WARNING]
> This server does **not** implement authentication or encryption.  
> It is designed **for local, personal use only**.
> Do **not** expose the server to untrusted networks or use it in production without adding proper security measures.


## License

This project is released under the [MIT License](LICENSE).

You are free to use, modify, and distribute this software under the terms of the MIT License. See the LICENSE file for detailed terms and conditions.
