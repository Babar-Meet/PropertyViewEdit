import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QTreeView, QPushButton, QLabel, QDateTimeEdit, 
                              QCheckBox, QFileDialog, QFrame, QSplitter, QHeaderView,
                              QScrollArea, QLineEdit, QFormLayout, QTabWidget,
                              QProgressBar)
from PySide6.QtCore import Qt, QDateTime, Signal, QThread, QSize, QTimer
from PySide6.QtGui import QIcon, QColor, QPalette, QFont
import fs_logic
import tree_model
from datetime import datetime
import os
import win32con

STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    color: #cccccc;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}

QTreeView {
    background-color: #252526;
    border: none;
    outline: none;
    selection-background-color: #37373d;
    selection-color: #ffffff;
    alternate-background-color: #2a2a2a;
}

QTreeView::item {
    padding: 6px;
    border-bottom: 1px solid #333333;
}

QTreeView::item:hover {
    background-color: #2a2d2e;
}

QTreeView::item:selected {
    background-color: #37373d;
    color: white;
}

QHeaderView::section {
    background-color: #252526;
    color: #858585;
    padding: 4px;
    border: none;
    border-bottom: 1px solid #333333;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}

QSplitter::handle {
    background-color: #333333;
    width: 1px;
}

#DetailsPanel {
    background-color: #1e1e1e;
}

#Header {
    font-weight: bold;
    font-size: 16px;
    color: #ffffff;
    padding: 0px 0px 10px 0px;
}

#SubHeader {
    font-weight: bold;
    font-size: 12px;
    color: #007acc;
    text-transform: uppercase;
    margin-top: 20px;
}

QLabel#PathLabel {
    color: #858585;
    font-size: 11px;
    padding: 5px;
    background-color: #252526;
    border-radius: 4px;
}

QPushButton {
    background-color: #0e639c;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:disabled {
    background-color: #333333;
    color: #666666;
}

QDateTimeEdit, QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #3c3c3c;
    padding: 6px;
    color: white;
    border-radius: 2px;
}

QDateTimeEdit:focus, QLineEdit:focus {
    border: 1px solid #007acc;
}

QTabWidget::pane {
    border-top: 1px solid #333333;
}

QTabBar::tab {
    background: #1e1e1e;
    color: #858585;
    padding: 8px 16px;
    border-bottom: 1px solid transparent;
}

