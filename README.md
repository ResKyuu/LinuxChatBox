# LinuxChatbox

**Native Linux VRChat chatbox for MPRIS media players**

Display your currently playing music in VRChat's chatbox using OSC. Works with any MPRIS-compatible media player on Linux—no Wine, no API keys, no tokens required.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

---

## ✨ Features

- 🎵 **MPRIS Integration** — Automatically detects any Linux media player via D-Bus
- 🎮 **VRChat OSC** — Sends formatted messages to VRChat chatbox in real-time
- 💬 **Discord Rich Presence** — Display VRChat world, player count, and music in Discord
- 🎨 **Customizable Display** — Configure prefix, separator, time format, and volume display
- 🎛️ **Media Controls** — Play/pause, next, previous, and volume control from the GUI
- 💾 **Persistent Config** — Settings saved to `~/.config/linuxchatbox/config.json`
- 🖥️ **Desktop Integration** — Launch from application menu like any other app
- 🐧 **Linux Native** — No Windows compatibility layers required

---

## 🚀 Quick Start

### Requirements

- **Python 3.10+**
- **PyQt6**
- **dbus-python**
- **python-osc**
- **pypresence** (for Discord Rich Presence)
- **PulseAudio** (`pactl`) or **PipeWire** (`wpctl`) for volume control

Most dependencies are likely already installed on your system.

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/reskyuu/linuxchatbox.git
   cd linuxchatbox
   ```

2. **Run the installer:**

   ```bash
   ./install.sh
   ```

   This will:
   - Install the Python package with pip
   - Create a desktop launcher entry
   - Install the application icon
   - Make `linuxchatbox` command available

3. **Launch the app:**
   - **From application menu**: Search for "LinuxChatbox" and click
   - **From terminal**: Run `linuxchatbox`

That's it! The app runs standalone with no terminal window required.

### Manual Installation

If you prefer manual installation:

```bash
# Install Python package
pip install -e . --user

# Install desktop integration (optional but recommended)
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp linuxchatbox/resources/linuxchatbox.desktop ~/.local/share/applications/
cp linuxchatbox/resources/icon.png ~/.local/share/icons/hicolor/256x256/apps/linuxchatbox.png
update-desktop-database ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor/ -f -t
```

---

## 📖 Usage

### Basic Workflow

1. **Start LinuxChatbox** from your application menu
2. **Play music** in any MPRIS-compatible player (Spotify, VLC, Firefox, etc.)
3. **Click "Start Sending"** to enable OSC transmission
4. **Open VRChat** — your music info appears in the chatbox!

### Supported Media Players

Any application that supports MPRIS2 will work automatically:

- Spotify
- VLC
- Firefox / Chrome (web players)
- Rhythmbox
- Audacious
- Strawberry
- And many more!

### Configuration Options

**Media Tab:**

- Toggle OSC sending on/off
- Configure OSC port (default: 9000)
- Media playback controls
- Volume slider

**Options Tab:**

- Message prefix (emoji or text)
- Title/artist separator
- Show/hide artist name
- Show/hide playback time
- Time format options
- Show/hide volume level
- Custom idle message

**Discord Tab:**

- Enable/disable Discord Rich Presence
- VRChat OSC listener port (default: 9001)
- Real-time world and player count display
- Discord presence preview

All settings are automatically saved to `~/.config/linuxchatbox/config.json`.

---

## 💬 Discord Rich Presence

LinuxChatbox can display your VRChat activity and currently playing music in Discord!

### What It Shows

- **VRChat World Name** — The world you're currently in
- **Player Count** — How many players are in the world with you
- **Current Song** — The music you're listening to (title and artist)
- **Custom Icon** — Static image configured by the app developer

### Setup

**No Discord Developer Portal setup required!** The app uses a pre-configured Discord application.

1. Enable Discord Rich Presence in the **Discord tab**
2. Make sure Discord is running
3. Configure VRChat to send OSC data:
   - In VRChat, go to **Settings → OSC**
   - Enable **OSC**
   - The app listens on port **9001** by default (configurable in Discord tab)

### VRChat OSC Configuration

VRChat doesn't natively send world info via OSC. To get world name and player count displayed in Discord, you'll need to use one of these methods:

**Option 1: Custom OSC App**
Use a third-party VRChat OSC tool that sends world data to the configured port.

**Option 2: Manual Testing**
You can test the Discord RPC with dummy data using OSC send tools.

**Note:** The music info will still display even without VRChat world data!

---

## 🖥️ Desktop Integration

### Launching Without Terminal

After installation, LinuxChatbox appears in your application menu and can be launched like any other desktop app—no terminal required!

**On GNOME:** Press Super → type "LinuxChatbox" → Enter  
**On KDE:** Click Application Launcher → type "LinuxChatbox"  
**On XFCE:** Applications Menu → Multimedia → LinuxChatbox

The app runs completely standalone. Close the terminal—it keeps running!

### Customizing the Icon

The default icon is a teal background with a music note. To use your own:

#### Option 1: Replace the icon file

```bash
# Copy your 256x256 PNG icon
cp /path/to/your/icon.png ~/.local/share/icons/hicolor/256x256/apps/linuxchatbox.png

# Update icon cache
gtk-update-icon-cache ~/.local/share/icons/hicolor/ -f -t
```

#### Option 2: Use a system icon

```bash
# Edit the desktop file
nano ~/.local/share/applications/linuxchatbox.desktop

# Change Icon= to a system icon name:
Icon=multimedia-player
# or: audio-headphones, preferences-desktop-sound, media-playback-start

