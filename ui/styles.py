DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

QLabel {
    color: #cccccc;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #3c3f41;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #3a96dd;
}

QPushButton {
    background-color: #3a96dd;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2b86cd;
}

QPushButton:pressed {
    background-color: #1a76bd;
}

QPushButton#btn_stop {
    background-color: #d32f2f;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton#btn_stop:hover {
    background-color: #f44336;
    border: 1px solid #ffcdd2;
}

QPushButton#btn_stop:pressed {
    background-color: #b71c1c;
}

QListWidget {
    background-color: #3c3f41;
    border: 1px solid #555555;
    border-radius: 4px;
}

QListWidget::item {
    padding: 8px;
}

QListWidget::item:selected {
    background-color: #3a96dd;
    color: white;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 4px;
    margin-top: 20px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
    color: #aaaaaa;
}
"""
