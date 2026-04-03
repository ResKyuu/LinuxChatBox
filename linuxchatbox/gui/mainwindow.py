"""Main application window for LinuxChatbox."""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QStatusBar, QTabWidget,
)
from PyQt6.QtGui import QIcon

from ..workers.media_worker import MediaWorker
from ..core.config import load_config, save_config
from ..core.mpris import send_mpris_command
from .media_tab import MediaTab
from .options_tab import OptionsTab


STYLESHEET = """
    QMainWindow, QWidget, QTabWidget, QTabBar {
        background-color: #000000;
        color: #cccccc;
        font-family: -apple-system, "Segoe UI", "Cantarell", sans-serif;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #1a1a1a;
        border-radius: 0;
        background-color: #000000;
    }
    QTabBar::tab {
        background-color: #000000;
        color: #666666;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 16px;
        margin-right: 0;
        font-size: 13px;
        font-weight: 500;
    }
    QTabBar::tab:selected {
        background-color: #000000;
        color: #a855f7;
        border-bottom: 2px solid #a855f7;
    }
    QTabBar::tab:hover:!selected {
        color: #999999;
    }
    QGroupBox {
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        margin-top: 6px;
        padding: 12px;
        color: #666666;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
    }
    #appTitle {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
    }
    #divider {
        background-color: #1a1a1a;
        max-height: 1px;
        min-height: 1px;
        border: none;
        color: #1a1a1a;
    }
    QFrame#divider {
        background-color: #1a1a1a;
        border: none;
        color: #1a1a1a;
    }
    #trackLabel {
        font-size: 15px;
        font-weight: 500;
        color: #ffffff;
        padding: 2px 0;
    }
    #trackLabel[state="idle"] {
        color: #666666;
        font-style: italic;
        font-weight: 400;
    }
    #artistLabel {
        font-size: 13px;
        color: #999999;
    }
    #timeLabel {
        font-size: 12px;
        color: #a855f7;
        font-family: "SF Mono", "Consolas", monospace;
    }
    #playerLabel {
        font-size: 11px;
        color: #555555;
    }
    #intervalLabel {
        font-size: 11px;
        color: #555555;
    }
    #toggleBtn {
        background-color: #a855f7;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 500;
        padding: 10px 16px;
    }
    #toggleBtn:hover {
        background-color: #9333ea;
    }
    #toggleBtn:checked {
        background-color: #1a1a1a;
        color: #a855f7;
    }
    #toggleBtn:checked:hover {
        background-color: #262626;
    }
    #portLabel, #optLabel {
        color: #999999;
        font-size: 13px;
    }
    QSpinBox, QLineEdit, QComboBox {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        padding: 6px 8px;
        color: #cccccc;
        selection-background-color: #a855f7;
        selection-color: #ffffff;
    }
    QSpinBox:hover, QLineEdit:hover, QComboBox:hover {
        border-color: #262626;
    }
    QSpinBox:focus, QLineEdit:focus, QComboBox:focus {
        border-color: #a855f7;
    }
    QComboBox::drop-down {
        border: none;
        width: 16px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #666666;
        width: 0;
        height: 0;
    }
    QComboBox QAbstractItemView {
        background-color: #0a0a0a;
        border: 1px solid #1a1a1a;
        selection-background-color: #a855f7;
        selection-color: #ffffff;
        color: #cccccc;
        outline: none;
    }
    QCheckBox {
        color: #cccccc;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #1a1a1a;
        border-radius: 3px;
        background-color: #0a0a0a;
    }
    QCheckBox::indicator:hover {
        border-color: #a855f7;
    }
    QCheckBox::indicator:checked {
        background-color: #a855f7;
        border-color: #a855f7;
    }
    #previewLabel, #optPreviewLabel {
        font-size: 12px;
        color: #999999;
        font-family: "SF Mono", "Consolas", monospace;
        padding: 4px;
    }
    QStatusBar {
        background-color: #000000;
        color: #666666;
        font-size: 11px;
        border-top: 1px solid #1a1a1a;
    }
    #volIcon {
        font-size: 14px;
        color: #666666;
    }
    #volPctLabel {
        font-size: 11px;
        color: #999999;
        font-family: "SF Mono", "Consolas", monospace;
    }
    QSlider#volSlider {
        height: 20px;
    }
    QSlider#volSlider::groove:horizontal {
        height: 4px;
        background: #1a1a1a;
        border-radius: 2px;
    }
    QSlider#volSlider::sub-page:horizontal {
        background: #a855f7;
        border-radius: 2px;
    }
    QSlider#volSlider::handle:horizontal {
        width: 12px;
        height: 12px;
        margin: -4px 0;
        background: #ffffff;
        border-radius: 6px;
    }
    #ctrlBtn, #ctrlBtnPlay {
        background-color: #0a0a0a;
        color: #cccccc;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        font-size: 14px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }
    #ctrlBtn:hover {
        background-color: #1a1a1a;
        border-color: #262626;
    }
    #ctrlBtn:disabled {
        color: #333333;
        border-color: #0a0a0a;
    }
    #ctrlBtnPlay {
        background-color: #a855f7;
        color: #ffffff;
        border: none;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
    }
    #ctrlBtnPlay:hover {
        background-color: #9333ea;
    }
    #ctrlBtnPlay:disabled {
        background-color: #1a1a1a;
        color: #333333;
    }
"""


