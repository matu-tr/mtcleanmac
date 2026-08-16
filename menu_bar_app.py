#!/usr/bin/env python3
# MTCleanMac
# Copyright (C) 2026 Mansur Turasan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""MTCleanMac menu bar app: lives in the macOS status bar, cleans with one click."""
import os
import subprocess
import sys
import threading
from pathlib import Path

import rumps

import MTCleanMac

LOGIN_ITEM_LABEL = "com.mansur.mtcleanmac"
LOGIN_ITEM_PLIST = Path(f"~/Library/LaunchAgents/{LOGIN_ITEM_LABEL}.plist").expanduser()


def _login_item_program_args():
    if getattr(sys, "frozen", False):
        return [sys.executable]
    return [sys.executable, os.path.abspath(__file__)]


def _login_item_plist_contents():
    args = "".join(f"<string>{arg}</string>" for arg in _login_item_program_args())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n<dict>\n'
        f"    <key>Label</key>\n    <string>{LOGIN_ITEM_LABEL}</string>\n"
        f"    <key>ProgramArguments</key>\n    <array>{args}</array>\n"
        "    <key>RunAtLoad</key>\n    <true/>\n"
        "</dict>\n</plist>\n"
    )


class MTCleanMacApp(rumps.App):
    def __init__(self):
        super().__init__("🧹", quit_button="Quit")
        self.clean_item = rumps.MenuItem("Clean Now", callback=self.clean_now)
        self.login_item = rumps.MenuItem("Launch at Login", callback=self.toggle_login_item)
        self.login_item.state = LOGIN_ITEM_PLIST.exists()
        self.menu = [self.clean_item, None, self.login_item]
        self._cleaning = False

    def clean_now(self, sender):
        if self._cleaning:
            return
        self._cleaning = True
        self.title = "🧹⏳"
        self.clean_item.title = "Cleaning..."
        self.clean_item.set_callback(None)
        threading.Thread(target=self._run_cleanup, daemon=True).start()

    def _run_cleanup(self):
        error = None
        try:
            for path in MTCleanMac.CLEANUP_PATHS:
                MTCleanMac.delete_contents(path)
            MTCleanMac.clean_snapshots()
        except Exception as e:
            error = str(e)
        finally:
            self._cleaning = False
            self.title = "🧹"
            self.clean_item.title = "Clean Now"
            self.clean_item.set_callback(self.clean_now)
            if error:
                rumps.notification("MTCleanMac", "Error", error)
            else:
                rumps.notification("MTCleanMac", "Done", "Cleanup finished ✅")

    def toggle_login_item(self, sender):
        uid = os.getuid()
        if sender.state:
            subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(LOGIN_ITEM_PLIST)])
            LOGIN_ITEM_PLIST.unlink(missing_ok=True)
            sender.state = False
        else:
            LOGIN_ITEM_PLIST.parent.mkdir(parents=True, exist_ok=True)
            LOGIN_ITEM_PLIST.write_text(_login_item_plist_contents())
            subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(LOGIN_ITEM_PLIST)])
            sender.state = True


if __name__ == "__main__":
    MTCleanMacApp().run()
