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

import os
import subprocess
from datetime import datetime
from pathlib import Path

# iCloud Drive log path
ICLOUD_PATH = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/")
APP_DOCUMENTS_PATH = os.path.expanduser("~/Documents/AutomationLogs")  # Save log and DB in Documents
LOG_DIR = Path(os.path.join(APP_DOCUMENTS_PATH, "MTTimeMachineCleanup"))
LOG_FILE = Path(os.path.join(APP_DOCUMENTS_PATH, "MTTimeMachineCleanup", "snapshot_log.txt"))

def show_notification(title, message, subtitle=None, sound=None):
    """
    Show a native macOS notification with optional subtitle and sound.
    """
    try:
        script = f'display notification "{message.replace("\"", "\'")}" with title "{title}"'
        if subtitle:
            script += f' subtitle "{subtitle}"'
        if sound:
            script += f' sound name "{sound}"'
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        log(f"Notification failed: {e}")

def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")

def is_latest_backup_external():
    result = run_cmd(["tmutil", "latestbackup"])
    output = result.stdout.strip()
    if output.startswith("/Volumes/"):
        log(f"Latest backup found on external disk: {output}")
        return True
    else:
        log(f"Latest backup NOT found on external disk: '{output}'")
        return False

def get_local_snapshots():
    result = run_cmd(["tmutil", "listlocalsnapshots", "/"])
    snapshots = [
        line.strip() for line in result.stdout.splitlines()
        if line.strip().startswith("com.apple.TimeMachine")
    ]
    return snapshots

def delete_local_snapshots():
    log("Deleting all local snapshots...")
    result = run_cmd(["tmutil", "thinlocalsnapshots", "/", "9999999999999999", "4"])
    log("Deletion result:\n" + result.stdout + result.stderr)

def main():
    log("==== Snapshot Cleaner Started ====")
    show_notification(
        title="MTCleanMac",
        message="Snapshot Cleaner Started",
        subtitle="",
        sound="Glass"
    )
    snapshots = get_local_snapshots()
    if snapshots:
        log(f"{len(snapshots)} local snapshot(s) found:")
        for snap in snapshots:
            log(f"  - {snap}")

        if is_latest_backup_external():
            delete_local_snapshots()
        else:
            log("❌ Skipped deletion: Latest backup is not on external disk.")
    else:
        log("✅ No local snapshots found.")
    log("==== Snapshot Cleaner Finished ====\n")
    show_notification(
        title="MTCleanMac",
        message="Snapshot Cleaner Finished ✅",
        subtitle="",
        sound="Glass"
    )

if __name__ == "__main__":
    main()