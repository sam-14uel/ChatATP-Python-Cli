"""
Cross-platform notification system for ChatATP CLI
Supports desktop notifications and sound alerts on all major platforms.
"""

import os
import sys
import platform
from typing import Optional
import threading
import time

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class NotificationManager:
    """Cross-platform notification manager with sound support"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.system = platform.system().lower()
        self._sound_enabled = True

        if not PLYER_AVAILABLE:
            print("Warning: plyer not available. Desktop notifications disabled.")
            self.enabled = False

    def enable_notifications(self):
        """Enable desktop notifications"""
        self.enabled = True

    def disable_notifications(self):
        """Disable desktop notifications"""
        self.enabled = False

    def enable_sound(self):
        """Enable sound notifications"""
        self._sound_enabled = True

    def disable_sound(self):
        """Disable sound notifications"""
        self._sound_enabled = False

    def notify(self,
               title: str,
               message: str = "",
               icon: Optional[str] = None,
               timeout: int = 5,
               sound: bool = True) -> bool:
        """
        Send a desktop notification

        Args:
            title: Notification title
            message: Notification message
            icon: Path to icon file (optional)
            timeout: Timeout in seconds
            sound: Whether to play sound

        Returns:
            bool: True if notification was sent successfully
        """
        if not self.enabled or not PLYER_AVAILABLE:
            return False

        try:
            # Send desktop notification
            notification.notify(
                title=title,
                message=message,
                app_name="ChatATP CLI",
                app_icon=icon,
                timeout=timeout
            )

            # Play sound in a separate thread to avoid blocking
            if sound and self._sound_enabled:
                threading.Thread(target=self._play_sound, daemon=True).start()

            return True

        except Exception as e:
            # Silently fail for notification errors
            print(f"Notification error: {e}", file=sys.stderr)
            return False

    def _play_sound(self):
        """Play notification sound cross-platform"""
        try:
            if self.system == "windows":
                self._play_windows_sound()
            elif self.system == "darwin":  # macOS
                self._play_macos_sound()
            elif self.system == "linux":
                self._play_linux_sound()
            else:
                # Fallback - try system bell
                print('\a', end='', flush=True)

        except Exception:
            # If sound fails, just use system bell as fallback
            try:
                print('\a', end='', flush=True)
            except:
                pass

    def _play_windows_sound(self):
        """Play notification sound on Windows"""
        try:
            import winsound
            winsound.MessageBeep(winsound.SND_ALIAS)
        except ImportError:
            # winsound not available, use system bell
            print('\a', end='', flush=True)

    def _play_macos_sound(self):
        """Play notification sound on macOS"""
        try:
            os.system("afplay /System/Library/Sounds/Ping.aiff")
        except:
            print('\a', end='', flush=True)

    def _play_linux_sound(self):
        """Play notification sound on Linux"""
        try:
            # Try various sound commands
            sound_commands = [
                "paplay /usr/share/sounds/freedesktop/stereo/message.oga",
                "aplay /usr/share/sounds/alsa/Front_Center.wav",
                "beep",
                "play -q -n synth 0.1 sin 800"  # sox fallback
            ]

            for cmd in sound_commands:
                if os.system(f"{cmd} 2>/dev/null") == 0:
                    break
        except:
            print('\a', end='', flush=True)

    def notify_ai_start(self, model_name: str = ""):
        """Notify when AI starts responding"""
        model_info = f" ({model_name})" if model_name else ""
        return self.notify(
            title="ChatATP is thinking...",
            message=f"AI{model_info} is processing your message",
            sound=True
        )

    def notify_ai_complete(self, model_name: str = ""):
        """Notify when AI response is complete"""
        model_info = f" ({model_name})" if model_name else ""
        return self.notify(
            title="Response ready!",
            message=f"ChatATP{model_info} has replied",
            sound=True
        )

    def notify_tool_start(self, tool_name: str):
        """Notify when a tool starts executing"""
        return self.notify(
            title=f"Running {tool_name}...",
            message=f"Tool execution in progress",
            sound=False  # Don't spam with sound for tools
        )

    def notify_tool_complete(self, tool_name: str, success: bool = True):
        """Notify when a tool completes"""
        status = "completed" if success else "failed"
        return self.notify(
            title=f"Tool {status}!",
            message=f"{tool_name} execution {status}",
            sound=not success  # Only sound on failure
        )

    def notify_error(self, error_message: str):
        """Notify on errors"""
        return self.notify(
            title="ChatATP Error",
            message=error_message[:100],  # Truncate long messages
            sound=True
        )


# Global notification manager instance
notification_manager = NotificationManager()
