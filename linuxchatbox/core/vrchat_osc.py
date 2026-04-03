"""VRChat OSC message parsing."""


def parse_vrchat_message(address, args):
    """Parse VRChat OSC messages for world and player data.
    
    VRChat sends various OSC messages including:
    - /avatar/parameters/* - Avatar parameters
    - /avatar/change - Avatar changes
    
    For world/player info, we'll need to listen to custom messages.
    VRChat doesn't natively send world info via OSC, but can be obtained
    through VRChat API or custom OSC apps.
    
    Args:
        address: OSC address string (e.g., "/avatar/parameters/VRChatWorld")
        args: List of arguments from OSC message
        
    Returns:
        dict with 'type', 'world_name', 'player_count', etc., or None if not relevant
    """
    # World name message (custom OSC address we'll listen for)
    if address == "/chatbox/vrchat/world":
        if args and len(args) >= 1:
            return {
                'type': 'world',
                'world_name': str(args[0]),
                'player_count': int(args[1]) if len(args) >= 2 else 0
            }
    
    # Alternative: Parse from VRChat's avatar parameters if using custom world script
    if address.startswith("/avatar/parameters/"):
        param_name = address.split("/avatar/parameters/", 1)[1]
        if param_name == "WorldName" and args:
            return {
                'type': 'world_name',
                'world_name': str(args[0])
            }
        if param_name == "PlayerCount" and args:
            return {
                'type': 'player_count',
                'player_count': int(args[0])
            }
    
    return None


def build_vrchat_info_string(world_name, player_count):
    """Build a formatted string for VRChat world info.
    
    Args:
        world_name: Name of the VRChat world
        player_count: Number of players in the world
        
    Returns:
        Formatted string for display
    """
    if not world_name:
        return "Not in VRChat"
    
    if player_count is not None and player_count > 0:
        return f"{world_name} ({player_count} player{'s' if player_count != 1 else ''})"
    return world_name
