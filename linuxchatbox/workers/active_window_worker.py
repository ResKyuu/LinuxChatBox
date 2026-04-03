"""Background worker thread for active window detection."""

import time
from PyQt6.QtCore import QThread, pyqtSignal

from ..core.active_window import get_active_window


class ActiveWindowWorker(QThread):
    """Background thread that polls for the currently active window."""
    
    window_changed = pyqtSignal(str)  # Emits window name when it changes
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self._running = True
        self._last_window = None
        self._poll_interval = 2.5  # Check every 2.5 seconds
        
    def stop(self):
        """Stop the worker thread."""
        self._running = False
        
    def run(self):
        """Main worker loop that polls for active window changes."""
        while self._running:
            try:
                # Get current active window
                current_window = get_active_window()
                
                # Only emit signal if window has changed
                if current_window != self._last_window:
                    self._last_window = current_window
                    self.window_changed.emit(current_window)
                    
            except Exception as e:
                # Don't spam errors - only emit once per unique error
                error_msg = f"Window detection error: {str(e)}"
                self.error_occurred.emit(error_msg)
                # Continue running even if there's an error
                
            # Wait before next poll
            time.sleep(self._poll_interval)
