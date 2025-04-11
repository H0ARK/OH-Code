"""
High-level VIM operations for the OpenHands VIM microagent.

This module provides higher-level editing operations that build on top of the
basic VIM commands provided by the VimMicroAgent class. These operations are
designed to be used with semantic code understanding to enable more efficient
editing workflows.
"""

from typing import List, Optional, Tuple, Union
from pathlib import Path

from openhands.core.logger import openhands_logger as logger
from openhands.microagent.vim.vim_agent import get_vim_agent


class VimOperations:
    """
    High-level VIM operations for efficient code editing.
    
    This class provides semantic operations that build on top of the
    basic VIM commands provided by the VimMicroAgent class.
    """
    
    @staticmethod
    def edit_function(file_path: Union[str, Path], function_name: str, new_content: Optional[str] = None) -> bool:
        """
        Navigate to a function in a file and optionally replace its content.
        
        Args:
            file_path: Path to the file containing the function
            function_name: Name of the function to edit
            new_content: Optional new content for the function
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        vim = get_vim_agent()
        
        # Open the file
        if not vim.open_file(file_path):
            return False
        
        # Search for the function definition
        if not vim.search(f"(def|function|func)\\s+{function_name}\\b"):
            logger.error(f"Function {function_name} not found in {file_path}")
            return False
        
        # If we just want to navigate to the function, we're done
        if new_content is None:
            return True
        
        # TODO: This is where we would use semantic graph understanding to
        # determine the start and end lines of the function. For now, we'll
        # just use a simple approach that works for Python functions.
        
        # Get the current line number (function definition line)
        function_line = vim.execute_command('echo line(".")')
        if not function_line:
            return False
        
        function_line = int(function_line.strip())
        
        # Find the indentation level of the function definition
        content = vim.get_current_file_content()
        if not content:
            return False
        
        lines = content.split('\n')
        if function_line > len(lines):
            return False
        
        function_def_line = lines[function_line - 1]  # Convert to 0-indexed
        indentation = len(function_def_line) - len(function_def_line.lstrip())
        
        # Find the end of the function by looking for a line with the same or less indentation
        end_line = function_line
        for i in range(function_line, len(lines)):
            # Skip empty lines
            if not lines[i].strip():
                end_line = i + 1
                continue
                
            line_indentation = len(lines[i]) - len(lines[i].lstrip())
            if line_indentation <= indentation:
                end_line = i
                break
            end_line = i + 1
        
        # Replace the function content
        new_lines = new_content.split('\n')
        
        # Keep the function definition line
        # new_lines.insert(0, function_def_line)
        
        return vim.replace_range(function_line, end_line, new_lines)
    
    @staticmethod
    def add_import(file_path: Union[str, Path], import_statement: str) -> bool:
        """
        Add an import statement to a file if it doesn't already exist.
        
        Args:
            file_path: Path to the file to add the import to
            import_statement: Import statement to add
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        vim = get_vim_agent()
        
        # Open the file
        if not vim.open_file(file_path):
            return False
        
        # Check if the import already exists
        content = vim.get_current_file_content()
        if not content:
            return False
        
        if import_statement in content:
            logger.info(f"Import {import_statement} already exists in {file_path}")
            return True
        
        # Find where to add the import
        # For now, we'll simply add it after the last import
        lines = content.split('\n')
        
        # Find the last import line
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                last_import_line = i + 1  # Convert to 1-indexed
        
        # If no imports found, add at the beginning of the file
        if last_import_line == 0:
            last_import_line = 1
        
        # Go to the line where we want to add the import
        if not vim.goto_line(last_import_line):
            return False
        
        # Add the import on a new line
        vim.insert_text(import_statement + '\n')
        
        # Save the file
        return vim.save_file()
    
    @staticmethod
    def insert_after_pattern(file_path: Union[str, Path], pattern: str, new_content: str) -> bool:
        """
        Insert content after a pattern match in a file.
        
        Args:
            file_path: Path to the file to edit
            pattern: Pattern to search for
            new_content: Content to insert after the pattern
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        vim = get_vim_agent()
        
        # Open the file
        if not vim.open_file(file_path):
            return False
        
        # Search for the pattern
        if not vim.search(pattern):
            logger.error(f"Pattern '{pattern}' not found in {file_path}")
            return False
        
        # Move to the end of the line
        vim.execute_command('normal! $')
        
        # Insert the new content
        if not vim.insert_text('\n' + new_content):
            return False
        
        # Save the file
        return vim.save_file()
    
    @staticmethod
    def edit_class(file_path: Union[str, Path], class_name: str, method_name: Optional[str] = None, new_method_content: Optional[str] = None) -> bool:
        """
        Navigate to a class and optionally to a method within that class.
        
        Args:
            file_path: Path to the file containing the class
            class_name: Name of the class to edit
            method_name: Optional name of a method to edit within the class
            new_method_content: Optional new content for the method
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        vim = get_vim_agent()
        
        # Open the file
        if not vim.open_file(file_path):
            return False
        
        # Search for the class definition
        if not vim.search(f"(class)\\s+{class_name}\\b"):
            logger.error(f"Class {class_name} not found in {file_path}")
            return False
        
        # If we don't need to edit a method, we're done
        if method_name is None:
            return True
        
        # Move to the beginning of the class body
        vim.execute_command('normal! j0')
        
        # Search for the method within the class
        # TODO: This should be enhanced with semantic understanding to properly scope the search
        if not vim.search(f"(def)\\s+{method_name}\\b"):
            logger.error(f"Method {method_name} not found in class {class_name}")
            return False
        
        # If we just want to navigate to the method, we're done
        if new_method_content is None:
            return True
        
        # Replace the method using a similar approach to edit_function
        # This is a simplification that works for Python classes
        function_line = vim.execute_command('echo line(".")')
        if not function_line:
            return False
        
        function_line = int(function_line.strip())
        
        content = vim.get_current_file_content()
        if not content:
            return False
        
        lines = content.split('\n')
        function_def_line = lines[function_line - 1]  # Convert to 0-indexed
        indentation = len(function_def_line) - len(function_def_line.lstrip())
        
        # Find the end of the method
        end_line = function_line
        for i in range(function_line, len(lines)):
            if not lines[i].strip():
                end_line = i + 1
                continue
                
            line_indentation = len(lines[i]) - len(lines[i].lstrip())
            if line_indentation <= indentation:
                end_line = i
                break
            end_line = i + 1
        
        # Replace the method content
        new_lines = new_method_content.split('\n')
        return vim.replace_range(function_line, end_line, new_lines)
    
    @staticmethod
    def create_file(file_path: Union[str, Path], content: str) -> bool:
        """
        Create a new file with the specified content.
        
        Args:
            file_path: Path to the file to create
            content: Content for the new file
            
        Returns:
            bool: True if operation was successful, False otherwise
        """
        vim = get_vim_agent()
        
        # Create a new buffer for the file
        vim.execute_command(f'enew')
        
        # Set the buffer contents
        lines = content.split('\n')
        if not vim.replace_range(1, 1, lines):
            return False
        
        # Save the buffer to the specified file
        vim.execute_command(f'write {file_path}')
        
        return True 