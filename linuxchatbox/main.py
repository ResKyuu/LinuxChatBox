#!/usr/bin/env python3
"""
LinuxChatbox — Native Linux VRChat chatbox for MPRIS media players
Main entry point
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from .gui.mainwindow import LinuxChatbox


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("LinuxChatbox")
    app.setApplicationVersion("0.2.0")
    app.setDesktopFileName("linuxchatbox.desktop")
    
    # Set application icon
    icon_paths = [
        Path.home() / ".local/share/icons/hicolor/256x256/apps/linuxchatbox.png",
        Path(__file__).parent / "resources/icon.png",
    ]
    for icon_path in icon_paths:
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            break
    
    window = LinuxChatbox()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
