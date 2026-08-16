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

"""py2app build script. Usage: python3 setup.py py2app"""
from pathlib import Path
from setuptools import setup

VERSION = Path(__file__).parent.joinpath("VERSION").read_text().strip()

APP = ["menu_bar_app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "MTCleanMac",
        "CFBundleDisplayName": "MTCleanMac",
        "CFBundleIdentifier": "com.mansur.mtcleanmac",
        "CFBundleVersion": VERSION,
        "CFBundleShortVersionString": VERSION,
        "LSUIElement": True,  # menu bar agent: no Dock icon, no app switcher entry
        "NSHumanReadableCopyright": "Copyright (C) 2026 Mansur Turasan",
    },
    "packages": ["rumps"],
}

setup(
    app=APP,
    name="MTCleanMac",
    version=VERSION,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
