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
        background-color: #1c1b19;
        color: #cdccca;
        font-family: "Inter", "Segoe UI", "Cantarell", sans-serif;
        font-size: 13px;
    }
    QTabWidget::pane {
        border: 1px solid #393836;
        border-radius: 8px;
        background-color: #1c1b19;
    }
    QTabBar::tab {
        background-color: #22211f;
        color: #797876;
        border: 1px solid #393836;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 6px 20px;
        margin-right: 3px;
        font-size: 12px;
        font-weight: 600;
    }
    QTabBar::tab:selected {
        background-color: #1c1b19;
        color: #cdccca;
        border-bottom-color: #1c1b19;
    }
    QTabBar::tab:hover:!selected {
        background-color: #2d2c2a;
        color: #cdccca;
    }
    QGroupBox {
        border: 1px solid #393836;
        border-radius: 8px;
        margin-top: 8px;
        padding: 12px 10px 10px 10px;
        color: #797876;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
    }
    #appTitle {
        font-size: 18px;
        font-weight: 700;
        color: #cdccca;
    }
    #divider {
        color: #393836;
        background-color: #393836;
        max-height: 1px;
        border: none;
    }
    #trackLabel {
        font-size: 15px;
        font-weight: 600;
        color: #e8e7e5;
        padding: 4px 0;
    }
    #trackLabel[state="idle"] {
        color: #797876;
        font-style: italic;
        font-weight: 400;
    }
    #artistLabel {
        font-size: 13px;
        color: #797876;
    }
    #timeLabel {
        font-size: 12px;
        color: #4f98a3;
        font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
        letter-spacing: 0.5px;
    }
    #playerLabel {
        font-size: 11px;
        color: #5a5957;
        font-style: italic;
    }
    #intervalLabel {
        font-size: 11px;
        color: #5a5957;
    }
    #toggleBtn {
        background-color: #01696f;
        color: #f9f8f5;
        border: none;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 20px;
    }
    #toggleBtn:hover         { background-color: #0c4e54; }
    #toggleBtn:checked       { background-color: #a12c7b; }
    #toggleBtn:checked:hover { background-color: #7d1e5e; }
    #portLabel, #optLabel {
        color: #797876;
        min-width: 130px;
    }
    QSpinBox, QLineEdit, QComboBox {
        background-color: #22211f;
        border: 1px solid #393836;
        border-radius: 5px;
        padding: 5px 8px;
        color: #cdccca;
        min-width: 90px;
    }
    QSpinBox:focus, QLineEdit:focus, QComboBox:focus {
        border-color: #4f98a3;
    }
    QComboBox::drop-down { border: none; padding-right: 8px; }
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #797876;
        width: 0; height: 0;
        margin-right: 6px;
    }
    QComboBox QAbstractItemView {
        background-color: #22211f;
        border: 1px solid #393836;
        selection-background-color: #2d2c2a;
        selection-color: #cdccca;
        color: #cdccca;
    }
    QCheckBox {
        color: #cdccca;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border: 1px solid #393836;
        border-radius: 4px;
        background-color: #22211f;
    }
    QCheckBox::indicator:checked  { background-color: #01696f; border-color: #01696f; }
    QCheckBox::indicator:hover    { border-color: #4f98a3; }
    #previewLabel, #optPreviewLabel {
        font-size: 12px;
        color: #797876;
        font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
        padding: 4px 2px;
        line-height: 1.6;
    }
    QStatusBar {
        background-color: #171614;
        color: #5a5957;
        font-size: 11px;
        border-top: 1px solid #262523;
    }
    #volIcon { font-size: 14px; color: #797876; }
    #volPctLabel { font-size: 11px; color: #797876; min-width: 36px; }
    QSlider#volSlider { height: 20px; }
    QSlider#volSlider::groove:horizontal {
        height: 4px;
        background: #393836;
        border-radius: 2px;
    }
    QSlider#volSlider::sub-page:horizontal {
        background: #4f98a3;
        border-radius: 2px;
    }
    QSlider#volSlider::handle:horizontal {
        width: 14px;
        height: 14px;
        margin: -5px 0;
        background: #cdccca;
        border-radius: 7px;
    }
    QSlider#volSlider::handle:horizontal:hover { background: #ffffff; }
    #ctrlBtn, #ctrlBtnPlay {
        background-color: #22211f;
        color: #cdccca;
        border: 1px solid #393836;
        border-radius: 8px;
        font-size: 15px;
        min-width: 40px;
        max-width: 40px;
        min-height: 36px;
        max-height: 36px;
        padding: 0;
    }
    #ctrlBtn:hover, #ctrlBtnPlay:hover { background-color: #2d2c2a; border-color: #4f98a3; }
    #ctrlBtn:pressed, #ctrlBtnPlay:pressed { background-color: #393836; }
    #ctrlBtn:disabled, #ctrlBtnPlay:disabled { color: #3a3937; border-color: #2a2927; }
    #ctrlBtnPlay {
        background-color: #01696f;
        color: #f9f8f5;
        border-color: #01696f;
    }
    #ctrlBtnPlay:hover   { background-color: #0c4e54; border-color: #0c4e54; }
    #ctrlBtnPlay:pressed { background-color: #0f3638; }
    #ctrlBtnPlay:disabled { background-color: #1e2e2e; border-color: #1e2e2e; color: #3a5555; }
"""


class LinuxChatbox(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinuxChatbox")
        self.setMinimumWidth(480)
        self.setMinimumHeight(440)

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
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        title_lbl = QLabel("🎮 LinuxChatbox")
        title_lbl.setObjectName("appTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        root.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("divider")
        root.addWidget(sep)

        self.tabs = QTabWidget()
        self.media_tab = MediaTab(self._opts)
        self.options_tab = OptionsTab(self._opts, self._on_options_changed)
        
        self.tabs.addTab(self.media_tab, "  Media  ")
        self.tabs.addTab(self.options_tab, "  Options  ")
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
        colors = {"ok": "#6daa45", "error": "#dd6974", "neutral": "#5a5957"}
        color = colors.get(level, colors["neutral"])
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #171614;
                color: {color};
                font-size: 11px;
                border-top: 1px solid #262523;
            }}
        """)
        self.status_bar.showMessage(message)

    def closeEvent(self, event):
        """Handle window close."""
        self._worker.stop()
        self._worker.wait(2000)
        super().closeEvent(event)
