"""MPRIS D-Bus helpers for media player detection and control."""

import subprocess

try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False


def get_mpris_players():
    """Get list of available MPRIS players on session bus."""
    if not DBUS_AVAILABLE:
        return []
    try:
        bus = dbus.SessionBus()
        return [n for n in bus.list_names() if n.startswith("org.mpris.MediaPlayer2.")]
    except Exception:
        return []


def get_mpris_track(service_name):
    """Get track metadata from MPRIS player.
    
    Returns:
        dict with keys: title, artist, position_us, length_us, status, service, art_url
        or None if failed
    """
    if not DBUS_AVAILABLE:
        return None
    try:
        bus = dbus.SessionBus()
        obj = bus.get_object(service_name, "/org/mpris/MediaPlayer2")
        props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")

        status = str(props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus"))
        meta   = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")

        title       = str(meta.get("xesam:title", "Unknown"))
        artist_list = meta.get("xesam:artist", ["Unknown"])
        artist      = str(artist_list[0]) if artist_list else "Unknown"

        try:
            position_us = int(props.Get("org.mpris.MediaPlayer2.Player", "Position"))
        except Exception:
            position_us = 0

        length_us = int(meta.get("mpris:length", 0))
        
        # Get album artwork URL
        art_url = meta.get("mpris:artUrl", "")
        if art_url:
            art_url = str(art_url)

        return {
            "title": title, "artist": artist,
            "position_us": position_us, "length_us": length_us,
            "status": status, "service": service_name,
            "art_url": art_url,
        }
    except Exception:
        return None


def send_mpris_command(service_name, command):
    """Send an MPRIS2 playback command using dbus-send subprocess.
    
    Bypasses dbus-python entirely — avoids GLib main loop requirement.
    Works reliably from any thread or the GUI thread.
    
    Args:
        service_name: MPRIS service name (e.g., org.mpris.MediaPlayer2.spotify)
        command: 'PlayPause' | 'Next' | 'Previous'
    """
    if not service_name:
        return
    try:
        subprocess.Popen(
            [
                "dbus-send",
                "--session",
                "--type=method_call",
                f"--dest={service_name}",
                "/org/mpris/MediaPlayer2",
                f"org.mpris.MediaPlayer2.Player.{command}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # dbus-send not found — try playerctl as fallback
        cmd_map = {"PlayPause": "play-pause", "Next": "next", "Previous": "previous"}
        playerctl_cmd = cmd_map.get(command, command.lower())
        try:
            player_name = service_name.replace("org.mpris.MediaPlayer2.", "")
            subprocess.Popen(
                ["playerctl", "-p", player_name, playerctl_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass
    except Exception:
        pass


def set_mpris_position(service_name, position_us):
    """Set the playback position in microseconds.
    
    Args:
        service_name: MPRIS service name
        position_us: Position in microseconds
    """
    if not DBUS_AVAILABLE or not service_name:
        return
    try:
        bus = dbus.SessionBus()
        obj = bus.get_object(service_name, "/org/mpris/MediaPlayer2")
        player = dbus.Interface(obj, "org.mpris.MediaPlayer2.Player")
        
        # Get current track ID
        props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
        meta = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        track_id = meta.get("mpris:trackid", "/")
        
        # SetPosition requires track ID and position
        player.SetPosition(track_id, dbus.Int64(position_us))
    except Exception:
        pass  # Silently fail - not all players support seeking
