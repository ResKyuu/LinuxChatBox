"""Configuration persistence for LinuxChatbox."""

import json
from pathlib import Path


CONFIG_PATH = Path.home() / ".config" / "linuxchatbox" / "config.json"


def save_config(opts, osc_port, discord_enabled=False, vrchat_port=9001, custom_statuses=None, custom_statuses_enabled=None, rotation_interval=30):
    """Persist DisplayOptions + OSC port + Discord settings + custom statuses to JSON."""
    if custom_statuses is None:
        custom_statuses = ["", "", "", "", ""]
    if custom_statuses_enabled is None:
        custom_statuses_enabled = [False, False, False, False, False]
    
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
        "custom_statuses": custom_statuses,
        "custom_statuses_enabled": custom_statuses_enabled,
        "rotation_interval": rotation_interval,
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config():
    """Load config from JSON. Returns (DisplayOptions, osc_port, discord_enabled, vrchat_port, custom_statuses, custom_statuses_enabled, rotation_interval). Safe on first run."""
    from .display_options import DisplayOptions
    
    opts = DisplayOptions()
    osc_port = 9000
    discord_enabled = False
    vrchat_port = 9001
    custom_statuses = ["", "", "", "", ""]
    custom_statuses_enabled = [False, False, False, False, False]
    rotation_interval = 30
    
    if not CONFIG_PATH.exists():
        return opts, osc_port, discord_enabled, vrchat_port, custom_statuses, custom_statuses_enabled, rotation_interval
    
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
        
        # Handle both old single status and new multi-status format
        if "custom_statuses" in data:
            custom_statuses = data.get("custom_statuses", custom_statuses)
            custom_statuses_enabled = data.get("custom_statuses_enabled", custom_statuses_enabled)
        elif "custom_status" in data:
            # Migrate old single status to new format
            old_status = data.get("custom_status", "")
            old_enabled = data.get("custom_status_enabled", False)
            if old_status:
                custom_statuses[0] = old_status
                custom_statuses_enabled[0] = old_enabled
        
        rotation_interval = data.get("rotation_interval", rotation_interval)
    except Exception as e:
        print(f"Config load error (using defaults): {e}")
    
    return opts, osc_port, discord_enabled, vrchat_port, custom_statuses, custom_statuses_enabled, rotation_interval
