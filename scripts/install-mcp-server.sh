#!/bin/bash
set -e

# Create target directory for test binaries
mkdir -p target/test-binaries

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Map architecture names
case $ARCH in
    x86_64|amd64)
        ARCH="x86_64"
        ;;
    aarch64|arm64)
        ARCH="aarch64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Set binary name based on platform
if [ "$OS" = "linux" ]; then
    BINARY_NAME="goldentooth-mcp-${ARCH}-linux"
elif [ "$OS" = "darwin" ]; then
    BINARY_NAME="goldentooth-mcp-${ARCH}-darwin"
else
    echo "Unsupported OS: $OS"
    echo "Supported platforms: Linux (x86_64, aarch64), macOS (x86_64, aarch64)"
    exit 1
fi

# Download the binary
echo "Downloading $BINARY_NAME..."
curl -L -o target/test-binaries/goldentooth-mcp \
    "https://github.com/goldentooth/mcp-server/releases/latest/download/$BINARY_NAME"

# Make it executable
chmod +x target/test-binaries/goldentooth-mcp

echo "MCP server installed successfully at target/test-binaries/goldentooth-mcp"

# Verify it works
./target/test-binaries/goldentooth-mcp --version || echo "Binary installed (version check not available)"
