"""
Command-line interface for the VIM microagent.

This module provides a simple command-line interface to interact with the VIM microagent
and test its functionality in headless Docker environments.
"""

import argparse
import sys
from pathlib import Path

from openhands.core.logger import openhands_logger as logger
from openhands.microagent.vim.vim_agent import get_vim_agent
from openhands.microagent.vim.operations import VimOperations


def main():
    """Main entry point for the VIM microagent CLI."""
    parser = argparse.ArgumentParser(description='VIM Microagent CLI (Headless)')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # server commands
    server_parser = subparsers.add_parser('server', help='Manage Neovim server')
    server_subparsers = server_parser.add_subparsers(dest='server_command', help='Server command')
    
    server_start = server_subparsers.add_parser('start', help='Start Neovim server')
    server_stop = server_subparsers.add_parser('stop', help='Stop Neovim server')
    server_status = server_subparsers.add_parser('status', help='Check Neovim server status')
    
    # file operations
    file_parser = subparsers.add_parser('file', help='File operations')
    file_subparsers = file_parser.add_subparsers(dest='file_command', help='File command')
    
    file_open = file_subparsers.add_parser('open', help='Open a file')
    file_open.add_argument('path', help='Path to the file')
    
    file_create = file_subparsers.add_parser('create', help='Create a new file')
    file_create.add_argument('path', help='Path to the file')
    file_create.add_argument('--content', '-c', help='Content for the file')
    file_create.add_argument('--content-file', '-f', help='File containing content for the new file')
    
    # edit operations
    edit_parser = subparsers.add_parser('edit', help='Edit operations')
    edit_subparsers = edit_parser.add_subparsers(dest='edit_command', help='Edit command')
    
    edit_function = edit_subparsers.add_parser('function', help='Edit a function')
    edit_function.add_argument('file', help='Path to the file')
    edit_function.add_argument('function', help='Name of the function')
    edit_function.add_argument('--content', '-c', help='New content for the function')
    edit_function.add_argument('--content-file', '-f', help='File containing new content for the function')
    
    edit_class = edit_subparsers.add_parser('class', help='Edit a class')
    edit_class.add_argument('file', help='Path to the file')
    edit_class.add_argument('class_name', help='Name of the class')
    edit_class.add_argument('--method', '-m', help='Name of the method to edit')
    edit_class.add_argument('--content', '-c', help='New content for the method')
    edit_class.add_argument('--content-file', '-f', help='File containing new content for the method')
    
    edit_import = edit_subparsers.add_parser('import', help='Add an import statement')
    edit_import.add_argument('file', help='Path to the file')
    edit_import.add_argument('import_statement', help='Import statement to add')
    
    # get changes
    changes_parser = subparsers.add_parser('changes', help='Get recorded changes')
    changes_parser.add_argument('--format', choices=['diff', 'json'], default='diff', 
                              help='Output format for changes')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle server commands
    if args.command == 'server':
        return handle_server_command(args)
    
    # Handle file commands
    if args.command == 'file':
        return handle_file_command(args)
    
    # Handle edit commands
    if args.command == 'edit':
        return handle_edit_command(args)
    
    # Handle changes command
    if args.command == 'changes':
        return handle_changes_command(args)
    
    parser.print_help()
    return 1


def handle_server_command(args):
    """Handle server commands."""
    vim = get_vim_agent()
    
    if args.server_command == 'start':
        if vim.start_server():
            print("Neovim server started successfully")
            return 0
        else:
            print("Failed to start Neovim server")
            return 1
    
    elif args.server_command == 'stop':
        vim.stop_server()
        print("Neovim server stopped")
        return 0
    
    elif args.server_command == 'status':
        if vim._is_server_running():
            print("Neovim server is running")
        else:
            print("Neovim server is not running")
        return 0
    
    return 1


def handle_file_command(args):
    """Handle file commands."""
    vim = get_vim_agent()
    
    if args.file_command == 'open':
        if vim.open_file(args.path):
            print(f"Opened file: {args.path}")
            return 0
        else:
            print(f"Failed to open file: {args.path}")
            return 1
    
    elif args.file_command == 'create':
        content = ""
        if args.content:
            content = args.content
        elif args.content_file:
            try:
                with open(args.content_file, 'r') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading content file: {e}")
                return 1
        
        if VimOperations.create_file(args.path, content):
            print(f"Created file: {args.path}")
            
            # Display changes in the chat format
            print("\nChanges:")
            print(vim.format_changes_for_chat())
            return 0
        else:
            print(f"Failed to create file: {args.path}")
            return 1
    
    return 1


def handle_edit_command(args):
    """Handle edit commands."""
    vim = get_vim_agent()
    
    if args.edit_command == 'function':
        content = None
        if args.content:
            content = args.content
        elif args.content_file:
            try:
                with open(args.content_file, 'r') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading content file: {e}")
                return 1
        
        if VimOperations.edit_function(args.file, args.function, content):
            print(f"Edited function: {args.function} in {args.file}")
            
            # Display changes in the chat format
            print("\nChanges:")
            print(vim.format_changes_for_chat())
            return 0
        else:
            print(f"Failed to edit function: {args.function} in {args.file}")
            return 1
    
    elif args.edit_command == 'class':
        content = None
        if args.content:
            content = args.content
        elif args.content_file:
            try:
                with open(args.content_file, 'r') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading content file: {e}")
                return 1
        
        if VimOperations.edit_class(args.file, args.class_name, args.method, content):
            print(f"Edited class: {args.class_name} in {args.file}")
            
            # Display changes in the chat format
            print("\nChanges:")
            print(vim.format_changes_for_chat())
            return 0
        else:
            print(f"Failed to edit class: {args.class_name} in {args.file}")
            return 1
    
    elif args.edit_command == 'import':
        if VimOperations.add_import(args.file, args.import_statement):
            print(f"Added import: {args.import_statement} to {args.file}")
            
            # Display changes in the chat format
            print("\nChanges:")
            print(vim.format_changes_for_chat())
            return 0
        else:
            print(f"Failed to add import: {args.import_statement} to {args.file}")
            return 1
    
    return 1


def handle_changes_command(args):
    """Handle changes command."""
    vim = get_vim_agent()
    
    if args.format == 'diff':
        changes = vim.format_changes_for_chat()
        print(changes)
    else:  # json format
        import json
        changes = vim.get_changes()
        print(json.dumps(changes, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 