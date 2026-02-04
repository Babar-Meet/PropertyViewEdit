from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QObject, Signal, QThread
from PySide6.QtGui import QIcon
import os
import fs_logic
from datetime import datetime

class TreeItem:
    def __init__(self, file_info: fs_logic.FileInfo, parent=None):
        self.file_info = file_info
        self.parent_item = parent
        self.child_items = []
        self._loaded = False

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return 5 # Name, Size, Type, Modified, Attributes

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def data(self, column):
        if column == 0:
            return self.file_info.name
        elif column == 1:
            if self.file_info.is_dir:
                return ""
            size = self.file_info.size
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:3.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        elif column == 2:
            if self.file_info.is_dir:
                return "Folder"
            _, ext = os.path.splitext(self.file_info.path)
            return f"{ext.upper()[1:]} File" if ext else "File"
        elif column == 3:
            dt = datetime.fromtimestamp(self.file_info.modified_time)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif column == 4:
            return "".join(self.file_info.attribute_strings)
        return None

class FileTreeModel(QAbstractItemModel):
    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        self.root_path = root_path
        root_info = fs_logic.FileInfo(root_path)
        self.root_item = TreeItem(root_info)
        self._load_children(self.root_item)

    def _load_children(self, item):
        if item.file_info.is_dir and not item._loaded:
            contents = fs_logic.get_directory_contents(item.file_info.path)
            # Sort: folders first, then names
            contents.sort(key=lambda x: (not x.is_dir, x.name.lower()))
            for info in contents:
                item.append_child(TreeItem(info, item))
            item._loaded = True

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if row < parent_item.child_count():
            child_item = parent_item.child(row)
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

        if parent_item == self.root_item or parent_item is None:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        if parent_item.file_info.is_dir and not parent_item._loaded:
            self._load_children(parent_item)

        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):
        return 5

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item.data(index.column())
        
        if role == Qt.DecorationRole and index.column() == 0:
            if item.file_info.is_dir:
                return QIcon.fromTheme("folder", QIcon())
            else:
                return QIcon.fromTheme("text-x-generic", QIcon())

        if role == Qt.TextAlignmentRole:
            if index.column() == 1: # Size right aligned
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            headers = ["Name", "Size", "Type", "Modified", "Attributes"]
            if 0 <= section < len(headers):
                return headers[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = super().flags(index)
        if index.column() == 0: # Name is editable
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            item = index.internalPointer()
            if index.column() == 0: # Rename
                try:
                    new_path = fs_logic.rename_file(item.file_info.path, value)
                    item.file_info = fs_logic.FileInfo(new_path)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    return True
                except Exception as e:
                    print(f"Rename failed: {e}")
                    return False
        return False

    def get_info(self, index):
        if not index.isValid():
            return None
        return index.internalPointer().file_info

    def refresh_item(self, index):
        """Notifies the view that an item has changed."""
        if not index.isValid():
            return
        
        # We need to emit for all columns of this row
        row = index.row()
        parent_index = index.parent()
        item = index.internalPointer()
        
        # Re-read basics
        try:
            item.file_info = fs_logic.FileInfo(item.file_info.path)
        except:
            pass # Maybe deleted?
        
        top_left = self.index(row, 0, parent_index)
        bottom_right = self.index(row, self.columnCount() - 1, parent_index)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
