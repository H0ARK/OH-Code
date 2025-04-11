"""
Integration module for the VIM microagent.

This module provides functions to integrate the VIM microagent with the
OpenHands runtime and chat interface.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from openhands.core.logger import openhands_logger as logger
from openhands.microagent.vim.vim_agent import get_vim_agent
from openhands.microagent.vim.operations import VimOperations


def edit_file(file_path: Union[str, Path], function_name: Optional[str] = None, 
             class_name: Optional[str] = None, method_name: Optional[str] = None,
             content: Optional[str] = None) -> Dict:
    """
    Edit a file using the VIM microagent and return the changes for display in the chat window.
    
    This function provides a high-level interface for the OpenHands runtime to interact
    with the VIM microagent.
    
    Args:
        file_path: Path to the file to edit
        function_name: Optional name of the function to edit
        class_name: Optional name of the class to edit
        method_name: Optional name of the method to edit within the class
        content: New content for the function/method
        
    Returns:
        Dict: Dictionary with success status and changes for display in the chat window
    """
    vim = get_vim_agent()
    success = False
    message = ""
    
    try:
        # Ensure the file path exists
        file_path = Path(file_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Different editing operations based on parameters
        if function_name is not None:
            # Edit a function
            success = VimOperations.edit_function(file_path, function_name, content)
            message = f"Edited function: {function_name} in {file_path}"
        elif class_name is not None and method_name is not None:
            # Edit a class method
            success = VimOperations.edit_class(file_path, class_name, method_name, content)
            message = f"Edited method: {method_name} in class {class_name} in {file_path}"
        elif class_name is not None:
            # Edit a class (navigate to it)
            success = VimOperations.edit_class(file_path, class_name)
            message = f"Navigated to class: {class_name} in {file_path}"
        elif not file_path.exists() and content is not None:
            # Create a new file
            success = VimOperations.create_file(file_path, content)
            message = f"Created file: {file_path}"
        else:
            # Simple edit with content
            vim.open_file(file_path)
            if content is not None:
                # Replace the entire file
                lines = content.split('\n')
                success = vim.replace_range(1, len(vim.get_current_file_content().split('\n')) + 1, lines)
                vim.save_file()
                message = f"Edited file: {file_path}"
            else:
                # Just open the file
                success = True
                message = f"Opened file: {file_path}"
        
        # Get the changes in diff format for display in the chat window
        changes = vim.format_changes_for_chat()
        
        return {
            "success": success,
            "message": message,
            "changes": changes
        }
    
    except Exception as e:
        logger.error(f"Error in edit_file: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "changes": ""
        }


def add_import(file_path: Union[str, Path], import_statement: str) -> Dict:
    """
    Add an import statement to a file and return the changes for display in the chat window.
    
    Args:
        file_path: Path to the file to add the import to
        import_statement: Import statement to add
        
    Returns:
        Dict: Dictionary with success status and changes for display in the chat window
    """
    try:
        success = VimOperations.add_import(file_path, import_statement)
        vim = get_vim_agent()
        
        return {
            "success": success,
            "message": f"Added import: {import_statement} to {file_path}" if success else 
                      f"Failed to add import: {import_statement} to {file_path}",
            "changes": vim.format_changes_for_chat()
        }
    
    except Exception as e:
        logger.error(f"Error in add_import: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "changes": ""
        }


def insert_after_pattern(file_path: Union[str, Path], pattern: str, new_content: str) -> Dict:
    """
    Insert content after a pattern match in a file and return the changes for display in the chat window.
    
    Args:
        file_path: Path to the file to edit
        pattern: Pattern to search for
        new_content: Content to insert after the pattern
        
    Returns:
        Dict: Dictionary with success status and changes for display in the chat window
    """
    try:
        success = VimOperations.insert_after_pattern(file_path, pattern, new_content)
        vim = get_vim_agent()
        
        return {
            "success": success,
            "message": f"Inserted content after pattern '{pattern}' in {file_path}" if success else 
                      f"Failed to insert content after pattern '{pattern}' in {file_path}",
            "changes": vim.format_changes_for_chat()
        }
    
    except Exception as e:
        logger.error(f"Error in insert_after_pattern: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "changes": ""
        }


def get_server_status() -> Dict:
    """
    Get the status of the Neovim server.
    
    Returns:
        Dict: Dictionary with server status
    """
    vim = get_vim_agent()
    
    return {
        "running": vim._is_server_running(),
        "connected": vim._is_connected
    }


def ensure_server_running() -> Dict:
    """
    Ensure the Neovim server is running.
    
    Returns:
        Dict: Dictionary with server status
    """
    vim = get_vim_agent()
    
    if not vim._is_server_running():
        success = vim.start_server()
    else:
        success = True
    
    return {
        "success": success,
        "running": vim._is_server_running(),
        "connected": vim._is_connected
    } 