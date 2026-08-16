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
import shutil
import subprocess
from pathlib import Path
from pync import Notifier

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

def is_latest_backup_on_external_disk():
    try:
        result = subprocess.run(
            ["tmutil", "latestbackup"],
            capture_output=True, text=True
        )
        output = result.stdout.strip()
        if not output:
            print("⚠️ 'tmutil latestbackup' returned no result.")
            print("💡 Tip: If you're running this from VSCode, make sure Visual Studio Code has Full Disk Access.")
            return False
        elif output.startswith("/Volumes/"):
            print(f"✅ Latest backup is on external disk: {output}")
            return True
        else:
            print(f"⚠️ Latest backup is not on an external disk: {output}")
            return False
    except Exception as e:
        print(f"❌ Error checking latest backup: {e}")
        return False

def check_and_handle_snapshots():
    print("\n🕵️ Checking for local Time Machine snapshots...")
    try:
        result = subprocess.run(
            ["tmutil", "listlocalsnapshots", "/"],
            capture_output=True, text=True
        )
        snapshots = [
            line.strip() for line in result.stdout.splitlines()
            if line.strip().startswith("com.apple.TimeMachine")
        ]

        if not snapshots:
            print("✅ No local snapshots found.")
            return

        print("⚠️ Found local snapshots:")
        for s in snapshots:
            print(f"  - {s}")

        # Check if last full backup is on external drive
        print("\n💽 Verifying that the latest full backup is on an external disk...")
        if is_latest_backup_on_external_disk():
            choice = input("\n🧹 Do you want to delete all local snapshots? (y/n): ").lower()
            if choice in ["y", "yes"]:
                print("🧨 Deleting local snapshots...")
                subprocess.run([
                    "sudo", "tmutil", "thinlocalsnapshots", "/", "9999999999999999", "4"
                ])
                print("✅ Snapshots deleted.")
            else:
                print("⏭️ Skipping snapshot deletion.")
        else:
            print("🚫 Cannot delete local snapshots safely – no external backup found.")

    except Exception as e:
        print(f"❌ Failed to check snapshots: {e}")

def main():
    print("🧹 Starting macOS user-level cleanup...")
    try:
        try:
            Notifier.notify("🧹 MTCleanMac cleanup started.", title="MTCleanMac")
        except Exception:
            pass
        for path in CLEANUP_PATHS:
            delete_contents(path)
        check_and_handle_snapshots()
        try:
            Notifier.notify("🎉 MTCleanMac cleanup complete.", title="MTCleanMac", sound="default")
        except Exception:
            pass
    except Exception as e:
        try:
            Notifier.notify(f"❌ MTCleanMac error: {e}", title="MTCleanMac", sound="default")
        except Exception:
            pass
        raise

if __name__ == "__main__":
    main()