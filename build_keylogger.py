import PyInstaller.__main__
import os
import shutil
from datetime import datetime

# Configuration
APP_NAME = "TypingLogger"
SCRIPT_FILE = "word_keylogger.py"  # Save the previous code with this filename
ICON_FILE = None  # Optional: "app_icon.ico" for a custom icon
ADD_DATA = []  # Optional: [("assets", "assets")] to include additional files
ONE_FILE = True  # False to create a folder instead of single executable
CONSOLE = False  # Set to True to show console window

# Prepare build command
build_date = datetime.now().strftime("%Y-%m-%d")
build_command = [
    SCRIPT_FILE,
    "--name", f"{APP_NAME}_{build_date}",
    "--clean",
    "--noconfirm"
]

if ONE_FILE:
    build_command.append("--onefile")
    
if not CONSOLE:
    build_command.append("--windowed")
    
if ICON_FILE and os.path.exists(ICON_FILE):
    build_command.extend(["--icon", ICON_FILE])
    
for src, dest in ADD_DATA:
    build_command.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

# Run PyInstaller
print("Building executable...")
PyInstaller.__main__.run(build_command)

print("\nBuild completed! Executable is in the 'dist' folder.")