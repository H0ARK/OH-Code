# Docker Integration for VIM Microagent

This document explains how to properly integrate Vim/Neovim into the OpenHands Docker environment for the VIM microagent.

## Overview

The VIM microagent requires either Vim or Neovim to be installed in the sandbox runtime container. Instead of creating a separate build process, we should extend the existing Docker setup.

## Integration Options

### Option 1: Custom Runtime Image Extension (Recommended)

Create a custom runtime image extending the default one:

1. Create a `runtime-neovim` directory in the project's `containers` folder:

```bash
mkdir -p containers/runtime-neovim
```

2. Create a Dockerfile in this directory:

```bash
# In containers/runtime-neovim/Dockerfile
FROM docker.all-hands.dev/all-hands-ai/runtime:0.12-nikolaik

# Install Vim, Neovim and dependencies
RUN apt-get update && apt-get install -y \
    vim \
    neovim \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pynvim for Neovim Python integration
RUN pip3 install pynvim

# Set up configuration directory for Neovim
# Create the directory with global permissions - OpenHands will set proper ownership at runtime
RUN mkdir -p /home/openhands/.config/nvim && \
    chmod -R 777 /home/openhands/.config

# Basic init.vim configuration - create with global permissions
RUN echo 'set nocompatible\nset hidden\nset noswapfile\nset nobackup\nset nowritebackup' > /home/openhands/.config/nvim/init.vim && \
    chmod 666 /home/openhands/.config/nvim/init.vim

# Create symbolic link from nvim to vim (as backup)
RUN ln -sf /usr/bin/nvim /usr/local/bin/vim || true

# Label the image
LABEL description="OpenHands sandbox with Vim/Neovim for VIM microagent"
LABEL version="1.0"
LABEL maintainer="OpenHands Team"
```

> **Important Note**: We use `chmod` instead of `chown` because the `openhands` user doesn't exist during image build - it's created by OpenHands when the container runs. Setting global permissions allows OpenHands to adjust ownership at runtime.

3. Build the image:

```bash
docker build -t docker.all-hands.dev/all-hands-ai/runtime-neovim:0.12 -f containers/runtime-neovim/Dockerfile .
```

4. Use this image in your docker-compose.yml file by setting the `SANDBOX_RUNTIME_CONTAINER_IMAGE` environment variable:

```yaml
services:
  openhands:
    # ... existing configuration ...
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime-neovim:0.12
      # ... other environment variables ...
```

Or set it as an environment variable before running docker-compose:

```bash
export SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime-neovim:0.12
docker-compose up
```

### Option 2: Use docker-compose.override.yml

Create a docker-compose.override.yml file to override the runtime image:

```yaml
# docker-compose.override.yml
services:
  openhands:
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime-neovim:0.12
```

## Usage

When OpenHands runs, it will use the custom runtime image with Vim and Neovim pre-installed. The VIM microagent will automatically detect and use either Vim or Neovim without needing to install it at runtime.

## Testing

To verify that Vim or Neovim is available in your environment, you can run:

```bash
vim --version  # For traditional Vim
nvim --version  # For Neovim
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with the Neovim configuration, you may need to adjust the permissions in the running container:

```bash
# Get the container ID
docker ps | grep openhands

# Execute a shell in the container
docker exec -it CONTAINER_ID /bin/bash

# Fix permissions (inside the container)
chown -R openhands:openhands /home/openhands/.config
```

### Vim/Neovim Missing

If Vim/Neovim is not detected despite using the custom image:

1. Verify the runtime container is using the correct image:

   ```bash
   docker ps --format "{{.Image}} {{.Names}}" | grep openhands
   ```

2. Check if the binaries exist but aren't in the PATH:

   ```bash
   find / -name "vim" -o -name "nvim" 2>/dev/null
   ```

3. Try using the absolute path to Vim if found:
   ```bash
   /usr/bin/vim --version
   /usr/bin/nvim --version
   ```

## Fallback

The VIM microagent includes automatic fallback code that attempts to install Vim or Neovim if neither is present. It first tries to install Neovim, and if that fails, it attempts to install traditional Vim.
