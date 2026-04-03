"""Background worker thread for media player polling and OSC sending."""

import threading

from PyQt6.QtCore import QThread, pyqtSignal

try:
    from pythonosc import udp_client
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False

from ..core.mpris import get_mpris_players, get_mpris_track
from ..core.osc import build_osc_message
from ..core.volume import get_app_volume


class MediaWorker(QThread):
    """Background thread that polls MPRIS players and sends OSC messages to VRChat."""
    
    track_updated    = pyqtSignal(dict)   # a track is actively Playing
    idle_triggered   = pyqtSignal()       # enabled but nothing playing
    no_media         = pyqtSignal()       # disabled and nothing playing
    osc_sent         = pyqtSignal(str)
    error_occurred   = pyqtSignal(str)
    interval_changed = pyqtSignal(int)

    def __init__(self, opts, parent=None):
        super().__init__(parent)
        self._opts         = opts
        self._enabled      = False
        self._osc_port     = 9000
        self._running      = True
        self._interval     = 2
        self._osc_client   = None
        self._last_service = None           # most recent active MPRIS service
        self._wake_event   = threading.Event()  # used for clean shutdown
        self._custom_statuses = ["", "", "", "", ""]
        self._custom_statuses_enabled = [False, False, False, False, False]
        self._rotation_interval = 30
        self._rotation_counter = 0  # Track time for rotation
        self._current_status_index = 0  # Which status is currently displayed
        self._playback_enabled = True  # New: control playback messages separately
        self._rebuild_osc()

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_osc_port(self, port):
        self._osc_port = port
        self._rebuild_osc()
    
    def set_custom_statuses(self, custom_statuses, custom_statuses_enabled, rotation_interval):
        """Update the custom status messages with rotation."""
        self._custom_statuses = custom_statuses
        self._custom_statuses_enabled = custom_statuses_enabled
        self._rotation_interval = rotation_interval
        self._rotation_counter = 0  # Reset rotation counter
        self._current_status_index = 0  # Reset to first status
    
    def set_playback_enabled(self, enabled):
        """Enable/disable sending playback messages."""
        self._playback_enabled = enabled
    
    def _get_current_status(self):
        """Get the current status to display (handles rotation)."""
        # Get list of enabled statuses
        enabled_statuses = [
            (i, self._custom_statuses[i])
            for i in range(5)
            if self._custom_statuses_enabled[i] and self._custom_statuses[i].strip()
        ]
        
        if not enabled_statuses:
            return None
        
        if len(enabled_statuses) == 1:
            # Only one status, always return it
            return enabled_statuses[0][1]
        
        # Multiple statuses - handle rotation
        # Make sure current index is valid
        if self._current_status_index >= len(enabled_statuses):
            self._current_status_index = 0
        
        return enabled_statuses[self._current_status_index][1]
    
    def _update_rotation(self):
        """Update rotation counter and advance to next status if needed."""
        # Get list of enabled statuses
        enabled_statuses = [
            i for i in range(5)
            if self._custom_statuses_enabled[i] and self._custom_statuses[i].strip()
        ]
        
        if len(enabled_statuses) <= 1:
            # No rotation needed
            return
        
        # Increment rotation counter
        self._rotation_counter += self._interval
        
        if self._rotation_counter >= self._rotation_interval:
            # Time to rotate
            self._current_status_index = (self._current_status_index + 1) % len(enabled_statuses)
            self._rotation_counter = 0

    def stop(self):
        self._running = False
        self._wake_event.set()

    def _rebuild_osc(self):
        if not OSC_AVAILABLE:
            return
        try:
            self._osc_client = udp_client.SimpleUDPClient("127.0.0.1", self._osc_port)
        except Exception as e:
            self._osc_client = None
            self.error_occurred.emit(f"OSC init error: {e}")

    def run(self):
        while self._running:
            try:
                self._tick()
            except Exception as e:
                self.error_occurred.emit(str(e))
            self._wake_event.wait(timeout=self._interval)
            self._wake_event.clear()

    def _tick(self):
        players = get_mpris_players()

        # ── Find playing track (for OSC) and any track (for UI + buttons) ──
        playing_track = None
        display_track = None

        for svc in players:
            t = get_mpris_track(svc)
            if t and t["status"] == "Playing":
                playing_track = t
                display_track = t
                break

        # Fall back to any paused/stopped player for UI display & button control
        if display_track is None and players:
            display_track = get_mpris_track(players[0])

        # ── No players at all ─────────────────────────────────────────────
        if display_track is None:
            self._interval = 2
            self.no_media.emit()
            return

        # ── Update UI — always, for any player state ──────────────────────
        self._last_service = display_track["service"]
        total_seconds  = display_track["length_us"] // 1_000_000
        self._interval = 2 if total_seconds % 2 == 0 else 3
        self.interval_changed.emit(self._interval)

        if self._opts.show_volume:
            app_hint = display_track["service"].replace("org.mpris.MediaPlayer2.", "")
            vol = get_app_volume(app_hint)
            display_track["volume"] = vol
            if vol is None:
                self.error_occurred.emit("Volume: could not find stream in pactl sink-inputs")
        else:
            display_track["volume"] = None

        self.track_updated.emit(display_track)  # always emitted → buttons always enabled

        # ── OSC sending ───────────────────────────────────────────────────
        if not self._enabled or not self._osc_client:
            return

        # Update rotation (advances to next status if time elapsed)
        self._update_rotation()
        
        # Get current status (handles rotation)
        current_status = self._get_current_status()

        # Build the message based on playback toggle
        if self._playback_enabled and playing_track:
            # Playing: send playback with current status
            msg = build_osc_message(playing_track, self._opts, current_status or "", current_status is not None)
        elif self._playback_enabled:
            # Paused → send idle text with current status
            msg = self._opts.idle_message
            if current_status:
                msg = current_status + "\n" + msg
            self.idle_triggered.emit()
        else:
            # Playback disabled → only send current status or nothing
            if current_status:
                msg = current_status
            else:
                # Nothing to send
                return

        try:
            self._osc_client.send_message("/chatbox/input", [msg, True])
            self.osc_sent.emit(msg)
        except Exception as e:
            self.error_occurred.emit(f"OSC send error: {e}")
