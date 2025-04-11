"""
VIM Microagent module for OpenHands.

This module provides integration with Neovim for efficient code editing operations.
The VIM microagent is designed to work in headless Docker environments and pass
code changes back to be presented in the chat window.
"""

from openhands.microagent.vim.vim_agent import VimMicroAgent, get_vim_agent
from openhands.microagent.vim.operations import VimOperations
from openhands.microagent.vim.integration import (
    edit_file,
    add_import,
    insert_after_pattern,
    get_server_status,
    ensure_server_running
)

__all__ = [
    'VimMicroAgent', 
    'get_vim_agent', 
    'VimOperations',
    'edit_file',
    'add_import',
    'insert_after_pattern',
    'get_server_status',
    'ensure_server_running'
] 