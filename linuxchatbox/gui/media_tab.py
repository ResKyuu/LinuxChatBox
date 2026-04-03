"""Media tab widget for displaying now playing info and controls."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from pathlib import Path
import urllib.request
import urllib.parse

from ..core.display_options import _fmt
from ..core.volume import set_app_volume
from ..core.mpris import set_mpris_position


class ArtworkLoader(QThread):
    """Background thread for loading album artwork."""
    artwork_loaded = pyqtSignal(QPixmap)
    
    def __init__(self, art_url, parent=None):
        super().__init__(parent)
        self.art_url = art_url
        
    def run(self):
        try:
            if not self.art_url:
                return
                
            # Handle file:// URLs
            if self.art_url.startswith("file://"):
                file_path = urllib.parse.unquote(self.art_url[7:])
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.artwork_loaded.emit(pixmap)
            # Handle HTTP/HTTPS URLs
            elif self.art_url.startswith("http://") or self.art_url.startswith("https://"):
                data = urllib.request.urlopen(self.art_url, timeout=3).read()
                pixmap = QPixmap()
                if pixmap.loadFromData(data):
                    self.artwork_loaded.emit(pixmap)
        except Exception:
            pass  # Silently fail - artwork is optional


class MediaTab(QWidget):
    """Media tab containing now playing info, controls, OSC toggle, and preview."""
    
    def __init__(self, opts, parent=None):
        super().__init__(parent)
        self._opts = opts
        self._active_service = None
        self._app_hint = None
        self._artwork_loader = None
        self._updating_position = False  # Flag to prevent feedback loop
        self._current_length_us = 0  # Store current track length
        self._current_art_url = ""  # Store current artwork URL to prevent reloading
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        media_group = QGroupBox("Now Playing (MPRIS)")
        mg = QVBoxLayout(media_group)
        mg.setSpacing(4)

        # Album artwork
        self.artwork_label = QLabel()
        self.artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork_label.setFixedSize(160, 160)
        self.artwork_label.setStyleSheet("""
            QLabel {
                background-color: #0a0a0a;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
            }
        """)
        self.artwork_label.hide()  # Hidden by default
        mg.addWidget(self.artwork_label, 0, Qt.AlignmentFlag.AlignCenter)

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

        # Position slider (seek bar) with time labels
        pos_row = QHBoxLayout()
        pos_row.setSpacing(6)
        
        self.pos_time_label = QLabel("0:00")
        self.pos_time_label.setObjectName("timeLabel")
        self.pos_time_label.setFixedWidth(45)
        pos_row.addWidget(self.pos_time_label)
        
        self.pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.pos_slider.setRange(0, 100)
        self.pos_slider.setValue(0)
        self.pos_slider.setObjectName("volSlider")
        self.pos_slider.sliderReleased.connect(self._on_position_slider)
        pos_row.addWidget(self.pos_slider)
        
        self.pos_duration_label = QLabel("0:00")
        self.pos_duration_label.setObjectName("timeLabel")
        self.pos_duration_label.setFixedWidth(45)
        self.pos_duration_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        pos_row.addWidget(self.pos_duration_label)
        
        mg.addLayout(pos_row)

        # Volume slider below position slider
        vol_row = QHBoxLayout()
        vol_row.setSpacing(6)
        
        vol_icon = QLabel("🔊")
        vol_icon.setObjectName("volIcon")
        vol_icon.setFixedWidth(16)
        vol_row.addWidget(vol_icon)
        
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.setObjectName("volSlider")
        self.vol_slider.valueChanged.connect(self._on_volume_slider)
        vol_row.addWidget(self.vol_slider)
        
        self.vol_pct_label = QLabel("50%")
        self.vol_pct_label.setObjectName("volPctLabel")
        self.vol_pct_label.setFixedWidth(30)
        vol_row.addWidget(self.vol_pct_label)
        
        mg.addLayout(vol_row)

        layout.addWidget(media_group)

        osc_group = QGroupBox("VRChat OSC")
        og = QVBoxLayout(osc_group)
        og.setSpacing(8)

        self.toggle_btn = QPushButton("▶  Start Sending")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setCheckable(True)
        og.addWidget(self.toggle_btn)

        from PyQt6.QtWidgets import QSpinBox
        port_row = QHBoxLayout()
        port_lbl = QLabel("OSC Port:")
        port_lbl.setObjectName("portLabel")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(9000)
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
        self._current_length_us = track["length_us"]
        
        # Restore normal track label style
        self.track_label.setProperty("state", "")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)

        self.track_label.setText(track["title"])
        self.artist_label.setText(track["artist"])
        pos = _fmt(track["position_us"])
        dur = _fmt(track["length_us"])
        self.time_label.setText(f"{pos} / {dur}")
        
        # Update position slider and time labels
        if track["length_us"] > 0 and not self.pos_slider.isSliderDown():
            self._updating_position = True
            progress = int((track["position_us"] / track["length_us"]) * 100)
            self.pos_slider.setValue(progress)
            self._updating_position = False
            
            # Update time labels
            self.pos_time_label.setText(_fmt(track["position_us"]))
            self.pos_duration_label.setText(_fmt(track["length_us"]))
        
        if track.get("volume") is not None:
            self.vol_slider.blockSignals(True)
            self.vol_slider.setValue(int(track["volume"]))
            self.vol_pct_label.setText(f"{int(track['volume'])}%")
            self.vol_slider.blockSignals(False)
            
        svc = track["service"].replace("org.mpris.MediaPlayer2.", "")
        self.player_label.setText(f"\u25b6 via {svc}")
        
        # Load album artwork (only if URL changed to prevent flickering)
        art_url = track.get("art_url", "")
        if art_url and art_url != self._current_art_url:
            self._current_art_url = art_url
            self._load_artwork(art_url)
        elif art_url:
            # URL is the same, keep showing current artwork
            pass
        else:
            # No artwork URL
            self._current_art_url = ""
            self.artwork_label.hide()
            
    def _load_artwork(self, art_url):
        """Load album artwork in background thread."""
        # Cancel any existing loader
        if self._artwork_loader and self._artwork_loader.isRunning():
            self._artwork_loader.quit()
            self._artwork_loader.wait()
        
        self._artwork_loader = ArtworkLoader(art_url)
        self._artwork_loader.artwork_loaded.connect(self._display_artwork)
        self._artwork_loader.start()
        
    def _display_artwork(self, pixmap):
        """Display the loaded artwork."""
        if not pixmap.isNull():
            # Scale pixmap to fit label while maintaining aspect ratio
            scaled = pixmap.scaled(
                160, 160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.artwork_label.setPixmap(scaled)
            self.artwork_label.show()
        else:
            self.artwork_label.hide()
        
    def show_idle_state(self):
        """Display the idle message in the Now Playing area."""
        self.track_label.setText(self._opts.idle_message)
        self.track_label.setProperty("state", "idle")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)
        self.artist_label.setText("")
        self.time_label.setText("")
        self.player_label.setText("")
        self.artwork_label.hide()
        self._current_art_url = ""
        self.pos_slider.setValue(0)
        self.pos_time_label.setText("0:00")
        self.pos_duration_label.setText("0:00")

    def show_no_media_state(self):
        """Display the default inactive state when sending is OFF."""
        self.track_label.setText("— No media detected —")
        self.track_label.setProperty("state", "")
        self.track_label.style().unpolish(self.track_label)
        self.track_label.style().polish(self.track_label)
        self.artist_label.setText("")
        self.time_label.setText("")
        self.player_label.setText("")
        self.artwork_label.hide()
        self._current_art_url = ""
        self.pos_slider.setValue(0)
        self.pos_time_label.setText("0:00")
        self.pos_duration_label.setText("0:00")
        
    def _on_position_slider(self):
        """Handle position slider changes (seeking)."""
        if self._updating_position or not self._active_service or self._current_length_us == 0:
            return
        
        # Convert slider percentage to microseconds
        target_position = int((self.pos_slider.value() / 100) * self._current_length_us)
        set_mpris_position(self._active_service, target_position)
        
    def _on_volume_slider(self, value):
        """Handle volume slider changes."""
        self.vol_pct_label.setText(f"{value}%")
        if self._app_hint:
            set_app_volume(
                self._app_hint,
                str(self._active_service) if self._active_service else None,
                value
            )
