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
