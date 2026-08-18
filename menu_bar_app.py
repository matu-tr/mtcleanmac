#!/usr/bin/env python3
# Silkele
# Copyright (C) 2026 matu-tr
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

"""Silkele menu bar app: lives in the macOS status bar, cleans with one click."""
import threading

import rumps
from ServiceManagement import SMAppService

import silkele

SM_APP_SERVICE_STATUS_ENABLED = 1


class SilkeleApp(rumps.App):
    def __init__(self):
        super().__init__("🧹", quit_button="Quit")
        self.clean_item = rumps.MenuItem("Clean Now", callback=self.clean_now)
        self.login_item = rumps.MenuItem("Launch at Login", callback=self.toggle_login_item)
        self.login_item.state = self._login_item_enabled()
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
            for path in silkele.CLEANUP_PATHS:
                silkele.delete_contents(path)
            silkele.clean_snapshots()
        except Exception as e:
            error = str(e)
        finally:
            self._cleaning = False
            self.title = "🧹"
            self.clean_item.title = "Clean Now"
            self.clean_item.set_callback(self.clean_now)
            if error:
                rumps.notification("Silkele", "Error", error)
            else:
                rumps.notification("Silkele", "Done", "Cleanup finished ✅")

    def _login_item_enabled(self):
        try:
            return SMAppService.mainAppService().status() == SM_APP_SERVICE_STATUS_ENABLED
        except Exception:
            return False

    def toggle_login_item(self, sender):
        service = SMAppService.mainAppService()
        try:
            if self._login_item_enabled():
                ok, error = service.unregisterAndReturnError_(None)
            else:
                ok, error = service.registerAndReturnError_(None)
            if not ok:
                raise RuntimeError(str(error))
        except Exception as e:
            rumps.notification("Silkele", "Error", str(e))
        sender.state = self._login_item_enabled()


if __name__ == "__main__":
    SilkeleApp().run()
