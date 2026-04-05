# LinuxChatbox

A native Linux version of **MagicChatbox** for VRChat. Display your currently playing music in VRChat's chatbox using OSC and MPRIS media players.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

---

## ✨ Features

- **MPRIS Integration** — Works with any Linux media player (Spotify, VLC, Firefox, etc.)
- **VRChat OSC** — Sends formatted messages to VRChat chatbox in real-time
- **Discord Rich Presence** — Display Current Activity & what you're currently listening to
- **Customizable Display** — Configure prefix, separator, time format, and volume display
- **Media Controls** — Play/pause, next, previous, and volume control from the GUI
- **Custom Status** - Set up to 5 Custom Statuses and customize their rotation interval as you like
- **Desktop Integration** — Launch from application menu like any other app

---

## How It Works

LinuxChatbox monitors your MPRIS-compatible media players via D-Bus and sends the currently playing track info to VRChat using the OSC protocol. It's a pure Linux implementation—no Wine, no Windows compatibility layers, no API keys required.

---

## 🚀 Installation

### Prerequisites: Install Python 3.10+

Most Linux distributions come with Python 3 pre-installed. If not, install it using your package manager:

**Debian/Ubuntu/Pop!\_OS/Linux Mint:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora/RHEL/CentOS:**

```bash
sudo dnf install python3 python3-pip
```

**Arch/Manjaro:**

```bash
sudo pacman -S python python-pip
```

**openSUSE:**

```bash
sudo zypper install python3 python3-pip
```

**Gentoo:**

```bash
sudo emerge --ask dev-lang/python
```

**Void Linux:**

```bash
sudo xbps-install -S python3 python3-pip
```

**Alpine Linux:**

```bash
sudo apk add python3 py3-pip
```

**NixOS:**

```bash
nix-env -iA nixpkgs.python3
```

### Install LinuxChatbox

1. **Clone the repository:**

   ```bash
   git clone https://github.com/reskyuu/linuxchatbox.git
   cd linuxchatbox
   ```

2. **Run the installer:**

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Launch the app:**
   - From application menu: Search for "LinuxChatbox"
   - From terminal: Run `linuxchatbox`

---

## 📖 Usage

1. Start LinuxChatbox from your application menu
2. Play music in any MPRIS-compatible player
3. Click "Start Sending" to enable OSC transmission
4. Open VRChat — your music info appears in the chatbox!

---

## 📝 License & Credits

**This program is 100% AI-written.** I (ResKyuu) take no credit for the code.

LinuxChatbox is licensed under the MIT License. You are free to distribute, modify, and contribute to this project as you wish.

Inspired by (MagicChatbox)[https://github.com/BoiHanny/vrcosc-magicchatbox] for Windows.

---

**Made for the Linux VRChat community**
