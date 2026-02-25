from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
)


class NoScrollSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class ParameterInput(QWidget):
    def __init__(
        self, label_text, widget_type, default_value=None, options=None, parent=None
    ):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.label = QLabel(label_text)
        self.layout.addWidget(self.label)

        self.input_widget = None
        self.widget_type = widget_type
        self.default_value = default_value

        if widget_type == "text":
            self.input_widget = QLineEdit()
            if default_value:
                self.input_widget.setText(str(default_value))

        elif widget_type == "int":
            self.input_widget = NoScrollSpinBox()
            self.input_widget.setRange(-1, 999999)  # -1 for auto/unlimited often used
            if default_value is not None:
                self.input_widget.setValue(int(default_value))

        elif widget_type == "float":
            self.input_widget = NoScrollDoubleSpinBox()
            self.input_widget.setRange(0.0, 100.0)
            self.input_widget.setSingleStep(0.1)
            if default_value is not None:
                self.input_widget.setValue(float(default_value))

        elif widget_type == "bool":
            self.input_widget = QCheckBox()
            if default_value:
                self.input_widget.setChecked(True)

        elif widget_type == "combo":
            self.input_widget = NoScrollComboBox()
            if options:
                self.input_widget.addItems(options)
            if default_value:
                self.input_widget.setCurrentText(str(default_value))

        self.layout.addWidget(self.input_widget)

    def get_value(self):
        if self.widget_type == "text":
            return self.input_widget.text()
        elif self.widget_type == "int":
            return self.input_widget.value()
        elif self.widget_type == "float":
            return self.input_widget.value()
        elif self.widget_type == "bool":
            return self.input_widget.isChecked()
        elif self.widget_type == "combo":
            return self.input_widget.currentText()

    def reset_to_default(self):
        """Reset this input to its default value."""
        if self.default_value is not None:
            self.set_value(self.default_value)
        elif self.widget_type == "text":
            self.input_widget.setText("")
        elif self.widget_type == "int":
            self.input_widget.setValue(0)
        elif self.widget_type == "float":
            self.input_widget.setValue(0.0)
        elif self.widget_type == "bool":
            self.input_widget.setChecked(False)
        elif self.widget_type == "combo":
            self.input_widget.setCurrentIndex(0)

    def set_value(self, value):
        if self.widget_type == "text":
            self.input_widget.setText(str(value))
        elif self.widget_type == "int":
            self.input_widget.setValue(int(value))
        elif self.widget_type == "float":
            self.input_widget.setValue(float(value))
        elif self.widget_type == "bool":
            self.input_widget.setChecked(bool(value))
        elif self.widget_type == "combo":
            self.input_widget.setCurrentText(str(value))
