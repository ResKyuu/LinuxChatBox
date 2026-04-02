#!/bin/bash
# LinuxChatbox Installation Script

set -e

echo "🎮 Installing LinuxChatbox..."

# Install Python package
echo "📦 Installing Python package..."
pip install -e . --user

# Install desktop file
echo "🖥️  Installing desktop integration..."
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp linuxchatbox/resources/linuxchatbox.desktop ~/.local/share/applications/
cp linuxchatbox/resources/icon.png ~/.local/share/icons/hicolor/256x256/apps/linuxchatbox.png
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ -f -t 2>/dev/null || true

# Verify installation
if command -v linuxchatbox &> /dev/null; then
    echo "✅ Installation complete!"
    echo ""
    echo "You can now:"
    echo "  • Launch from your application menu (search 'LinuxChatbox')"
    echo "  • Run 'linuxchatbox' from terminal"
    echo ""
    echo "The app runs standalone — no terminal window required!"
else
    echo "⚠️  Warning: 'linuxchatbox' command not found in PATH"
    echo "Add to your shell config (~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
