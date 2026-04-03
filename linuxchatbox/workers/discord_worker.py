"""Background worker thread for Discord Rich Presence."""

import os
import sys
import time
import threading
from PyQt6.QtCore import QThread, pyqtSignal

try:
    # IMPORTANT: Patch pypresence BEFORE baseclient uses it
    import pypresence.utils
    import pypresence.baseclient
    
    # Save original function
    _original_get_ipc_path = pypresence.utils.get_ipc_path
    
    def _patched_get_ipc_path(pipe=None):
        """Patched version that checks Flatpak location first."""
        user_id = os.getuid()
        
        # Flatpak Discord paths (check these first!)
        flatpak_paths = [
            f"/run/user/{user_id}/.flatpak/com.discordapp.Discord/xdg-run/discord-ipc-0",
            f"/run/user/{user_id}/.flatpak/com.discordapp.DiscordCanary/xdg-run/discord-ipc-0",
        ]
        
        import socket
        for path in flatpak_paths:
            if os.path.exists(path):
                try:
                    # Test if it's a valid socket
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                        client.settimeout(0.5)
                        client.connect(path)
                        return path
                except (OSError, socket.timeout):
                    continue
        
        # Fall back to original implementation for non-Flatpak
        return _original_get_ipc_path(pipe)
    
    # Apply patch to both the utils module AND the baseclient's imported reference
    pypresence.utils.get_ipc_path = _patched_get_ipc_path
    pypresence.baseclient.get_ipc_path = _patched_get_ipc_path
    
    # Now import Presence (which will use the patched function)
    from pypresence import Presence
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False

from ..core.discord_rpc import DISCORD_APP_ID, build_discord_presence


class DiscordWorker(QThread):
    """Background thread that manages Discord Rich Presence connection."""
    
    status_changed = pyqtSignal(str)  # Connection status messages
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self._enabled = False
        self._running = True
        self._rpc = None
        self._connected = False
        
        # Song data
        self._song_title = None
        self._song_artist = None
        
        # Active window data
        self._active_window = None
        
        # Update interval and trigger
        self._update_interval = 5
        self._force_update = threading.Event()
        
    def set_enabled(self, enabled):
        """Enable or disable Discord RPC."""
        self._enabled = enabled
        if not enabled and self._connected:
            self._disconnect()
        
    def set_song_data(self, title, artist=None):
        """Update currently playing song data."""
        self._song_title = title
        self._song_artist = artist
        self._force_update.set()  # Trigger immediate update
        
    def set_active_window(self, window_name):
        """Update currently active window."""
        self._active_window = window_name
        self._force_update.set()  # Trigger immediate update
        
    def stop(self):
        """Stop the worker thread."""
        self._running = False
        self._disconnect()
        
    def _connect(self):
        """Connect to Discord RPC."""
        if not PYPRESENCE_AVAILABLE:
            self.error_occurred.emit("pypresence not installed")
            return False
            
        try:
            # The monkey-patch applied on module import will handle Flatpak
            self._rpc = Presence(DISCORD_APP_ID)
            self._rpc.connect()
            self._connected = True
            self.status_changed.emit("Connected to Discord")
            # Immediately update presence after connecting
            self._update_presence()
            return True
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "Could not find discord" in error_msg:
                self.error_occurred.emit("Discord not running (try restarting Discord)")
            else:
                self.error_occurred.emit(f"Discord connection failed: {e}")
            self._rpc = None
            self._connected = False
            return False
            
    def _disconnect(self):
        """Disconnect from Discord RPC."""
        if self._rpc and self._connected:
            try:
                self._rpc.close()
                self.status_changed.emit("Disconnected from Discord")
            except:
                pass
        self._rpc = None
        self._connected = False
        
    def _update_presence(self):
        """Update Discord presence with current data."""
        if not self._connected or not self._rpc:
            return
            
        try:
            # Build presence with song and active window data
            presence = build_discord_presence(
                song_title=self._song_title,
                song_artist=self._song_artist,
                active_window=self._active_window
            )
            
            # Update Discord
            self._rpc.update(**presence)
            
        except Exception as e:
            self.error_occurred.emit(f"Discord update failed: {e}")
            # Try to reconnect on next cycle
            self._connected = False
            
    def run(self):
        """Main worker loop."""
        while self._running:
            # Connect if enabled and not connected
            if self._enabled and not self._connected:
                if self._connect():
                    pass
                
            # Disconnect if disabled and connected
            elif not self._enabled and self._connected:
                self._disconnect()
                
            # Update presence if connected
            elif self._enabled and self._connected:
                self._update_presence()
                
            # Wait for update interval OR immediate trigger
            self._force_update.wait(timeout=self._update_interval)
            self._force_update.clear()
