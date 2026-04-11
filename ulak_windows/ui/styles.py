DARK_THEME = """
QMainWindow {
    background-color: #0a0e27;
}

QWidget {
    background-color: #0a0e27;
    color: #e8eaf6;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #b24bf3);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00fff9, stop:1 #ff2e97);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0099bb, stop:1 #8833cc);
}

QPushButton:disabled {
    background: #2d3462;
    color: #5a6080;
}

QPushButton#secondaryBtn {
    background: #1e234a;
    color: #00d4ff;
    border: 1px solid #00d4ff;
}

QPushButton#secondaryBtn:hover {
    background: #2d3462;
    color: #00fff9;
    border-color: #00fff9;
}

QPushButton#actionBtn {
    background: #1a73e8;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#actionBtn:hover {
    background: #1557b0;
}

QPushButton#actionBtn:pressed {
    background: #0d47a1;
}

QPushButton#linkBtn {
    background: #1a73e8;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#linkBtn:hover {
    background: #1557b0;
}

QListWidget {
    background-color: #141b40;
    border: 2px solid #00d4ff;
    border-radius: 12px;
    padding: 8px;
    outline: none;
}

QListWidget::item {
    background-color: #1e234a;
    border-radius: 8px;
    padding: 16px;
    margin: 4px;
    color: #e8eaf6;
    border: 1px solid #2d3462;
}

QListWidget::item:hover {
    background-color: #252d5c;
    border: 1px solid #00d4ff;
}

QListWidget::item:selected {
    background-color: rgba(0, 212, 255, 0.15);
    color: #00d4ff;
    border: 1px solid #00d4ff;
}

QLabel {
    color: #e8eaf6;
    background: transparent;
}

QProgressBar {
    border: 2px solid #00d4ff;
    border-radius: 8px;
    text-align: center;
    background-color: #141b40;
    color: #e8eaf6;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00d4ff, stop:1 #b24bf3);
    border-radius: 6px;
}

QScrollBar:vertical {
    background: #141b40;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #00d4ff;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #00fff9;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #141b40;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #00d4ff;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QTabWidget::pane {
    border: 2px solid #2d3462;
    border-radius: 0px;
    background-color: #0a0e27;
}

QTabBar::tab {
    background-color: #141b40;
    color: #8b949e;
    padding: 8px 12px;
    border: 1px solid #2d3462;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #1e234a;
    color: #00d4ff;
    border-color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}

QTabBar::tab:hover:!selected {
    background-color: #1e234a;
    color: #e8eaf6;
}

QLineEdit {
    background-color: #141b40;
    border: 1px solid #2d3462;
    border-radius: 8px;
    color: #e8eaf6;
    padding: 8px 12px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}

QLineEdit:focus {
    border: 1px solid #00d4ff;
    background-color: #1e234a;
}

QCheckBox {
    color: #e8eaf6;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #2d3462;
    background: #141b40;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00d4ff, stop:1 #b24bf3);
    border-color: #00d4ff;
}

QCheckBox::indicator:hover {
    border-color: #00d4ff;
}

QMessageBox {
    background-color: #141b40;
}

QMessageBox QLabel {
    color: #e8eaf6;
    background: transparent;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QFrame {
    background-color: #0a0e27;
}

QMenu {
    background-color: #141b40;
    border: 1px solid #00d4ff;
    border-radius: 8px;
    color: #e8eaf6;
}

QMenu::item:selected {
    background-color: rgba(0, 212, 255, 0.2);
    color: #00d4ff;
}

QTextEdit {
    background-color: #141b40;
    border: 1px solid #2d3462;
    border-radius: 8px;
    color: #e8eaf6;
    padding: 8px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}

QTextEdit:focus {
    border-color: #00d4ff;
}

QDialog {
    background-color: #141b40;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
    min-height: 32px;
}
"""
