# Time Weaver

## Setup (Build the Executable)

1. Download or clone the project
2. Double-click MakeExecutable.bat
3. Wait 2–5 minutes for the build to complete

After completion, the executable will be available at:
dist/TimeWeaver.exe

A portable folder is also created automatically for distribution.

Users only need to run the exe.
No Python, no Qt, no installation required.

---

## Description

Time Weaver is a Windows desktop application to view and modify real filesystem timestamps:
Creation Time, Modified Time, and Accessed Time.

It is built for accuracy, performance, and handling large directory structures on Windows.

---

## Features
- VS Code inspired dark UI
- Lazy-loading directory tree
- Native Windows API support for creation time
- Recursive timestamp updates
- Async filesystem operations
- Portable standalone executable

---

## Requirements (Build Only)
- Windows OS
- Python 3.9+

---

## Developer Usage (Optional)

pip install -r requirements.txt
python main.py

---

## Project Structure
- main.py – Entry point
- main_window.py – UI logic and styling
- tree_model.py – Lazy-loading filesystem tree model
- fs_logic.py – Native filesystem operations (Win32 API)
- build.py – Executable build logic
- MakeExecutable.bat – One-click setup and build script
