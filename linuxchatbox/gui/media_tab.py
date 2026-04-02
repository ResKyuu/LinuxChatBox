"""Media tab widget for displaying now playing info and controls."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider,
)
from PyQt6.QtCore import Qt

from ..core.display_options import _fmt
from ..core.volume import set_app_volume


class MediaTab(QWidget):
    """Media tab containing now playing info, controls, OSC toggle, and preview."""
    
    def __init__(self, opts, parent=None):
        super().__init__(parent)
        self._opts = opts
        self._active_service = None
        self._app_hint = None
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        media_group = QGroupBox("Now Playing (MPRIS)")
        mg = QVBoxLayout(media_group)
        mg.setSpacing(4)

        self.track_label = QLabel("— No media detected —")
        self.track_label.setObjectName("trackLabel")
        self.track_label.setWordWrap(True)
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mg.addWidget(self.track_label)

        self.artist_label = QLabel("")
        self.artist_label.setObjectName("artistLabel")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mg.addWidget(self.artist_label)

        self.time_label = QLabel("")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mg.addWidget(self.time_label)

        self.player_label = QLabel("")
        self.player_label.setObjectName("playerLabel")
        self.player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mg.addWidget(self.player_label)

        self.interval_label = QLabel("Poll interval: 2s")
        self.interval_label.setObjectName("intervalLabel")
        self.interval_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mg.addWidget(self.interval_label)

        # Media control buttons
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)
        ctrl_row.addStretch()

        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setObjectName("ctrlBtn")
        self.btn_prev.setToolTip("Previous")
        ctrl_row.addWidget(self.btn_prev)

        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("ctrlBtnPlay")
        self.btn_play.setToolTip("Play / Pause")
        ctrl_row.addWidget(self.btn_play)

        self.btn_next = QPushButton("⏭")
        self.btn_next.setObjectName("ctrlBtn")
        self.btn_next.setToolTip("Next")
        ctrl_row.addWidget(self.btn_next)

        ctrl_row.addStretch()
        mg.addLayout(ctrl_row)

        # Volume slider
        vol_row = QHBoxLayout()
        vol_row.setSpacing(8)
        vol_icon = QLabel("🔊")
        vol_icon.setObjectName("volIcon")
        vol_row.addWidget(vol_icon)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.setObjectName("volSlider")
        self.vol_slider.valueChanged.connect(self._on_volume_slider)
        vol_row.addWidget(self.vol_slider)
        self.vol_pct_label = QLabel("50%")
        self.vol_pct_label.setObjectName("volPctLabel")
        self.vol_pct_label.setMinimumWidth(36)
        vol_row.addWidget(self.vol_pct_label)
        mg.addLayout(vol_row)

        layout.addWidget(media_group)

        osc_group = QGroupBox("VRChat OSC")
        og = QVBoxLayout(osc_group)
        og.setSpacing(8)

        self.toggle_btn = QPushButton("▶  Start Sending")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setMinimumHeight(40)
        og.addWidget(self.toggle_btn)

        from PyQt6.QtWidgets import QSpinBox
        port_row = QHBoxLayout()
        port_lbl = QLabel("OSC Port:")
        port_lbl.setObjectName("portLabel")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(9000)
        self.port_spin.setMinimumHeight(32)
        port_row.addWidget(port_lbl)
        port_row.addWidget(self.port_spin)
        port_row.addStretch()
        og.addLayout(port_row)

        layout.addWidget(osc_group)

        prev_group = QGroupBox("Last Sent to Chatbox")
        pg = QVBoxLayout(prev_group)
        self.preview_label = QLabel("—")
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setWordWrap(True)
        pg.addWidget(self.preview_label)
        layout.addWidget(prev_group)

        layout.addStretch()
        
    def update_track_display(self, track):
        """Update the now playing display with track info."""
        self._active_service = track["service"]
        self._app_hint = str(track["service"]).replace("org.mpris.MediaPlayer2.", "")
        
        # Restore normal track label style
        self.track_label.setProperty("state", "")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)

        self.track_label.setText(track["title"])
        self.artist_label.setText(track["artist"])
        pos = _fmt(track["position_us"])
        dur = _fmt(track["length_us"])
        vol_suffix = f"  {self._opts.volume_prefix}{track['volume']}%" if self._opts.show_volume and track.get("volume") is not None else ""
        self.time_label.setText(f"{pos} / {dur}{vol_suffix}")
        
        if track.get("volume") is not None:
            self.vol_slider.blockSignals(True)
            self.vol_slider.setValue(int(track["volume"]))
            self.vol_pct_label.setText(f"{int(track['volume'])}%")
            self.vol_slider.blockSignals(False)
            
        svc = track["service"].replace("org.mpris.MediaPlayer2.", "")
        self.player_label.setText(f"\u25b6 via {svc}")
        
    def show_idle_state(self):
        """Display the idle message in the Now Playing area."""
        self.track_label.setText(self._opts.idle_message)
        self.track_label.setProperty("state", "idle")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)
        self.artist_label.setText("")
        self.time_label.setText("")
        self.player_label.setText("")

    def show_no_media_state(self):
        """Display the default inactive state when sending is OFF."""
        self.track_label.setText("— No media detected —")
        self.track_label.setProperty("state", "")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)
        self.artist_label.setText("")
        self.time_label.setText("")
        self.player_label.setText("")
        
    def _on_volume_slider(self, value):
        """Handle volume slider changes."""
        self.vol_pct_label.setText(f"{value}%")
        if self._app_hint:
            set_app_volume(
                self._app_hint,
                str(self._active_service) if self._active_service else None,
                value
            )
