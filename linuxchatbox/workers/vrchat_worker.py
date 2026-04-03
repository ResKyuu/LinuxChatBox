"""Background worker thread for VRChat OSC listener."""

from PyQt6.QtCore import QThread, pyqtSignal

try:
    from pythonosc import dispatcher, osc_server
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False

from ..core.vrchat_osc import parse_vrchat_message


class VRChatWorker(QThread):
    """Background thread that listens for OSC messages from VRChat."""
    
    world_updated = pyqtSignal(str, int)  # world_name, player_count
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self._vrchat_port = 9001  # Default VRChat OSC receive port
        self._server = None
        self._running = True
        self._current_world = None
        self._current_player_count = 0
        
    def set_vrchat_port(self, port):
        """Change the VRChat OSC listening port."""
        self._vrchat_port = port
        
    def stop(self):
        """Stop the worker thread and OSC server."""
        self._running = False
        if self._server:
            self._server.shutdown()
        
    def run(self):
        """Main worker loop - runs OSC server."""
        if not OSC_AVAILABLE:
            self.error_occurred.emit("python-osc not available")
            return
            
        try:
            # Create OSC dispatcher
            disp = dispatcher.Dispatcher()
            disp.set_default_handler(self._handle_osc_message)
            
            # Create and run OSC server
            self._server = osc_server.ThreadingOSCUDPServer(
                ("127.0.0.1", self._vrchat_port), disp
            )
            
            # Server blocks until shutdown() is called
            self._server.serve_forever()
            
        except OSError as e:
            if "Address already in use" in str(e):
                self.error_occurred.emit(f"Port {self._vrchat_port} already in use")
            else:
                self.error_occurred.emit(f"OSC server error: {e}")
        except Exception as e:
            self.error_occurred.emit(f"VRChat OSC error: {e}")
            
    def _handle_osc_message(self, address, *args):
        """Handle incoming OSC message from VRChat.
        
        Args:
            address: OSC address string
            *args: OSC message arguments
        """
        parsed = parse_vrchat_message(address, args)
        
        if parsed is None:
            return
            
        msg_type = parsed.get('type')
        
        # Handle world name updates
        if msg_type == 'world' or msg_type == 'world_name':
            world_name = parsed.get('world_name')
            if world_name and world_name != self._current_world:
                self._current_world = world_name
                # If we got player count in the same message
                if 'player_count' in parsed:
                    self._current_player_count = parsed['player_count']
                self.world_updated.emit(self._current_world, self._current_player_count)
                
        # Handle player count updates
        elif msg_type == 'player_count':
            player_count = parsed.get('player_count', 0)
            if player_count != self._current_player_count:
                self._current_player_count = player_count
                if self._current_world:
                    self.world_updated.emit(self._current_world, self._current_player_count)
