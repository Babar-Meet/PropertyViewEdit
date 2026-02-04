import os
import time
import win32file
import win32con
import win32api
import win32com.client
from datetime import datetime
from typing import Optional, List, Dict, Any

# FileInfo class captures both core and extended OS properties
class FileInfo:
    def __init__(self, path: str, fast_load: bool = True):
        self.path = path
        self.name = os.path.basename(path) or path
        self.is_dir = os.path.isdir(path)
        self.exists = os.path.exists(path)
        
        # Core stats (fast)
        try:
            stats = os.stat(path)
            self.creation_time = stats.st_ctime
            self.modified_time = stats.st_mtime
            self.accessed_time = stats.st_atime
            self.size = stats.st_size
            self.attributes = win32api.GetFileAttributes(path)
        except Exception:
            self.creation_time = 0
            self.modified_time = 0
            self.accessed_time = 0
            self.size = 0
            self.attributes = 0

        # Extended properties (lazy loaded)
        self.properties: Dict[str, Any] = {}
        self.all_properties_loaded = False

    def load_extended_properties(self):
        """Loads all available shell properties for this file."""
        if self.all_properties_loaded:
            return

        try:
            import pythoncom
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("Shell.Application")
            
            folder_path = os.path.dirname(os.path.abspath(self.path))
            file_name = os.path.basename(self.path)
            
            folder = shell.NameSpace(folder_path)
            if not folder:
                return
                
            item = folder.ParseName(file_name)
            if not item:
                return

            # Fetch properties
            for i in range(320):
                name = folder.GetDetailsOf(None, i)
                if not name:
                    continue
                val = folder.GetDetailsOf(item, i)
                if val:
                    self.properties[name] = val
            
            self.all_properties_loaded = True
        except Exception as e:
            print(f"Error loading extended properties: {e}")
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass

    @property
    def attribute_strings(self) -> List[str]:
        attrs = []
        mapping = {
            win32con.FILE_ATTRIBUTE_READONLY: 'R',
            win32con.FILE_ATTRIBUTE_HIDDEN: 'H',
            win32con.FILE_ATTRIBUTE_SYSTEM: 'S',
            win32con.FILE_ATTRIBUTE_ARCHIVE: 'A',
            win32con.FILE_ATTRIBUTE_COMPRESSED: 'C',
            win32con.FILE_ATTRIBUTE_ENCRYPTED: 'E',
        }
        for attr, char in mapping.items():
            if self.attributes & attr:
                attrs.append(char)
        return attrs

def get_directory_contents(path: str) -> List[FileInfo]:
    try:
        entries = os.listdir(path)
        return [FileInfo(os.path.join(path, entry)) for entry in entries]
    except PermissionError:
        return []
    except Exception:
        return []

def update_timestamps(path: str, ctime: Optional[float] = None, mtime: Optional[float] = None, atime: Optional[float] = None, recursive: bool = False):
    """
    Updates timestamps for a file or directory.
    ctime, mtime, atime are unix timestamps.
    """
    def _update_single(p: str):
        try:
            # For os.utime, we need to pass None if we don't want to change it, 
            # but it only accepts (atime, mtime). So we have to get current if one is missing.
            current_stats = os.stat(p)
            new_atime = atime if atime is not None else current_stats.st_atime
            new_mtime = mtime if mtime is not None else current_stats.st_mtime
            
            os.utime(p, (new_atime, new_mtime))
            
            # Update Creation time using Windows API
            if os.name == 'nt' and ctime is not None:
                handle = win32file.CreateFile(
                    p,
                    win32con.GENERIC_WRITE,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                    None,
                    win32con.OPEN_EXISTING,
                    win32con.FILE_FLAG_BACKUP_SEMANTICS,
                    None
                )
                
                dt_c = datetime.fromtimestamp(ctime)
                # If we only want to set creation time, we can pass None for others to SetFileTime
                # but it's safer to pass what we have.
                win32file.SetFileTime(handle, dt_c, None, None)
                handle.close()
        except Exception as e:
            print(f"Error setting timestamps for {p}: {e}")
            raise e

    if recursive and os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in dirs + files:
                _update_single(os.path.join(root, name))
        _update_single(path)
    else:
        _update_single(path)

def rename_file(old_path: str, new_name: str) -> str:
    """Renames a file and returns the new full path."""
    try:
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        return new_path
    except Exception as e:
        print(f"Error renaming {old_path}: {e}")
        raise e

def set_attributes(path: str, attributes: int):
    """Sets Windows file attributes."""
    try:
        # Check if we can write
        if not os.access(path, os.W_OK):
             # Try to unset read-only first if we're trying to set something else?
             # No, let's just try and catch.
             pass
        win32api.SetFileAttributes(path, attributes)
    except Exception as e:
        if "Access is denied" in str(e):
            raise Exception(f"Permission Denied: Try running as Administrator.")
        print(f"Error setting attributes for {path}: {e}")
        raise e
