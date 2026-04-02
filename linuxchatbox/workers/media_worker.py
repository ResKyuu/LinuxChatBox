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
        self._rebuild_osc()

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_osc_port(self, port):
        self._osc_port = port
        self._rebuild_osc()

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

        if playing_track:
            msg = build_osc_message(playing_track, self._opts)
        else:
            msg = self._opts.idle_message  # paused → send idle text
            self.idle_triggered.emit()

        try:
            self._osc_client.send_message("/chatbox/input", [msg, True])
            self.osc_sent.emit(msg)
        except Exception as e:
            self.error_occurred.emit(f"OSC send error: {e}")
