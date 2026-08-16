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

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# List of user-level directories to clean
CLEANUP_PATHS = [
    "~/Library/Caches",
    "~/Library/Logs",
    "~/Library/Containers/com.apple.mail/Data/Library/Mail Downloads",
    "~/Library/Logs/DiagnosticReports",
    "~/Library/Developer/Xcode/DerivedData",
    "~/Library/Developer/Xcode/Archives",
    "~/Library/Developer/CoreSimulator"
]

LOG_DIR = Path("~/Documents/AutomationLogs/MTTimeMachineCleanup").expanduser()
LOG_FILE = LOG_DIR / "snapshot_log.txt"


def delete_contents(folder_path):
    folder = Path(folder_path).expanduser()
    if folder.exists() and folder.is_dir():
        print(f"\n🔍 Cleaning: {folder}")
        try:
            for item in folder.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    print(f"✅ Deleted: {item}")
                except Exception as e:
                    print(f"❌ Error deleting {item}: {e}")
        except PermissionError:
            print(f"⛔ Skipped (Permission Denied): {folder}")
        except Exception as e:
            print(f"❌ Error accessing {folder}: {e}")
    else:
        print(f"⛔ Folder not found or inaccessible: {folder}")


def _log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")


def _run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def _is_latest_backup_external():
    result = _run_cmd(["tmutil", "latestbackup"])
    output = result.stdout.strip()
    if output.startswith("/Volumes/"):
        _log(f"Latest backup found on external disk: {output}")
        return True
    else:
        _log(f"Latest backup NOT found on external disk: '{output}'")
        return False


def _get_local_snapshots():
    result = _run_cmd(["tmutil", "listlocalsnapshots", "/"])
    return [
        line.strip() for line in result.stdout.splitlines()
        if line.strip().startswith("com.apple.TimeMachine")
    ]


def _delete_local_snapshots():
    _log("Deleting all local snapshots...")
    result = _run_cmd(["tmutil", "thinlocalsnapshots", "/", "9999999999999999", "4"])
    _log("Deletion result:\n" + result.stdout + result.stderr)


def clean_snapshots():
    """Delete local Time Machine snapshots, but only if the latest backup is confirmed on an external disk."""
    _log("==== Snapshot cleanup started ====")
    snapshots = _get_local_snapshots()
    if snapshots:
        _log(f"{len(snapshots)} local snapshot(s) found:")
        for snap in snapshots:
            _log(f"  - {snap}")
        if _is_latest_backup_external():
            _delete_local_snapshots()
        else:
            _log("Skipped deletion: latest backup is not on an external disk.")
    else:
        _log("No local snapshots found.")
    _log("==== Snapshot cleanup finished ====\n")
