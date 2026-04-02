"""OSC message building for VRChat chatbox."""

from .display_options import TIME_FORMATS


def build_osc_message(track, opts):
    """Build the VRChat chatbox string from track data and display options.
    
    Args:
        track: dict with keys: title, artist, position_us, length_us, volume (optional)
        opts: DisplayOptions instance
        
    Returns:
        Formatted string ready to send via OSC
    """
    line1 = opts.prefix + track["title"]
    if opts.show_artist and track["artist"]:
        line1 += opts.separator + track["artist"]

    vol_str = ""
    if opts.show_volume and track.get("volume") is not None:
        vol_str = f"  {opts.volume_prefix}{track['volume']}%"

    if opts.show_time:
        fmt_fn = TIME_FORMATS.get(opts.time_format, TIME_FORMATS["MM:SS / MM:SS"])
        return line1 + "\n" + fmt_fn(track["position_us"], track["length_us"]) + vol_str
    if vol_str:
        return line1 + "\n" + vol_str.strip()
    return line1
