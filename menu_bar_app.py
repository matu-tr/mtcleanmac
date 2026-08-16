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
import threading

import rumps

import MTCleanMac


class MTCleanMacApp(rumps.App):
    def __init__(self):
        super().__init__("🧹", quit_button="Quit")
        self.clean_item = rumps.MenuItem("Clean Now", callback=self.clean_now)
        self.menu = [self.clean_item]
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


if __name__ == "__main__":
    MTCleanMacApp().run()
