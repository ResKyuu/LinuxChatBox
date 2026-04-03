"""Configuration persistence for LinuxChatbox."""

import json
from pathlib import Path


CONFIG_PATH = Path.home() / ".config" / "linuxchatbox" / "config.json"


def save_config(opts, osc_port, discord_enabled=False, vrchat_port=9001):
    """Persist DisplayOptions + OSC port + Discord settings to JSON."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "prefix":          opts.prefix,
        "separator":       opts.separator,
        "show_artist":     opts.show_artist,
        "show_time":       opts.show_time,
        "time_format":     opts.time_format,
        "idle_message":    opts.idle_message,
        "show_volume":     opts.show_volume,
        "volume_prefix":   opts.volume_prefix,
        "osc_port":        osc_port,
        "discord_enabled": discord_enabled,
        "vrchat_port":     vrchat_port,
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config():
    """Load config from JSON. Returns (DisplayOptions, osc_port, discord_enabled, vrchat_port). Safe on first run."""
    from .display_options import DisplayOptions
    
    opts = DisplayOptions()
    osc_port = 9000
    discord_enabled = False
    vrchat_port = 9001
    
    if not CONFIG_PATH.exists():
        return opts, osc_port, discord_enabled, vrchat_port
    
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        opts.prefix        = data.get("prefix",          opts.prefix)
        opts.separator     = data.get("separator",       opts.separator)
        opts.show_artist   = data.get("show_artist",     opts.show_artist)
        opts.show_time     = data.get("show_time",       opts.show_time)
        opts.time_format   = data.get("time_format",     opts.time_format)
        opts.idle_message  = data.get("idle_message",    opts.idle_message)
        opts.show_volume   = data.get("show_volume",     opts.show_volume)
        opts.volume_prefix = data.get("volume_prefix",   opts.volume_prefix)
        osc_port           = data.get("osc_port",        osc_port)
        discord_enabled    = data.get("discord_enabled", discord_enabled)
        vrchat_port        = data.get("vrchat_port",     vrchat_port)
    except Exception as e:
        print(f"Config load error (using defaults): {e}")
    
    return opts, osc_port, discord_enabled, vrchat_port
