---
name: vim
type: knowledge
version: "1.0.0"
agent: CodeActAgent
triggers:
  - vim
  - neovim
  - edit
  - vim-agent
  - edit code
  - efficient editing
---

# VIM Microagent

The VIM microagent provides integration with a headless Neovim instance running in a Docker container to enable efficient, precise code editing. It maintains persistent editor state between operations, allowing for more efficient editing workflows, and passes code changes back to be presented in the chat window.

## Key Features

- Runs a headless Neovim server in a Docker container
- Auto-installs Neovim if not available in the container
- Maintains persistent editor state between operations
- Enables precise code navigation and editing
- Supports semantic code operations (finding functions, classes, methods)
- Reduces the need for full file rewrites for small changes
- Returns changes in diff format for display in the chat window

## Basic Operations

The VIM microagent supports the following basic operations:

- Opening files
- Navigating to specific lines or patterns
- Inserting, replacing, and deleting text
- Saving files

## Semantic Operations

The VIM microagent also supports higher-level semantic operations:

- Finding and editing functions
- Finding and editing classes and methods
- Adding import statements
- Creating new files

## Integration with OpenHands

The VIM microagent can be used directly from Python code with the OpenHands runtime:

```python
from openhands.microagent.vim import edit_file, add_import

# Edit a function
result = edit_file(
    file_path="path/to/file.py",
    function_name="my_function",
    content="def my_function():\n    return 'new implementation'"
)

# Display changes in the chat window
print(result['changes'])

# Add an import statement
result = add_import("path/to/file.py", "import os")
print(result['changes'])
```

## Command-Line Interface

The VIM microagent includes a command-line interface for testing and manual operations:

```bash
# Start the Neovim server
openhands-vim server start

# Open a file
openhands-vim file open path/to/file.py

# Edit a function
openhands-vim edit function path/to/file.py function_name --content "def function_name():\n    return 'new implementation'"

# Add an import
openhands-vim edit import path/to/file.py "import some_module"

# Get recorded changes
openhands-vim changes
```

## Integration with Graph Memory

In the future, the VIM microagent will be integrated with a graph-based semantic code understanding component to enable more intelligent code editing operations that understand the structure and relationships in the code.
