from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QColorDialog, QScrollArea, QWidget, 
                             QFormLayout, QLineEdit, QTabWidget)
from PyQt5.QtCore import Qt
import copy

class ColorButton(QPushButton):
    def __init__(self, color_hex, parent=None):
        super().__init__(parent)
        self.color_hex = color_hex
        self.update_style()
        self.clicked.connect(self.pick_color)

    def update_style(self):
        self.setStyleSheet(f"background-color: {self.color_hex}; border: 1px solid #555;")
        self.setText(self.color_hex)

    def pick_color(self):
        color = QColorDialog.getColor(initial=Qt.white, parent=self, title="Pick Color")
        if color.isValid():
            self.color_hex = color.name()
            self.update_style()

    def get_color(self):
        return self.color_hex

class ThemeEditorDialog(QDialog):
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_theme = copy.deepcopy(theme_manager.get_theme())
        self.setWindowTitle("Theme Editor")
        self.resize(600, 500)
        
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.color_inputs = {}
        self.font_inputs = {}
        self.size_inputs = {}
        
        self.init_colors_tab()
        self.init_fonts_tab()
        self.init_sizes_tab()
        
        btn_box = QHBoxLayout()
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_theme)
        self.btn_save = QPushButton("Save & Close")
        self.btn_save.clicked.connect(self.save_theme)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset = QPushButton("Reset Defaults")
        self.btn_reset.clicked.connect(self.reset_defaults)
        
        btn_box.addWidget(self.btn_reset)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_apply)
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        
        self.layout.addLayout(btn_box)

    def init_colors_tab(self):
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        form = QFormLayout(content)
        
        for key, val in self.current_theme["colors"].items():
            btn = ColorButton(val)
            form.addRow(key.replace("_", " ").title() + ":", btn)
            self.color_inputs[key] = btn
            
        scroll.setWidget(content)
        layout = QVBoxLayout(tab)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "Colors")

    def init_fonts_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        
        for key, val in self.current_theme["fonts"].items():
            inp = QLineEdit(str(val))
            form.addRow(key.replace("_", " ").title() + ":", inp)
            self.font_inputs[key] = inp
            
        self.tabs.addTab(tab, "Fonts")

    def init_sizes_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        
        for key, val in self.current_theme["sizes"].items():
            inp = QLineEdit(str(val))
            form.addRow(key.replace("_", " ").title() + ":", inp)
            self.size_inputs[key] = inp
            
        self.tabs.addTab(tab, "Sizes")

    def collect_data(self):
        new_theme = copy.deepcopy(self.current_theme)
        
        for key, btn in self.color_inputs.items():
            new_theme["colors"][key] = btn.get_color()
            
        for key, inp in self.font_inputs.items():
            new_theme["fonts"][key] = inp.text()
            
        for key, inp in self.size_inputs.items():
            new_theme["sizes"][key] = inp.text()
            
        return new_theme

    def apply_theme(self):
        theme = self.collect_data()
        self.theme_manager.theme = theme # Update manager state temporarily
        # Trigger parent update if possible
        if self.parent():
            if hasattr(self.parent(), "apply_theme"):
                self.parent().apply_theme()
            elif hasattr(self.parent(), "setStyleSheet"):
                self.parent().setStyleSheet(self.theme_manager.get_stylesheet())

    def save_theme(self):
        theme = self.collect_data()
        self.theme_manager.save(theme)
        self.apply_theme()
        self.accept()

    def reset_defaults(self):
        from core.theme_manager import DEFAULT_THEME
        self.current_theme = copy.deepcopy(DEFAULT_THEME)
        
        # Refresh UI
        for key, btn in self.color_inputs.items():
            if key in self.current_theme["colors"]:
                btn.color_hex = self.current_theme["colors"][key]
                btn.update_style()
                
        for key, inp in self.font_inputs.items():
            if key in self.current_theme["fonts"]:
                inp.setText(str(self.current_theme["fonts"][key]))
                
        for key, inp in self.size_inputs.items():
            if key in self.current_theme["sizes"]:
                inp.setText(str(self.current_theme["sizes"][key]))
        
        self.apply_theme()