# Update database
update-desktop-database ~/.local/share/applications/
```

#### Option 3: Create a custom icon with ImageMagick

```bash
# Purple theme
magick -size 256x256 -background '#a12c7b' -fill white -gravity center \
    -pointsize 160 label:'🎵' \
    ~/.local/share/icons/hicolor/256x256/apps/linuxchatbox.png

# Dark theme
magick -size 256x256 -background '#1c1b19' -fill '#4f98a3' -gravity center \
    -pointsize 160 label:'🎮' \
    ~/.local/share/icons/hicolor/256x256/apps/linuxchatbox.png

# Update cache
gtk-update-icon-cache ~/.local/share/icons/hicolor/ -f -t
```

After changing the icon, log out and back in (or restart) to see the changes.

---

## 🛠️ Configuration

### Config File Location

`~/.config/linuxchatbox/config.json`

### Example Configuration

```json
{
  "prefix": "🎵 ",
  "separator": " - ",
  "show_artist": true,
  "show_time": true,
  "time_format": "MM:SS / MM:SS",
  "idle_message": "⏸ Looking for music...",
  "show_volume": false,
  "volume_prefix": "🔊 ",
  "osc_port": 9000
}
```

Settings are automatically saved when you change them in the GUI.

---

## 🏗️ Project Structure

```
linuxchatbox/
├── linuxchatbox/           # Main package
│   ├── main.py             # Application entry point
│   ├── gui/                # UI components
│   │   ├── mainwindow.py   # Main window, tabs, status bar
│   │   ├── media_tab.py    # Media display and controls
│   │   └── options_tab.py  # Configuration options
│   ├── workers/            # Background threads
│   │   └── media_worker.py # MPRIS polling & OSC sending
│   ├── core/               # Core logic (no GUI dependencies)
│   │   ├── display_options.py  # Display configuration
│   │   ├── config.py       # Config persistence
│   │   ├── mpris.py        # MPRIS D-Bus interface
│   │   ├── osc.py          # OSC message builder
│   │   └── volume.py       # Volume control
│   └── resources/
│       ├── icon.png        # Application icon
│       └── linuxchatbox.desktop  # Desktop entry file
├── pyproject.toml          # Package metadata
├── install.sh              # One-command installer
└── README.md               # This file
```

### Architecture

- **GUI Layer** (`gui/`) — PyQt6 interface, separated by tabs
- **Worker Layer** (`workers/`) — Background threads for polling and OSC
- **Core Layer** (`core/`) — Pure logic with no GUI dependencies
- **Resources** — Desktop integration files and assets

This modular structure makes it easy to add new features (Status tab, System stats, etc.) without touching existing code.

---

## 🔧 Development

### Setting Up for Development

```bash
# Clone the repo
git clone https://github.com/reskyuu/linuxchatbox.git
cd linuxchatbox

# Install in editable mode
pip install -e . --user

# Run from source
python -m linuxchatbox.main
```

### Adding New Features

The modular architecture makes it easy to extend:

1. **New Tab** → Create `linuxchatbox/gui/<feature>_tab.py`
2. **New Worker** → Create `linuxchatbox/workers/<feature>_worker.py`
3. **New Core Logic** → Create `linuxchatbox/core/<feature>.py`

No need to touch the main window or existing modules.

### Dependencies

Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Testing

Currently testing is manual. To test:

1. Start a media player (Spotify, VLC, etc.)
2. Launch LinuxChatbox
3. Click "Start Sending"
4. Verify OSC messages in VRChat

---

## 🐛 Troubleshooting

### App doesn't appear in menu

```bash
update-desktop-database ~/.local/share/applications/
gtk-update-icon-cache ~/.local/share/icons/hicolor/ -f -t
```

Then log out and back in.

### Command not found: linuxchatbox

Add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### No media player detected

Make sure your player supports MPRIS2. Check with:

```bash
dbus-send --session --print-reply --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep mpris
```

### Volume control not working

LinuxChatbox requires PulseAudio (`pactl`) or PipeWire (`wpctl`). Check if installed:

```bash
which pactl wpctl
```

### OSC not reaching VRChat

- Verify VRChat is running and OSC is enabled
- Check OSC port is set to 9000 (or match VRChat's config)
- Firewall may be blocking UDP port 9000

### Discord Rich Presence not working

- Make sure Discord desktop app is running (web version doesn't support RPC)
- Check if Discord RPC is enabled in the Discord tab
- Restart the app if you just started Discord
- Port 9001 might be in use by another app (change in Discord tab settings)

### VRChat world info not showing in Discord

- VRChat doesn't natively send world info via OSC
- You need a custom OSC tool or world script to send world data
- Music will still display even without VRChat world info

---

## 🚀 Planned Features

- **Status Tab** — Custom status messages
- **Time Tab** — Display current time in chatbox
- **System Tab** — CPU and RAM usage display
- **Window Tab** — Currently focused application name
- **AppImage/Flatpak** — Easy distribution for all Linux distros
- **Enhanced VRChat Integration** — Better world info detection

---

## 📝 License

MIT License — see LICENSE file for details.

---

## 🙏 Credits

Inspired by **MagicChatbox** for Windows. LinuxChatbox brings the same functionality to Linux using native tools.

Built with:

- **PyQt6** — GUI framework
- **dbus-python** — MPRIS communication
- **python-osc** — VRChat OSC protocol

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

**Made with ❤️ for the Linux VRChat community**
