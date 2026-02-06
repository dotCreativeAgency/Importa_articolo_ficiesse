"""Console utilities for cross-platform terminal compatibility.

Handles:
- Windows UTF-8 encoding setup (chcp 65001 equivalent)
- Emoji fallback for terminals without Unicode support
"""

import sys
import os

# Emoji to ASCII fallback mapping
EMOJI_MAP = {
    "✅": "[OK]",
    "❌": "[X]",
    "⚠️": "[!]",
    "✓": "[v]",
    "📁": "[D]",
    "📄": "[F]",
    "🔄": "[~]",
    "💾": "[S]",
    "→": "->",
    "━": "-",
    "═": "=",
}

# Global flag for emoji mode
_use_emoji = True


def setup_console():
    """Configure console for UTF-8 on Windows.
    
    Call this at the start of your main() function.
    Returns True if UTF-8 is properly configured.
    """
    if sys.platform == "win32":
        try:
            # Skip subprocess call during tests to avoid side effects
            if "pytest" not in sys.modules:
                # Set UTF-8 code page for Windows console
                import subprocess
                subprocess.run(
                    ["chcp", "65001"],
                    shell=True,
                    capture_output=True,
                    check=False
                )
            
            # Reconfigure stdout/stderr for UTF-8
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            
            # Set environment variable for child processes
            os.environ["PYTHONIOENCODING"] = "utf-8"
            
            return True
        except Exception:
            return False
    return True


def set_emoji_mode(use_emoji: bool):
    """Set whether to use emoji or ASCII fallbacks."""
    global _use_emoji
    _use_emoji = use_emoji


def get_emoji_mode() -> bool:
    """Get current emoji mode."""
    return _use_emoji


def e(emoji: str) -> str:
    """Return emoji or ASCII fallback based on current mode.
    
    Usage:
        from lib.console import e
        print(f"{e('✅')} Operazione completata!")
    """
    if _use_emoji:
        return emoji
    return EMOJI_MAP.get(emoji, emoji)


def safe_print(*args, **kwargs):
    """Print with automatic encoding error handling.
    
    Falls back to ASCII representation if encoding fails.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert to ASCII-safe representation
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace emoji with fallbacks
                safe_arg = arg
                for emoji, fallback in EMOJI_MAP.items():
                    safe_arg = safe_arg.replace(emoji, fallback)
                safe_args.append(safe_arg.encode("ascii", "replace").decode("ascii"))
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)
