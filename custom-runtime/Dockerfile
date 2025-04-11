# Use the official OpenHands runtime as the base image
FROM docker.all-hands.dev/all-hands-ai/runtime:0.12-nikolaik

# Install Neovim and Vim
RUN apt-get update && apt-get install -y \
    neovim \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 