# VIM Microagent

## Overview

This microagent provides a headless interface to Vim or Neovim for text editing tasks within the OpenHands platform. It runs in a Docker container and allows for file editing, change tracking, and other Vim operations.

## Architecture

The VIM microagent consists of:

1. **Core Agent**: Handles communication with the OpenHands platform and manages editing sessions
2. **Change Tracker**: Monitors and records changes made to files during editing sessions
3. **Vim Interface**: Interfaces with Vim or Neovim in a headless environment
4. **Semantic Graph Component**: (Future) Will provide semantic understanding of code being edited

## Requirements

- OpenHands platform running in Docker
- Custom runtime image with Vim or Neovim pre-installed (see Docker Integration section)

## Docker Integration

For detailed instructions on Docker integration, see [Docker Integration Guide](docker-instructions.md).

The VIM microagent requires either Vim or Neovim to be available in the container. The agent:

1. Checks if Vim or Neovim is installed
2. Uses the available editor (preferring Neovim if both are available)
3. Attempts to install Vim/Neovim if neither is found (fallback mechanism)

For optimal performance, we recommend using a custom Docker runtime image with Vim/Neovim pre-installed.

## Usage

The microagent provides a simple interface for:

```python
from openhands.microagent.vim import VimAgent

# Initialize the agent
vim_agent = VimAgent()

# Edit a file
result = vim_agent.edit_file("/path/to/file.txt", "i This is inserted text\nThis is a new line\x1b:wq")

# Get changes made
changes = vim_agent.get_changes()

# Display changes
vim_agent.display_changes()
```

## Future Work

1. **Enhanced Change Tracking**: Provide detailed diffs between file versions
2. **Semantic Understanding**: Integrate with the semantic graph to understand code context
3. **Advanced Vim Operations**: Support for macros, registers, and complex editing patterns
4. **Interactive Mode**: Support for more interactive editing sessions
5. **Syntax-aware Editing**: Leverage language-specific features for better editing