class LinuxChatbox(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxChatbox")
        self.setMinimumSize(480, 770)
        self.resize(480, 780)

        self._opts, _loaded_port = load_config()
        self._loaded_port = _loaded_port
        self._last_track = None

        self._worker = MediaWorker(self._opts)
        self._worker.track_updated.connect(self._on_track_updated)
        self._worker.idle_triggered.connect(self._on_idle_triggered)
        self._worker.no_media.connect(self._on_no_media)
        self._worker.osc_sent.connect(self._on_osc_sent)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.interval_changed.connect(self._on_interval_changed)
        self._worker.start()

        self._build_ui()
        self.setStyleSheet(STYLESHEET)
        
        # Set window icon
        self._set_window_icon()
        
        # Restore persisted OSC port
        self.media_tab.port_spin.setValue(self._loaded_port)
        self._worker.set_osc_port(self._loaded_port)

    def _set_window_icon(self):
        """Set the window icon from the resources directory."""
        # Try multiple possible icon locations
        icon_paths = [
            # Installed location
            Path.home() / ".local/share/icons/hicolor/256x256/apps/linuxchatbox.png",
            # Package resources directory
            Path(__file__).parent.parent / "resources/icon.png",
            # Development directory
            Path(__file__).parent.parent.parent / "linuxchatbox/resources/icon.png",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        header = QHBoxLayout()
        title_lbl = QLabel("LinuxChatbox")
        title_lbl.setObjectName("appTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        root.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("divider")
        root.addWidget(sep)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.media_tab = MediaTab(self._opts)
        self.options_tab = OptionsTab(self._opts, self._on_options_changed)
        
        self.tabs.addTab(self.media_tab, "Media")
        self.tabs.addTab(self.options_tab, "Options")
        root.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready — waiting for media player", "neutral")
        
        # Connect media tab signals
        self.media_tab.toggle_btn.clicked.connect(self._on_toggle)
        self.media_tab.port_spin.valueChanged.connect(self._on_port_changed)
        self.media_tab.btn_prev.clicked.connect(lambda: self._cmd_mpris("Previous"))
        self.media_tab.btn_play.clicked.connect(lambda: self._cmd_mpris("PlayPause"))
        self.media_tab.btn_next.clicked.connect(lambda: self._cmd_mpris("Next"))

    def _on_track_updated(self, track):
        """Handle track update from worker."""
        self._last_track = track
        self.media_tab.update_track_display(track)
        self.options_tab.set_last_track(track)
        
        svc = track["service"].replace("org.mpris.MediaPlayer2.", "")
        self._set_status(f"Detected: {track['title']} [{svc}]", "ok")

    def _on_idle_triggered(self):
        """Sending is ON but player is paused."""
        self._set_status(f"Paused — sending idle message to VRChat", "neutral")

    def _on_no_media(self):
        """Sending is OFF and nothing is playing."""
        self._last_track = None
        self.media_tab.show_no_media_state()
        self.options_tab.set_last_track(None)
        self._set_status("No MPRIS player found", "neutral")

    def _on_osc_sent(self, msg):
        """Handle OSC message sent."""
        self.media_tab.preview_label.setText(msg)
        # Only show the green tick for actual track messages, not idle spam
        if msg != self._opts.idle_message:
            self._set_status("\u2713 OSC sent to VRChat", "ok")

    def _on_error(self, err):
        """Handle worker error."""
        self._set_status(f"\u26a0 {err}", "error")

    def _on_interval_changed(self, interval):
        """Handle poll interval change."""
        self.media_tab.interval_label.setText(f"Poll interval: {interval}s")

    def _on_toggle(self, checked):
        """Handle OSC toggle button."""
        self._worker.set_enabled(checked)
        if checked:
            self.media_tab.toggle_btn.setText("\u23f9  Stop Sending")
            self._set_status("Sending to VRChat enabled", "ok")
        else:
            self.media_tab.toggle_btn.setText("\u25b6  Start Sending")
            if self._last_track is None:
                self.media_tab.show_no_media_state()
            self._set_status("Sending to VRChat disabled", "neutral")

    def _on_port_changed(self, port):
        """Handle OSC port change."""
        self._worker.set_osc_port(port)
        save_config(self._opts, port)
        self._set_status(f"OSC port changed to {port}", "neutral")
        
    def _on_options_changed(self):
        """Handle options change from options tab."""
        save_config(self._opts, self.media_tab.port_spin.value())

    def _cmd_mpris(self, command):
        """Execute MPRIS command."""
        svc = str(self.media_tab._active_service) if self.media_tab._active_service else None
        if not svc:
            # No service detected yet — try playerctl as generic fallback
            cmd_map = {"PlayPause": "play-pause", "Next": "next", "Previous": "previous"}
            if os.system(f"playerctl {cmd_map.get(command, command.lower())}") != 0:
                self._set_status("No active player detected yet", "error")
            return
        send_mpris_command(svc, command)

    def _set_status(self, message, level="neutral"):
        """Set status bar message with color."""
        colors = {"ok": "#a855f7", "error": "#ef4444", "neutral": "#666666"}
        color = colors.get(level, colors["neutral"])
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #000000;
                color: {color};
                font-size: 11px;
                border-top: 1px solid #1a1a1a;
            }}
        """)
        self.status_bar.showMessage(message)

    def closeEvent(self, event):
        """Handle window close."""
        self._worker.stop()
        self._worker.wait(2000)
        super().closeEvent(event)
