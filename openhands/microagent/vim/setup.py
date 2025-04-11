"""
Setup script for the VIM microagent.

This file registers the CLI entry point for the VIM microagent.
"""

from setuptools import setup

setup(
    name="openhands-vim-microagent",
    version="0.1.0",
    description="VIM microagent for OpenHands",
    author="OpenHands Team",
    entry_points={
        "console_scripts": [
            "openhands-vim=openhands.microagent.vim.cli:main",
        ],
    },
    install_requires=[
        "pynvim>=0.4.3",
    ],
) 