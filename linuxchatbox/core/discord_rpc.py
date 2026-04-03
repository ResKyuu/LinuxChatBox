"""Discord Rich Presence message building."""

# Discord Application Configuration
DISCORD_APP_ID = "1489645857614729347"
DISCORD_IMAGE_KEY = "lcb_icon"


def build_discord_presence(song_title=None, song_artist=None, active_window=None):
    """Build Discord Rich Presence data for LinuxChatbox.
    
    Args:
        song_title: Currently playing song title (optional)
        song_artist: Song artist (optional)
        active_window: Currently focused window/application name (optional)
        
    Returns:
        Dict ready for pypresence.update()
    """
    presence = {
        "large_image": DISCORD_IMAGE_KEY,
        "large_text": "LinuxChatbox",
    }
    
    # Details: Current Activity (window)
    if active_window:
        presence["details"] = f"Current Activity: {active_window}"
    else:
        presence["details"] = "Current Activity: Desktop"
    
    # State: Currently playing (song)
    if song_title:
        if song_artist:
            presence["state"] = f"Currently playing: {song_title} - {song_artist}"
        else:
            presence["state"] = f"Currently playing: {song_title}"
    else:
        presence["state"] = "Currently playing: Nothing"
    
    return presence