QTabBar::tab:selected {
    color: #ffffff;
    border-bottom: 2px solid #007acc;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #333333;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #444444;
}
"""

class PropLoadWorker(QThread):
    finished = Signal(object)
    
    def __init__(self, file_info):
        super().__init__()
        self.file_info = file_info
        
    def run(self):
        self.file_info.load_extended_properties()
        self.finished.emit(self.file_info)

class SaveWorker(QThread):
    finished = Signal(bool, str)
    
    def __init__(self, path, ctime, mtime, atime, attributes, recursive):
        super().__init__()
        self.path = path
        self.ctime = ctime
        self.mtime = mtime
        self.atime = atime
        self.attributes = attributes
        self.recursive = recursive
        
    def run(self):
        try:
            # Update timestamps
            fs_logic.update_timestamps(self.path, self.ctime, self.mtime, self.atime, self.recursive)
            
            # Update attributes (standard)
            if self.attributes is not None:
                fs_logic.set_attributes(self.path, self.attributes)
                
            self.finished.emit(True, "Changes applied successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limitless File Metadata Editor")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
        self.selected_info = None
        self.selected_index = None
        self.model = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Compact Toolbar (Always Top) ---
        self.toolbar_widget = QWidget()
        self.toolbar_widget.setStyleSheet("background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c;")
        self.toolbar_widget.setFixedHeight(35)
        toolbar_layout = QHBoxLayout(self.toolbar_widget)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)
        toolbar_layout.setSpacing(10)

        self.btn_open = QPushButton("Open Folder")
        self.btn_open.setFixedSize(90, 24)
        self.btn_open.setStyleSheet("font-size: 11px; background-color: #0e639c;")
        self.btn_open.clicked.connect(self.on_open_folder)
        toolbar_layout.addWidget(self.btn_open)

        toolbar_layout.addStretch()
        
        self.lbl_global_status = QLabel("Ready")
        self.lbl_global_status.setStyleSheet("color: #858585; font-size: 11px;")
        toolbar_layout.addWidget(self.lbl_global_status)

        self.main_layout.addWidget(self.toolbar_widget)

        # --- Content Area ---
        from PySide6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget()
        
        # Page 0: Placeholder
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        
        msg = QLabel("SELECT A FOLDER TO START EDITING")
        msg.setStyleSheet("color: #444444; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        placeholder_layout.addWidget(msg)
        self.stack.addWidget(self.placeholder_widget)

        # Page 1: Main Content
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # Left: Tree
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setMinimumWidth(300)
        self.splitter.addWidget(self.tree_view)
        
        # Right: Details
        self.details_container = QFrame()
        self.details_container.setObjectName("DetailsPanel")
        self.details_container.setMinimumWidth(400)
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)
        
        self.tabs = QTabWidget()
        
        # Tab 1: General & Edit
        self.tab_general = QWidget()
        gen_layout = QVBoxLayout(self.tab_general)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QFormLayout(scroll_content)
        self.form_layout.setSpacing(15)
        
        self.lbl_head = QLabel("Metadata Overview")
        self.lbl_head.setObjectName("Header")
        self.form_layout.addRow(self.lbl_head)
        
        self.lbl_path = QLabel("Select an item to view")
        self.lbl_path.setObjectName("PathLabel")
        self.lbl_path.setWordWrap(True)
        self.form_layout.addRow(self.lbl_path)
        
        self.form_layout.addRow(QLabel(""), QLabel("")) 
        
        self.dt_creation = QDateTimeEdit()
        self.dt_creation.setCalendarPopup(True)
        self.form_layout.addRow("Created:", self.dt_creation)
        
        self.dt_modified = QDateTimeEdit()
        self.dt_modified.setCalendarPopup(True)
        self.form_layout.addRow("Modified:", self.dt_modified)
        
        self.dt_accessed = QDateTimeEdit()
        self.dt_accessed.setCalendarPopup(True)
        self.form_layout.addRow("Accessed:", self.dt_accessed)
        
        self.form_layout.addRow(QLabel(""), QLabel(""))
        attr_container = QWidget()
        attr_layout = QHBoxLayout(attr_container)
        attr_layout.setContentsMargins(0, 0, 0, 0)
        self.cb_readonly = QCheckBox("Read-only")
        self.cb_hidden = QCheckBox("Hidden")
        self.cb_system = QCheckBox("System")
        self.cb_archive = QCheckBox("Archive")
        attr_layout.addWidget(self.cb_readonly)
        attr_layout.addWidget(self.cb_hidden)
        attr_layout.addWidget(self.cb_system)
        attr_layout.addWidget(self.cb_archive)
        self.form_layout.addRow("Flags:", attr_container)
        
        self.cb_recursive = QCheckBox("Apply recursively")
        self.form_layout.addRow("", self.cb_recursive)
        
        self.btn_save = QPushButton("Apply Changes")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.on_save)
        self.form_layout.addRow("", self.btn_save)
        
        scroll_area.setWidget(scroll_content)
        gen_layout.addWidget(scroll_area)
        
        # Tab 2: All Properties
        self.tab_all_props = QWidget()
        all_props_layout = QVBoxLayout(self.tab_all_props)
        all_props_layout.setContentsMargins(10, 10, 10, 10)
        
        self.prop_search = QLineEdit()
        self.prop_search.setPlaceholderText("Search properties...")
        self.prop_search.textChanged.connect(self.filter_properties)
        all_props_layout.addWidget(self.prop_search)
        
        self.prop_scroll = QScrollArea()
        self.prop_scroll.setWidgetResizable(True)
        self.prop_container = QWidget()
        self.prop_form = QFormLayout(self.prop_container)
        self.prop_scroll.setWidget(self.prop_container)
        all_props_layout.addWidget(self.prop_scroll)
        
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_all_props, "All Properties")
        details_layout.addWidget(self.tabs)
        
        self.splitter.addWidget(self.details_container)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)
        content_layout.addWidget(self.splitter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setFixedHeight(2)
        content_layout.addWidget(self.progress)
        
        self.stack.addWidget(self.content_widget)
        self.main_layout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0) # Start with placeholder

    def on_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if folder:
            self.lbl_global_status.setText("Loading...")
            self.model = tree_model.FileTreeModel(folder)
            self.tree_view.setModel(self.model)
            self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
            
            # Switch view
            self.stack.setCurrentIndex(1)
            
            self.lbl_path.setText(folder)
            self.tree_view.expandToDepth(0)
            self.lbl_global_status.setText("Ready")
            
    def on_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            return
            
        index = indexes[0]
        self.selected_index = index
        info = self.model.get_info(index)
        if info:
            self.selected_info = info
            self.update_details_ui(info)
            # Load extended properties in background
            self.load_extended_properties(info)

    def update_details_ui(self, info):
        self.lbl_head.setText(info.name)
        self.lbl_path.setText(info.path)
        
        self.dt_creation.setDateTime(QDateTime.fromSecsSinceEpoch(int(info.creation_time)))
        self.dt_modified.setDateTime(QDateTime.fromSecsSinceEpoch(int(info.modified_time)))
        self.dt_accessed.setDateTime(QDateTime.fromSecsSinceEpoch(int(info.accessed_time)))
        
        # Update attributes checkboxes
        self.cb_readonly.setChecked(bool(info.attributes & win32con.FILE_ATTRIBUTE_READONLY))
        self.cb_hidden.setChecked(bool(info.attributes & win32con.FILE_ATTRIBUTE_HIDDEN))
        self.cb_system.setChecked(bool(info.attributes & win32con.FILE_ATTRIBUTE_SYSTEM))
        self.cb_archive.setChecked(bool(info.attributes & win32con.FILE_ATTRIBUTE_ARCHIVE))
        
        self.cb_recursive.setEnabled(info.is_dir)
        if not info.is_dir:
            self.cb_recursive.setChecked(False)
            
        self.btn_save.setEnabled(True)
        
        # Clear prop tab until loaded
        self.clear_prop_form()
        if info.all_properties_loaded:
            self.fill_prop_form(info.properties)
        else:
            self.prop_form.addRow(QLabel("Loading all OS properties..."), QLabel(""))

    def load_extended_properties(self, info):
        if info.all_properties_loaded:
            return
            
        self.progress.setVisible(True)
        self.prop_worker = PropLoadWorker(info)
        self.prop_worker.finished.connect(self.on_props_loaded)
        self.prop_worker.start()

    def on_props_loaded(self, info):
        self.progress.setVisible(False)
        if self.selected_info == info:
            self.fill_prop_form(info.properties)

    def clear_prop_form(self):
        while self.prop_form.count():
            child = self.prop_form.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def fill_prop_form(self, props):
        self.clear_prop_form()
        # Sort properties by name
        sorted_keys = sorted(props.keys())
        for key in sorted_keys:
            val = props[key]
            lbl_key = QLabel(f"<b>{key}</b>")
            lbl_val = QLineEdit(str(val))
            lbl_val.setReadOnly(True) 
            lbl_val.setStyleSheet("background: transparent; border: none; color: #aaa;")
            self.prop_form.addRow(lbl_key, lbl_val)

    def filter_properties(self, text):
        text = text.lower()
        for i in range(self.prop_form.count()):
            item = self.prop_form.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Row consists of 2 widgets usually.
                row_idx, role = self.prop_form.getWidgetPosition(widget)
                
                # Check if this widget or its partner matches
                label_widget = self.prop_form.itemAt(row_idx, QFormLayout.LabelRole).widget()
                field_widget = self.prop_form.itemAt(row_idx, QFormLayout.FieldRole).widget()
                
                matches = text in label_widget.text().lower() or (field_widget and text in field_widget.text().lower())
                label_widget.setVisible(matches)
                field_widget.setVisible(matches)

    def on_save(self):
        if not self.selected_info:
            return
            
        ctime = self.dt_creation.dateTime().toSecsSinceEpoch()
        mtime = self.dt_modified.dateTime().toSecsSinceEpoch()
        atime = self.dt_accessed.dateTime().toSecsSinceEpoch()
        
        # Calculate attributes bitmask
        attrs = 0
        if self.cb_readonly.isChecked(): attrs |= win32con.FILE_ATTRIBUTE_READONLY
        if self.cb_hidden.isChecked(): attrs |= win32con.FILE_ATTRIBUTE_HIDDEN
        if self.cb_system.isChecked(): attrs |= win32con.FILE_ATTRIBUTE_SYSTEM
        if self.cb_archive.isChecked(): attrs |= win32con.FILE_ATTRIBUTE_ARCHIVE
        
        recursive = self.cb_recursive.isChecked()
        
        self.btn_save.setEnabled(False)
        self.lbl_global_status.setText("Working...")
        
        self.save_worker = SaveWorker(self.selected_info.path, ctime, mtime, atime, attrs, recursive)
        self.save_worker.finished.connect(self.on_save_finished)
        self.save_worker.start()
        
    def on_save_finished(self, success, message):
        self.btn_save.setEnabled(True)
        self.lbl_global_status.setText(message)
        if success:
            # Refresh the model item to show changes in tree
            if self.selected_index:
                self.model.refresh_item(self.selected_index)
                # Re-select to update details (model.refresh_item creates new FileInfo)
                self.update_details_ui(self.model.get_info(self.selected_index))
