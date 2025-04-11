# VIM + Graph Memory Microagent

## Overview

A specialized microagent that combines VIM's powerful editing capabilities with graph-based semantic code understanding to dramatically improve code editing efficiency in OpenHands.

## Current OpenHands Editing Limitations

1. **Disconnected operations** - Read, edit, test cycles require separate transactions
2. **Context loss** - No persistent state between operations
3. **Inefficient editing** - Full file rewrites for small changes
4. **No semantic understanding** - Edits based on line numbers rather than code structure
5. **Error-prone** - Easy to lose positioning when files change

## Solution Architecture

### Components

1. **Headless Neovim Server**

   - Runs in background as service
   - Provides RPC API for editing operations
   - Maintains persistent editor state

2. **Graph-based Code Representation**

   - Compressed semantic understanding of code
   - Maps relationships between files, functions, classes
   - Tracks dependencies and call hierarchies
   - Minimizes token usage while preserving context

3. **VIM Microagent**
   - Translates high-level edit requests into VIM commands
   - Uses semantic graph to target specific code elements
   - Provides immediate feedback on operations

### Workflow

```
           ┌─────────────────┐
           │ OpenHands Agent │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  VIM Microagent │◄───┐
           └────────┬────────┘    │
                    │             │
        ┌───────────┴──────────┐  │
        │                      │  │
        ▼                      ▼  │
┌──────────────┐      ┌─────────────────┐
│ Semantic     │      │ Headless        │
│ Graph        │─────►│ Neovim Server   │
└──────────────┘      └─────────┬───────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │ File System     │
                      └─────────────────┘
```

## Benefits

1. **Efficiency**

   - Surgical edits without reloading entire files
   - Automatic navigation to relevant code sections
   - Persistent positioning awareness

2. **Semantic Understanding**

   - Edit by code structure, not line numbers
   - Understand relationships between components
   - Target operations by function, class, or method

3. **Better Feedback Loop**

   - Immediate operation results
   - Maintain context through edit cycles
   - Faster iteration on code changes

4. **Reduced Token Usage**

   - Only load relevant code sections
   - Compress code representation with semantic graph
   - Minimize context needed between operations

5. **Advanced Editing Capabilities**
   - Text objects (e.g., "inside function", "around class")
   - Macros for repetitive edits
   - Block editing for multi-line changes

## Implementation Considerations

### Neovim Integration

```bash
# Start headless Neovim server
nvim --headless --listen 127.0.0.1:6666
```

Communication via RPC API:

```python
import pynvim
nvim = pynvim.attach('tcp', '127.0.0.1', 6666)
# Execute commands
nvim.command('normal! gg/function<CR>')
```

### Semantic Graph Format

Compact JSON representation with key mapping:

```json
{
  "km": {
    "key_map": "km",
    "files": "f",
    "functions": "fn",
    "classes": "c",
    "relationships": "r"
  },
  "f": [
    {
      "n": "main.py",
      "l": "python",
      "s": "Main file with entry point",
      "i": ["os", "module_a"]
    }
  ],
  "fn": [
    {
      "fn": "main.py",
      "n": "main_func",
      "p": [],
      "ca": ["func_b1", "func_a1"]
    }
  ],
  "r": [{ "sid": 0, "tid": 2, "rt": "imports" }]
}
```

### Command Translation Layer

Translates semantic operations to VIM commands:

- "Edit validation function in auth.py" → `:e auth.py` + `/def validate` + ...
- "Add parameter to process_data function" → Search for function + Position cursor + Insert mode + Edit

## Next Steps

1. Develop proof-of-concept integration with headless Neovim
2. Create semantic graph generator for Python codebase
3. Build command translation layer for common operations
4. Integrate with OpenHands microagent architecture
5. Develop testing framework to measure editing efficiency
