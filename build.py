"""
Build script to create a standalone executable for TimeWeaver.
Run: python build.py
"""
import os
import sys
import subprocess
import shutil

def run_command(cmd):
    """Run a shell command and print output."""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode

def main():
    print("=" * 60)
    print("Building TimeWeaver Standalone Executable")
    print("=" * 60)
    
    # Clean previous builds
    print("\n[1/4] Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    if os.path.exists('TimeWeaver.spec'):
        os.remove('TimeWeaver.spec')
    
    # Install PyInstaller if not present
    print("\n[2/4] Checking/installing PyInstaller...")
    run_command(f'"{sys.executable}" -m pip install pyinstaller')
    
    # Create the executable
    print("\n[3/4] Building executable (this may take a few minutes)...")
    
    # Critical: Include all hidden imports and ensure Qt files are included
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=TimeWeaver',
        '--icon=NONE',  # Change to "icon.ico" if you have one
        '--add-data=*.py;.',  # Include all Python files
        '--hidden-import=win32timezone',
        '--hidden-import=win32com',
        '--hidden-import=pythoncom',
        '--hidden-import=PySide6.QtXml',
        '--hidden-import=PySide6.QtSvg',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--clean',  # Clean PyInstaller cache
        'main.py'
    ]
    
    result = run_command(' '.join(cmd))
    
    if result != 0:
        print("\n[ERROR] Build failed!")
        sys.exit(1)
    
    # Test the executable
    print("\n[4/4] Testing the executable...")
    exe_path = os.path.join('dist', 'TimeWeaver.exe')
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n✅ SUCCESS: Created {exe_path}")
        print(f"   Size: {size_mb:.1f} MB")
        
        # Create a simple test script
        print("\nTo test on another machine:")
        print(f"1. Copy '{exe_path}' to the target machine")
        print("2. Double-click it to run")
        print("3. No Python, Qt, or any dependencies needed!")
    else:
        print(f"\n❌ ERROR: {exe_path} not created!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Build complete! The executable is ready for distribution.")
    print("=" * 60)

if __name__ == "__main__":
    main()