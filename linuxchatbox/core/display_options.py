"""Display options and formatting configuration."""


class DisplayOptions:
    """All user-configurable display/format settings. Shared between GUI and worker."""
    def __init__(self):
        self.prefix       = "\U0001f3b5 "   # 🎵
        self.separator    = " - "
        self.show_artist  = True
        self.show_time    = True
        self.time_format  = "MM:SS / MM:SS"
        self.idle_message = "\u23f8 Looking for music..."   # ⏸
        self.show_volume  = False
        self.volume_prefix = "\U0001f50a "   # 🔊


def _fmt(us):
    """Format microseconds as MM:SS."""
    s = us // 1_000_000
    return f"{s // 60:02d}:{s % 60:02d}"


def _fmt_short(us):
    """Format microseconds as M:SS."""
    s = us // 1_000_000
    return f"{s // 60}:{s % 60:02d}"


TIME_FORMATS = {
    "MM:SS / MM:SS":         lambda p, d: f"{_fmt(p)} / {_fmt(d)}",
    "M:SS / M:SS":           lambda p, d: f"{_fmt_short(p)} / {_fmt_short(d)}",
    "MM:SS (position only)": lambda p, d: _fmt(p),
    "[MM:SS / MM:SS]":       lambda p, d: f"[{_fmt(p)} / {_fmt(d)}]",
    "(MM:SS / MM:SS)":       lambda p, d: f"({_fmt(p)} / {_fmt(d)})",
}
