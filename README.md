# Time Weaver

A premium desktop application to view and modify real filesystem timestamps (Creation, Modified, Accessed) dynamically on Windows.

## Features
- **VS Code Inspired UI**: Clean dark theme with a sidebar tree view and details editor.
- **Lazy Loading Tree**: Efficiently handles large directories by loading children only when expanded.
- **Native Windows Support**: Uses Windows APIs to correctly modify **Creation Time**.
- **Recursive Updates**: Option to apply timestamp changes to all nested files and folders.
- **Async Execution**: Filesystem operations run in background threads to keep the UI responsive.

## Requirements
- Python 3.9+
- Windows OS (for creation time support)

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the application:
```bash
python main.py
```

## Structure
- `main.py`: Entry point.
- `main_window.py`: PySide6 UI logic and styling.
- `tree_model.py`: Custom lazy-loading QAbstractItemModel.
- `fs_logic.py`: Native filesystem operations (Win32 API).
