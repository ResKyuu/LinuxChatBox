"""Active window detection for X11 and Wayland."""

import subprocess
import os


def get_active_window_x11():
    """Get the active window name using X11 tools (xdotool).
    
    Returns:
        str: Name of the active window, or None if detection fails
    """
    try:
        # Try xdotool first (most reliable for X11)
        result = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    try:
        # Fallback to xprop
        window_id = subprocess.run(
            ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if window_id.returncode == 0 and "window id" in window_id.stdout:
            wid = window_id.stdout.split()[-1]
            window_name = subprocess.run(
                ["xprop", "-id", wid, "WM_NAME"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if window_name.returncode == 0:
                # Extract window name from: WM_NAME(STRING) = "Window Title"
                parts = window_name.stdout.split('=', 1)
                if len(parts) == 2:
                    name = parts[1].strip().strip('"')
                    if name:
                        return name
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return None


def get_active_window_wayland_sway():
    """Get the active window name for Sway (Wayland compositor).
    
    Returns:
        str: Name of the active window, or None if detection fails
    """
    try:
        result = subprocess.run(
            ["swaymsg", "-t", "get_tree"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            import json
            tree = json.loads(result.stdout)
            
            def find_focused(node):
                """Recursively find the focused window."""
                if node.get("focused"):
                    return node.get("name") or node.get("app_id")
                for child in node.get("nodes", []) + node.get("floating_nodes", []):
                    focused = find_focused(child)
                    if focused:
                        return focused
                return None
            
            window_name = find_focused(tree)
            if window_name:
                return window_name
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, ValueError, KeyError):
        pass
    
    return None


def get_active_window_wayland_hyprland():
    """Get the active window name for Hyprland (Wayland compositor).
    
    Returns:
        str: Name of the active window, or None if detection fails
    """
    try:
        result = subprocess.run(
            ["hyprctl", "activewindow", "-j"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            # Try title first, then class name
            return data.get("title") or data.get("class")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError, ValueError, KeyError):
        pass
    
    return None


def get_active_window_wayland_gnome():
    """Get the active window name for GNOME (Wayland/Mutter).
    
    Returns:
        str: Name of the active window, or None if detection fails
    """
    # GNOME Wayland primarily uses XWayland for most apps
    # So we can use X11 tools that work with XWayland
    
    # Try xprop (works with XWayland apps, which most apps are)
    try:
        window_id = subprocess.run(
            ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if window_id.returncode == 0 and "window id" in window_id.stdout:
            wid = window_id.stdout.split()[-1]
            window_name = subprocess.run(
                ["xprop", "-id", wid, "WM_NAME"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if window_name.returncode == 0:
                # Extract window name from: WM_NAME(STRING) = "Window Title"
                parts = window_name.stdout.split('=', 1)
                if len(parts) == 2:
                    name = parts[1].strip().strip('"')
                    if name:
                        return name
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    # Fallback: Try wmctrl (if installed)
    try:
        result = subprocess.run(
            ["wmctrl", "-l", "-p"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0:
            # This is a less reliable fallback
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                # Return the first window's name (not ideal but better than nothing)
                parts = lines[0].split(None, 4)
                if len(parts) >= 5:
                    return parts[4]
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return None


def get_active_window_wayland_kde():
    """Get the active window name for KDE Plasma (Wayland).
    
    Returns:
        str: Name of the active window, or None if detection fails
    """
    try:
        # KDE Plasma uses KWin scripting
        result = subprocess.run(
            ["qdbus", "org.kde.KWin", "/KWin", "org.kde.KWin.activeWindow"],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    return None


def detect_session_type():
    """Detect whether we're running under X11 or Wayland.
    
    Returns:
        str: "x11", "wayland", or "unknown"
    """
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session_type in ("x11", "wayland"):
        return session_type
    
    # Fallback: check for WAYLAND_DISPLAY or DISPLAY
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    elif os.environ.get("DISPLAY"):
        return "x11"
    
    return "unknown"


def detect_wayland_compositor():
    """Detect which Wayland compositor is running.
    
    Returns:
        str: "sway", "hyprland", "kde", "gnome", or "unknown"
    """
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    
    if "sway" in desktop or os.environ.get("SWAYSOCK"):
        return "sway"
    elif "hyprland" in desktop or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "hyprland"
    elif "kde" in desktop or "plasma" in desktop:
        return "kde"
    elif "gnome" in desktop:
        return "gnome"
    
    return "unknown"


def get_active_window():
    """Get the currently active (focused) window name.
    
    This function automatically detects the session type (X11/Wayland)
    and uses the appropriate method to get the window name.
    
    Returns:
        str: Name of the active window, or "Desktop" if detection fails
    """
    session_type = detect_session_type()
    
    if session_type == "x11":
        window = get_active_window_x11()
        if window:
            return window
    
    elif session_type == "wayland":
        compositor = detect_wayland_compositor()
        
        if compositor == "sway":
            window = get_active_window_wayland_sway()
            if window:
                return window
        
        elif compositor == "hyprland":
            window = get_active_window_wayland_hyprland()
            if window:
                return window
        
        elif compositor == "kde":
            window = get_active_window_wayland_kde()
            if window:
                return window
        
        elif compositor == "gnome":
            window = get_active_window_wayland_gnome()
            if window:
                return window
        
        # Try all Wayland methods as fallback
        for method in [get_active_window_wayland_gnome,
                      get_active_window_wayland_sway, 
                      get_active_window_wayland_hyprland,
                      get_active_window_wayland_kde]:
            window = method()
            if window:
                return window
    
    # Ultimate fallback
    return "Desktop"
