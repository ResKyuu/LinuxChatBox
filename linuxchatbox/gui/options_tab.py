"""Options tab widget for configuring display format."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QGroupBox,
)
from PyQt6.QtCore import Qt

from ..core.display_options import TIME_FORMATS
from ..core.osc import build_osc_message


def _opt_label(text):
    """Create a styled option label."""
    lbl = QLabel(text)
    lbl.setObjectName("optLabel")
    return lbl


class OptionsTab(QWidget):
    """Options tab for configuring message format and display options."""
    
    def __init__(self, opts, on_options_changed, parent=None):
        super().__init__(parent)
        self._opts = opts
        self._on_options_changed = on_options_changed
        self._last_track = None
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        fmt_group = QGroupBox("Message Format")
        fg = QFormLayout(fmt_group)
        fg.setSpacing(8)
        fg.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.opt_prefix = QLineEdit(self._opts.prefix)
        self.opt_prefix.setPlaceholderText("e.g.  🎵  or  ♪  or  [Music]")
        self.opt_prefix.textChanged.connect(self._apply_options)
        fg.addRow(_opt_label("Prefix:"), self.opt_prefix)

        self.opt_separator = QLineEdit(self._opts.separator)
        self.opt_separator.setPlaceholderText("e.g.   -   or   |   or   by ")
        self.opt_separator.textChanged.connect(self._apply_options)
        fg.addRow(_opt_label("Title / Artist sep:"), self.opt_separator)

        self.opt_show_artist = QCheckBox("Show artist name")
        self.opt_show_artist.setChecked(self._opts.show_artist)
        self.opt_show_artist.checkStateChanged.connect(self._apply_options)
        fg.addRow("", self.opt_show_artist)

        self.opt_show_time = QCheckBox("Show playback time")
        self.opt_show_time.setChecked(self._opts.show_time)
        self.opt_show_time.checkStateChanged.connect(self._apply_options)
        fg.addRow("", self.opt_show_time)

        self.opt_show_volume = QCheckBox("Show volume level")
        self.opt_show_volume.setChecked(self._opts.show_volume)
        self.opt_show_volume.checkStateChanged.connect(self._apply_options)
        fg.addRow("", self.opt_show_volume)

        self.opt_volume_prefix = QLineEdit(self._opts.volume_prefix)
        self.opt_volume_prefix.setPlaceholderText("e.g.  🔊  or  Vol:")
        self.opt_volume_prefix.setEnabled(self._opts.show_volume)
        self.opt_volume_prefix.textChanged.connect(self._apply_options)
        fg.addRow(_opt_label("Volume prefix:"), self.opt_volume_prefix)

        self.opt_time_fmt = QComboBox()
        for key in TIME_FORMATS:
            self.opt_time_fmt.addItem(key)
        self.opt_time_fmt.setCurrentText(self._opts.time_format)
        self.opt_time_fmt.setEnabled(self._opts.show_time)
        self.opt_time_fmt.currentTextChanged.connect(self._apply_options)
        fg.addRow(_opt_label("Time format:"), self.opt_time_fmt)

        layout.addWidget(fmt_group)

        # Idle message group
        idle_group = QGroupBox("Idle Message (when nothing is playing)")
        ig = QFormLayout(idle_group)
        ig.setSpacing(8)
        ig.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.opt_idle_message = QLineEdit(self._opts.idle_message)
        self.opt_idle_message.setPlaceholderText("e.g.  ⏸ Looking for music...")
        self.opt_idle_message.textChanged.connect(self._apply_options)
        ig.addRow(_opt_label("Idle message:"), self.opt_idle_message)

        layout.addWidget(idle_group)

        live_group = QGroupBox("Live Preview")
        lg = QVBoxLayout(live_group)
        self.opt_preview = QLabel("—")
        self.opt_preview.setObjectName("optPreviewLabel")
        self.opt_preview.setWordWrap(True)
        lg.addWidget(self.opt_preview)
        layout.addWidget(live_group)

        layout.addStretch()
        
    def _apply_options(self, *_):
        """Apply option changes and trigger callback."""
        self._opts.prefix       = self.opt_prefix.text()
        self._opts.separator    = self.opt_separator.text()
        self._opts.show_artist  = self.opt_show_artist.isChecked()
        self._opts.show_time    = self.opt_show_time.isChecked()
        self._opts.time_format  = self.opt_time_fmt.currentText()
        self._opts.idle_message = self.opt_idle_message.text()
        self._opts.show_volume  = self.opt_show_volume.isChecked()
        self._opts.volume_prefix = self.opt_volume_prefix.text()
        self.opt_time_fmt.setEnabled(self._opts.show_time)
        self.opt_volume_prefix.setEnabled(self._opts.show_volume)
        
        # Trigger callback to save config
        if self._on_options_changed:
            self._on_options_changed()
            
        self._update_preview()

    def _update_preview(self):
        """Update the live preview with current options."""
        if self._last_track:
            self.opt_preview.setText(build_osc_message(self._last_track, self._opts))
        else:
            dummy = {
                "title": "Track Title", "artist": "Artist Name",
                "position_us": 183_000_000, "length_us": 252_000_000,
                "volume": 75,
            }
            self.opt_preview.setText(build_osc_message(dummy, self._opts))
            
    def set_last_track(self, track):
        """Update the last track for preview."""
        self._last_track = track
        self._update_preview()
