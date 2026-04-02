#!/usr/bin/env python3
"""
LinuxChatbox — Native Linux VRChat chatbox for MPRIS media players
Main entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from .gui.mainwindow import LinuxChatbox


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("LinuxChatbox")
    app.setApplicationVersion("0.2.0")
    window = LinuxChatbox()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
