"""
VIM Microagent for OpenHands

This module implements a headless Neovim-based microagent for efficient code editing.
It provides a bridge between OpenHands and Neovim's powerful editing capabilities.
"""

import os
import socket
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pynvim

from openhands.core.logger import openhands_logger as logger
from openhands.microagent.microagent import BaseMicroAgent
from openhands.microagent.types import MicroAgentMetadata, MicroAgentType


class VimMicroAgent:
    """
    VIM Microagent that provides efficient code editing capabilities through Neovim.
    
    This agent runs a headless Neovim instance in a Docker container and provides 
    methods to interact with it, allowing for precise, efficient code editing operations.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6666):
        """
        Initialize the VIM Microagent.
        
        Args:
            host: Host to run the Neovim server on
            port: Port to run the Neovim server on
        """
        self.host = host
        self.port = port
        self.nvim = None
        self._server_process = None
        self._is_connected = False
        self.changes_record = []
    
    def start_server(self) -> bool:
        """
        Start a headless Neovim server if one is not already running.
        First checks if neovim is installed, attempts to install it if not.
        
        Returns:
            bool: True if the server was started successfully, False otherwise
        """
        # Check if Neovim is installed
        if not self._is_neovim_installed():
            success = self._install_neovim()
            if not success:
                logger.error("Failed to install Neovim")
                return False
        
        if self._is_server_running():
            logger.info(f"Neovim server already running at {self.host}:{self.port}")
            return True
        
        try:
            # Start Neovim in headless mode with socket listening
            self._server_process = subprocess.Popen(
                ["nvim", "--headless", "--listen", f"{self.host}:{self.port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give the server a moment to start
            import time
            time.sleep(1)
            
            # Check if the server is now running
            if self._is_server_running():
                logger.info(f"Started Neovim server at {self.host}:{self.port}")
                return True
            else:
                logger.error("Failed to start Neovim server")
                return False
        except Exception as e:
            logger.error(f"Error starting Neovim server: {e}")
            return False
    
    def _is_neovim_installed(self) -> bool:
        """
        Check if Vim or Neovim is installed in the container.
        
        Returns:
            bool: True if either Vim or Neovim is installed, False otherwise
        """
        try:
            # Check for nvim (preferred)
            nvim_result = subprocess.run(
                ["which", "nvim"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            if nvim_result.returncode == 0:
                logger.info("Neovim is installed")
                return True
                
            # Check for vim (alternative)
            vim_result = subprocess.run(
                ["which", "vim"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            if vim_result.returncode == 0:
                logger.info("Vim is installed")
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking for Vim/Neovim: {e}")
            return False
    
    def _install_neovim(self) -> bool:
        """
        Attempt to install Neovim or Vim in the container.
        
        Returns:
            bool: True if installation was successful, False otherwise
        """
        logger.info("Vim/Neovim not found, attempting to install...")
        try:
            # Determine the container's OS
            os_release = subprocess.run(
                ["cat", "/etc/os-release"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            os_info = os_release.stdout.lower()
            
            if "debian" in os_info or "ubuntu" in os_info:
                # Install in Debian/Ubuntu
                subprocess.run(
                    ["apt-get", "update", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Try to install neovim first
                neovim_result = subprocess.run(
                    ["apt-get", "install", "-y", "neovim"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # If neovim installation failed, try vim
                if neovim_result.returncode != 0:
                    logger.info("Neovim installation failed, trying vim...")
                    vim_result = subprocess.run(
                        ["apt-get", "install", "-y", "vim"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    return vim_result.returncode == 0
                
                return True
                
            elif "alpine" in os_info:
                # Install in Alpine
                neovim_result = subprocess.run(
                    ["apk", "add", "--no-cache", "neovim"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # If neovim installation failed, try vim
                if neovim_result.returncode != 0:
                    logger.info("Neovim installation failed, trying vim...")
                    vim_result = subprocess.run(
                        ["apk", "add", "--no-cache", "vim"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    return vim_result.returncode == 0
                
                return True
            else:
                logger.error("Unsupported OS for automatic Vim/Neovim installation")
                return False
            
        except Exception as e:
            logger.error(f"Error installing Vim/Neovim: {e}")
            return False
    
    def _is_server_running(self) -> bool:
        """
        Check if the Neovim server is running by attempting to create a socket connection.
        
        Returns:
            bool: True if the server is running, False otherwise
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except:
            sock.close()
            return False
    
    def connect(self) -> bool:
        """
        Connect to the Neovim server.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not self._is_server_running():
            success = self.start_server()
            if not success:
                logger.error("Cannot connect to Neovim - server not running")
                return False
        
        try:
            self.nvim = pynvim.attach('tcp', address=self.host, port=self.port)
            self._is_connected = True
            logger.info(f"Connected to Neovim server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Neovim server: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Neovim server."""
        if self.nvim:
            try:
                self.nvim.close()
            except:
                pass
            self.nvim = None
            self._is_connected = False
    
    def stop_server(self) -> None:
        """Stop the Neovim server if it was started by this instance."""
        self.disconnect()
        
        if self._server_process is not None:
            try:
                self._server_process.terminate()
                self._server_process.wait(timeout=5)
            except:
                try:
                    self._server_process.kill()
                except:
                    pass
            self._server_process = None
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.disconnect()
        self.stop_server()
    
    def open_file(self, file_path: Union[str, Path]) -> bool:
        """
        Open a file in Neovim.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            bool: True if the file was opened successfully, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Record the current content of the file if it exists for change tracking
            if Path(file_path).exists():
                with open(file_path, 'r') as f:
                    self._original_content = f.read()
            else:
                self._original_content = ""
                
            self.nvim.command(f'edit {file_path}')
            return True
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    def _ensure_connected(self) -> bool:
        """
        Ensure that we're connected to the Neovim server.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self._is_connected or not self.nvim:
            return self.connect()
        return True
    
    def goto_line(self, line_number: int) -> bool:
        """
        Move the cursor to a specific line.
        
        Args:
            line_number: The line number to go to (1-indexed)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            self.nvim.command(f'{line_number}')
            return True
        except Exception as e:
            logger.error(f"Error going to line {line_number}: {e}")
            return False
    
    def search(self, pattern: str) -> bool:
        """
        Search for a pattern in the current buffer.
        
        Args:
            pattern: The pattern to search for
            
        Returns:
            bool: True if the pattern was found, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Execute search command and get cursor position to check if it changed
            current_pos = self.nvim.current.window.cursor
            self.nvim.command(f'/\\v{pattern}')
            new_pos = self.nvim.current.window.cursor
            
            # If position changed, search was successful
            return current_pos != new_pos
        except Exception as e:
            logger.error(f"Error searching for '{pattern}': {e}")
            return False
    
    def insert_text(self, text: str) -> bool:
        """
        Insert text at the current cursor position.
        
        Args:
            text: Text to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Enter insert mode, insert text, return to normal mode
            self.nvim.input('i' + text + '\x1b')  # \x1b is Escape key
            return True
        except Exception as e:
            logger.error(f"Error inserting text: {e}")
            return False
    
    def replace_line(self, line_number: int, new_text: str) -> bool:
        """
        Replace a single line with new text.
        
        Args:
            line_number: Line number to replace (1-indexed)
            new_text: New text for the line
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Convert from 1-indexed to 0-indexed for the buffer API
            buffer_line = line_number - 1
            self.nvim.current.buffer[buffer_line] = new_text
            return True
        except Exception as e:
            logger.error(f"Error replacing line {line_number}: {e}")
            return False
    
    def replace_range(self, start_line: int, end_line: int, new_text: List[str]) -> bool:
        """
        Replace a range of lines with new text.
        
        Args:
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            new_text: List of strings for the new lines
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Convert from 1-indexed to 0-indexed for the buffer API
            buffer_start = start_line - 1
            buffer_end = end_line
            self.nvim.current.buffer[buffer_start:buffer_end] = new_text
            return True
        except Exception as e:
            logger.error(f"Error replacing range {start_line}-{end_line}: {e}")
            return False
    
    def save_file(self) -> bool:
        """
        Save the current file and record the changes for display in the chat window.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._ensure_connected():
            return False
        
        try:
            # Get the current file path
            file_path = self.nvim.current.buffer.name
            
            # Save the file
            self.nvim.command('write')
            
            # Record the change for display in the chat window
            if hasattr(self, '_original_content'):
                with open(file_path, 'r') as f:
                    new_content = f.read()
                
                # Record the changes
                if new_content != self._original_content:
                    self.changes_record.append({
                        'file': file_path,
                        'original': self._original_content,
                        'new': new_content
                    })
            
            return True
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False
    
    def execute_command(self, command: str) -> Optional[str]:
        """
        Execute a Vim command directly.
        
        Args:
            command: Vim command to execute
            
        Returns:
            Optional[str]: Command output if successful, None otherwise
        """
        if not self._ensure_connected():
            return None
        
        try:
            return self.nvim.command_output(command)
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return None
    
    def get_current_file_content(self) -> Optional[str]:
        """
        Get the content of the current file.
        
        Returns:
            Optional[str]: File content if successful, None otherwise
        """
        if not self._ensure_connected():
            return None
        
        try:
            content = self.nvim.current.buffer[:]
            return "\n".join(content)
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None
    
    def get_changes(self) -> List[Dict]:
        """
        Get the recorded changes to display in the chat window.
        
        Returns:
            List[Dict]: List of changes with file path, original content, and new content
        """
        return self.changes_record
    
    def format_changes_for_chat(self) -> str:
        """
        Format the recorded changes for display in the chat window.
        
        Returns:
            str: Formatted changes in a human-readable format
        """
        import difflib
        
        if not self.changes_record:
            return "No changes recorded."
        
        result = []
        for change in self.changes_record:
            file_path = change['file']
            original = change['original'].splitlines()
            new = change['new'].splitlines()
            
            diff = difflib.unified_diff(
                original, 
                new,
                fromfile=f'Original: {file_path}',
                tofile=f'Modified: {file_path}',
                lineterm=''
            )
            
            result.append('\n'.join(diff))
        
        return '\n\n'.join(result)


# Singleton instance of VimMicroAgent
_vim_agent = None

def get_vim_agent() -> VimMicroAgent:
    """
    Get the singleton instance of VimMicroAgent.
    
    Returns:
        VimMicroAgent: The singleton instance
    """
    global _vim_agent
    if _vim_agent is None:
        _vim_agent = VimMicroAgent()
    return _vim_agent 