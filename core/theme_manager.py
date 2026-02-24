import json
import os
import copy

DEFAULT_THEME = {
    "colors": {
        "window_bg": "#2b2b2b",
        "text": "#ffffff",
        "label_text": "#cccccc",
        "input_bg": "#3c3f41",
        "input_border": "#555555",
        "input_border_focus": "#3a96dd",
        "button_bg": "#3a96dd",
        "button_text": "#ffffff",
        "button_hover": "#2b86cd",
        "button_pressed": "#1a76bd",
        "stop_btn_bg": "#d32f2f",
        "stop_btn_hover": "#f44336",
        "stop_btn_pressed": "#b71c1c",
        "list_bg": "#3c3f41",
        "list_item_selected": "#3a96dd"
    },
    "fonts": {
        "family": "Segoe UI",
        "size": "14px"
    },
    "sizes": {
        "border_radius": "4px",
        "input_padding": "5px",
        "btn_padding": "8px 16px"
    }
}

class ThemeManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.theme = copy.deepcopy(DEFAULT_THEME)
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded = json.load(f)
                    # Merge with default to ensure all keys exist
                    self.merge_defaults(loaded, self.theme)
            except Exception as e:
                print(f"Error loading theme: {e}")
                self.theme = copy.deepcopy(DEFAULT_THEME)
        else:
            self.theme = copy.deepcopy(DEFAULT_THEME)

    def merge_defaults(self, source, target):
        for key, value in source.items():
            if isinstance(value, dict) and key in target:
                self.merge_defaults(value, target[key])
            else:
                target[key] = value

    def save(self, theme_data):
        self.theme = theme_data
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.theme, f, indent=4)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def get_theme(self):
        return self.theme

    def get_stylesheet(self):
        c = self.theme["colors"]
        f = self.theme["fonts"]
        s = self.theme["sizes"]
        
        return f"""
QMainWindow {{
    background-color: {c['window_bg']};
    color: {c['text']};
}}

QWidget {{
    background-color: {c['window_bg']};
    color: {c['text']};
    font-family: '{f['family']}', sans-serif;
    font-size: {f['size']};
}}

QLabel {{
    color: {c['label_text']};
}}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {c['input_bg']};
    border: 1px solid {c['input_border']};
    border-radius: {s['border_radius']};
    padding: {s['input_padding']};
    color: {c['text']};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {c['input_border_focus']};
}}

QPushButton {{
    background-color: {c['button_bg']};
    color: {c['button_text']};
    border: none;
    border-radius: {s['border_radius']};
    padding: {s['btn_padding']};
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {c['button_hover']};
}}

QPushButton:pressed {{
    background-color: {c['button_pressed']};
}}

QPushButton#btn_stop {{
    background-color: {c['stop_btn_bg']};
    color: {c['button_text']};
    border: none;
    border-radius: {s['border_radius']};
    padding: {s['btn_padding']};
    font-weight: bold;
}}

QPushButton#btn_stop:hover {{
    background-color: {c['stop_btn_hover']};
    border: 1px solid #ffcdd2;
}}

QPushButton#btn_stop:pressed {{
    background-color: {c['stop_btn_pressed']};
}}

QListWidget {{
    background-color: {c['list_bg']};
    border: 1px solid {c['input_border']};
    border-radius: {s['border_radius']};
}}

QListWidget::item {{
    padding: 8px;
}}

QListWidget::item:selected {{
    background-color: {c['list_item_selected']};
    color: {c['button_text']};
}}

QGroupBox {{
    border: 1px solid {c['input_border']};
    border-radius: {s['border_radius']};
    margin-top: 20px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
    color: {c['label_text']};
}}
"""
