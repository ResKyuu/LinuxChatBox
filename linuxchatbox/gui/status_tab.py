"""Status tab widget for custom status messages."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QGroupBox, QSpinBox,
)
from PyQt6.QtCore import Qt


def _opt_label(text):
    """Create a styled option label."""
    lbl = QLabel(text)
    lbl.setObjectName("optLabel")
    return lbl


class StatusTab(QWidget):
    """Status tab for configuring custom status messages with rotation."""
    
    def __init__(self, custom_statuses, custom_statuses_enabled, rotation_interval, on_status_changed, parent=None):
        super().__init__(parent)
        self._custom_statuses = custom_statuses  # List of 5 statuses
        self._custom_statuses_enabled = custom_statuses_enabled  # List of 5 bools
        self._rotation_interval = rotation_interval  # Seconds between rotations
        self._on_status_changed = on_status_changed
        self._status_inputs = []
        self._status_checkboxes = []
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Rotation settings group
        rotation_group = QGroupBox("Rotation Settings")
        rg = QFormLayout(rotation_group)
        rg.setSpacing(8)
        rg.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.rotation_interval_spin = QSpinBox()
        self.rotation_interval_spin.setRange(5, 300)
        self.rotation_interval_spin.setValue(self._rotation_interval)
        self.rotation_interval_spin.setSuffix(" seconds")
        self.rotation_interval_spin.valueChanged.connect(self._apply_status)
        rg.addRow(_opt_label("Rotation interval:"), self.rotation_interval_spin)
        
        rotation_info = QLabel("If 2+ statuses are enabled, they will rotate at this interval")
        rotation_info.setStyleSheet("color: #666666; font-size: 11px;")
        rotation_info.setWordWrap(True)
        rg.addRow("", rotation_info)
        
        layout.addWidget(rotation_group)

        # Custom statuses group
        status_group = QGroupBox("Custom Status Messages (up to 5)")
        sg = QVBoxLayout(status_group)
        sg.setSpacing(12)

        for i in range(5):
            status_row = QHBoxLayout()
            status_row.setSpacing(8)
            
            # Checkbox to enable this status
            checkbox = QCheckBox(f"#{i+1}")
            checkbox.setChecked(self._custom_statuses_enabled[i])
            checkbox.setFixedWidth(50)
            checkbox.checkStateChanged.connect(self._apply_status)
            self._status_checkboxes.append(checkbox)
            status_row.addWidget(checkbox)
            
            # Text input for status
            status_input = QLineEdit(self._custom_statuses[i])
            status_input.setPlaceholderText(f"e.g.  🎮 Gaming  or  ✨ Vibing  or  💤 AFK")
            status_input.textChanged.connect(self._apply_status)
            self._status_inputs.append(status_input)
            status_row.addWidget(status_input)
            
            sg.addLayout(status_row)

        layout.addWidget(status_group)

        info_group = QGroupBox("Information")
        ig = QVBoxLayout(info_group)
        info_text = QLabel(
            "Your custom status will appear <b>above</b> the playback message in VRChat.\n\n"
            "• Enable 1 status: Shows that status\n"
            "• Enable 2+ statuses: Rotates through them at the set interval\n"
            "• Enable 0 statuses: Only playback info is shown"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #999999; font-size: 12px;")
        ig.addWidget(info_text)
        layout.addWidget(info_group)

        preview_group = QGroupBox("Preview")
        pg = QVBoxLayout(preview_group)
        self.preview_label = QLabel("—")
        self.preview_label.setObjectName("optPreviewLabel")
        self.preview_label.setWordWrap(True)
        pg.addWidget(self.preview_label)
        layout.addWidget(preview_group)

        layout.addStretch()
        
        # Initial preview update
        self._update_preview()
        
    def _apply_status(self):
        """Apply status changes and trigger callback."""
        # Collect all statuses and enabled states
        for i in range(5):
            self._custom_statuses[i] = self._status_inputs[i].text()
            self._custom_statuses_enabled[i] = self._status_checkboxes[i].isChecked()
        
        self._rotation_interval = self.rotation_interval_spin.value()
        
        # Update preview
        self._update_preview()
        
        # Notify parent
        if self._on_status_changed:
            self._on_status_changed()
    
    def _update_preview(self):
        """Update the preview label."""
        enabled_statuses = [
            self._custom_statuses[i] 
            for i in range(5) 
            if self._custom_statuses_enabled[i] and self._custom_statuses[i].strip()
        ]
        
        if not enabled_statuses:
            preview = "🎵 Song Title - Artist Name\n0:45 / 3:21"
        elif len(enabled_statuses) == 1:
            preview = f"{enabled_statuses[0]}\n🎵 Song Title - Artist Name\n0:45 / 3:21"
        else:
            # Show rotation preview
            preview = "Rotating:\n"
            for i, status in enumerate(enabled_statuses, 1):
                preview += f"  {i}. {status}\n"
            preview += f"\n(Every {self._rotation_interval}s)\n\n"
            preview += f"{enabled_statuses[0]}\n🎵 Song Title - Artist Name\n0:45 / 3:21"
        
        self.preview_label.setText(preview)
    
    def get_custom_statuses(self):
        """Get the list of custom statuses."""
        return [self._status_inputs[i].text() for i in range(5)]
    
    def get_custom_statuses_enabled(self):
        """Get the list of enabled flags."""
        return [self._status_checkboxes[i].isChecked() for i in range(5)]
    
    def get_rotation_interval(self):
        """Get the rotation interval in seconds."""
        return self.rotation_interval_spin.value()
