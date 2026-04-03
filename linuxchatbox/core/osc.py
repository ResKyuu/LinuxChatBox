"""OSC message building for VRChat chatbox."""

from .display_options import TIME_FORMATS


def build_osc_message(track, opts, custom_status="", custom_status_enabled=False):
    """Build the VRChat chatbox string from track data and display options.
    
    Args:
        track: dict with keys: title, artist, position_us, length_us, volume (optional)
        opts: DisplayOptions instance
        custom_status: Custom status message to prepend
        custom_status_enabled: Whether to include the custom status
        
    Returns:
        Formatted string ready to send via OSC
    """
    line1 = opts.prefix + track["title"]
    if opts.show_artist and track["artist"]:
        line1 += opts.separator + track["artist"]

    vol_str = ""
    if opts.show_volume and track.get("volume") is not None:
        vol_str = f"  {opts.volume_prefix}{track['volume']}%"

    playback_message = ""
    if opts.show_time:
        fmt_fn = TIME_FORMATS.get(opts.time_format, TIME_FORMATS["MM:SS / MM:SS"])
        playback_message = line1 + "\n" + fmt_fn(track["position_us"], track["length_us"]) + vol_str
    elif vol_str:
        playback_message = line1 + "\n" + vol_str.strip()
    else:
        playback_message = line1
    
    # Prepend custom status if enabled
    if custom_status_enabled and custom_status.strip():
        return custom_status.strip() + "\n" + playback_message
    
    return playback_message
