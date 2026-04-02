"""Volume control for media players."""

import subprocess
import re


def get_app_volume(app_hint):
    """Read the per-application stream volume for the active media player.
    
    Uses `pactl list sink-inputs` to find the player's audio stream and
    returns its volume as an integer 0-100, or None on failure.

    This works correctly even with EasyEffects because it reads the
    per-app stream volume, not the virtual sink level.
    
    Args:
        app_hint: Application name hint (e.g., "spotify", "vlc")
        
    Returns:
        Volume as integer 0-100, or None if not found
    """
    try:
        r = subprocess.run(
            ["pactl", "list", "sink-inputs"],
            capture_output=True, text=True, timeout=2,
        )
        # pactl splits each stream with "Sink Input #N"
        blocks = r.stdout.split("Sink Input #")
        for block in blocks:
            if app_hint.lower() in block.lower():
                m = re.search(r"(\d+)%", block)
                if m:
                    return int(m.group(1))
    except Exception:
        pass
    return None


def set_app_volume(app_hint, service_name, value_pct):
    """Set playback volume.
    
    Strategy:
      1. MPRIS Properties.Set Volume (0.0-1.0) via dbus-send — no IDs needed
      2. Inline pactl lookup + set — fresh ID every call, atomic
      3. wpctl system volume fallback
      
    Args:
        app_hint: Application name hint (e.g., "spotify")
        service_name: MPRIS service name (e.g., org.mpris.MediaPlayer2.spotify)
        value_pct: Volume percentage 0-100
    """
    # 1. Try MPRIS Volume property
    if service_name:
        dbus_val = f"variant:double:{value_pct / 100:.4f}"
        r = subprocess.run(
            [
                "dbus-send", "--session", "--type=method_call",
                f"--dest={service_name}",
                "/org/mpris/MediaPlayer2",
                "org.freedesktop.DBus.Properties.Set",
                "string:org.mpris.MediaPlayer2.Player",
                "string:Volume",
                dbus_val,
            ],
            capture_output=True, timeout=2,
        )
        if r.returncode == 0:
            return

    # 2. pactl per-app stream — lookup and set in one block (no cached ID)
    try:
        r = subprocess.run(
            ["pactl", "list", "sink-inputs"],
            capture_output=True, text=True, timeout=2,
        )
        for block in r.stdout.split("Sink Input #"):
            if app_hint.lower() in block.lower():
                m = re.match(r"(\d+)", block.strip())
                if m:
                    result = subprocess.run(
                        ["pactl", "set-sink-input-volume", m.group(1), f"{value_pct}%"],
                        capture_output=True, timeout=2,
                    )
                    if result.returncode == 0:
                        return
    except Exception:
        pass

    # 3. wpctl system volume fallback
    subprocess.run(
        ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{value_pct / 100:.2f}"],
        capture_output=True, timeout=2,
    )
