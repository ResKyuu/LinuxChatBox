"""Discord tab for Rich Presence configuration."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt


class DiscordTab(QWidget):
    """Discord Rich Presence configuration tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        
    def _build_ui(self):
        """Build the Discord tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # ── Discord RPC Control Group ──
        rpc_group = QGroupBox("Discord Rich Presence")
        rpc_layout = QVBoxLayout(rpc_group)
        
        # Enable toggle
        toggle_layout = QHBoxLayout()
        self.enable_btn = QPushButton("▶ Enable Discord RPC")
        self.enable_btn.setObjectName("toggleBtn")
        self.enable_btn.setCheckable(True)
        self.enable_btn.setChecked(False)
        toggle_layout.addWidget(self.enable_btn)
        rpc_layout.addLayout(toggle_layout)
        
        # Status display
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setObjectName("optLabel")
        self.status_value = QLabel("Disconnected")
        self.status_value.setObjectName("trackLabel")
        self.status_value.setProperty("state", "idle")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value, 1)
        rpc_layout.addLayout(status_layout)
        
        layout.addWidget(rpc_group)
        
        # ── Current Presence Preview ──
        preview_group = QGroupBox("Discord Presence Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("Discord RPC disabled")
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_label.setMinimumHeight(80)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        # ── Info Section ──
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "Discord Rich Presence shows:\n"
            "• Currently focused application\n"
            "• Currently playing song from MPRIS\n\n"
            "Works completely independently!"
        )
        info_text.setObjectName("optLabel")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # Spacer
        layout.addStretch()
        
    def update_status(self, status_text):
        """Update the connection status display."""
        self.status_value.setText(status_text)
        if "Connected" in status_text:
            self.status_value.setProperty("state", "normal")
        else:
            self.status_value.setProperty("state", "idle")
        # Refresh style
        self.status_value.style().unpolish(self.status_value)
        self.status_value.style().polish(self.status_value)
        
    def update_preview(self, preview_text):
        """Update the Discord presence preview."""
        self.preview_label.setText(preview_text)
