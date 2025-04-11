# Custom runtime container with Neovim for VIM microagent
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