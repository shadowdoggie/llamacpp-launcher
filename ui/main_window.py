import os
import subprocess
import webbrowser
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QScrollArea,
    QMessageBox,
    QInputDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QDialog,
    QFormLayout,
    QComboBox,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer

from core.model_scanner import ModelScanner
from core.profile_manager import ProfileManager
from core.command_builder import CommandBuilder
from core.settings_manager import SettingsManager
from ui.widgets import ParameterInput
from core.gui_config import GuiConfig
from core.theme_manager import ThemeManager
from ui.theme_editor import ThemeEditorDialog


class ParameterEditDialog(QDialog):
    def __init__(self, param_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Parameter")
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)
        self.param_data = param_data or {}

        form = QFormLayout()

        self.inp_label = QLineEdit(self.param_data.get("label", ""))
        self.inp_key = QLineEdit(self.param_data.get("key", ""))
        self.inp_type = QComboBox()
        self.inp_type.addItems(["text", "int", "float", "bool", "combo"])
        self.inp_type.setCurrentText(self.param_data.get("type", "text"))
        self.inp_type.currentTextChanged.connect(self.on_type_changed)

        self.inp_default = QLineEdit(str(self.param_data.get("default", "")))

        self.inp_options = QLineEdit(
            ",".join(self.param_data.get("options", []))
            if isinstance(self.param_data.get("options"), list)
            else ""
        )
        self.inp_options.setPlaceholderText("Comma separated options for combo")
        self.inp_options.setEnabled(False)

        form.addRow("Label:", self.inp_label)
        form.addRow("Flag/Key:", self.inp_key)
        form.addRow("Type:", self.inp_type)
        form.addRow("Default:", self.inp_default)
        form.addRow("Options:", self.inp_options)

        self.layout.addLayout(form)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        self.layout.addLayout(btn_box)

        self.on_type_changed(self.inp_type.currentText())

    def on_type_changed(self, text):
        self.inp_options.setEnabled(text == "combo")

    def get_data(self):
        data = {
            "label": self.inp_label.text(),
            "key": self.inp_key.text(),
            "type": self.inp_type.currentText(),
        }

        # Parse default
        def_val = self.inp_default.text()
        if data["type"] == "int":
            try:
                data["default"] = int(def_val)
            except:
                data["default"] = 0
        elif data["type"] == "float":
            try:
                data["default"] = float(def_val)
            except:
                data["default"] = 0.0
        elif data["type"] == "bool":
            data["default"] = def_val.lower() in ("true", "1", "yes")
        elif data["type"] == "combo":
            data["default"] = def_val
            opts = [x.strip() for x in self.inp_options.text().split(",")]
            data["options"] = opts
        else:
            data["default"] = def_val

        return data


class SettingsDialog(QDialog):
    def __init__(self, current_server_dir, current_models_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 200)
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.server_dir_edit = QLineEdit(current_server_dir)
        self.btn_browse_server = QPushButton("Browse")
        self.btn_browse_server.clicked.connect(self.browse_server)

        server_layout = QHBoxLayout()
        server_layout.addWidget(self.server_dir_edit)
        server_layout.addWidget(self.btn_browse_server)

        self.models_dir_edit = QLineEdit(current_models_dir)
        self.btn_browse_models = QPushButton("Browse")
        self.btn_browse_models.clicked.connect(self.browse_models)

        models_layout = QHBoxLayout()
        models_layout.addWidget(self.models_dir_edit)
        models_layout.addWidget(self.btn_browse_models)

        form_layout.addRow("Llama Server Folder:", server_layout)
        form_layout.addRow("Models Folder:", models_layout)

        self.layout.addLayout(form_layout)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)

        self.layout.addLayout(btn_box)

    def browse_server(self):
        dir_ = QFileDialog.getExistingDirectory(
            self, "Select Llama Server Folder", self.server_dir_edit.text()
        )
        if dir_:
            self.server_dir_edit.setText(dir_)

    def browse_models(self):
        dir_ = QFileDialog.getExistingDirectory(
            self, "Select Models Folder", self.models_dir_edit.text()
        )
        if dir_:
            self.models_dir_edit.setText(dir_)

    def get_paths(self):
        return self.server_dir_edit.text(), self.models_dir_edit.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llama.cpp Launcher")
        self.resize(1000, 700)

        # Base Dir
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Settings
        self.settings_manager = SettingsManager(
            os.path.join(self.base_dir, "settings.json")
        )
        self.gui_config = GuiConfig(os.path.join(self.base_dir, "gui_layout.json"))
        self.theme_manager = ThemeManager(os.path.join(self.base_dir, "theme.json"))

        # Default Paths
        default_server_dir = os.path.dirname(self.base_dir)
        default_models_dir = os.path.join(default_server_dir, "models")

        self.server_dir = self.settings_manager.get("server_dir", default_server_dir)
        self.models_dir = self.settings_manager.get("models_dir", default_models_dir)

        # Core Components
        self.profile_manager = ProfileManager(
            os.path.join(self.base_dir, "profiles.json")
        )
        self.scanner = None
        self.command_builder = None

        self.refresh_components()

        self.available_models = []
        self.current_profile_name = None
        self.server_process = None

        # Timer to monitor server process
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)

        self.init_ui()
        self.apply_theme()
        self.refresh_models()
        self.load_profile_list()

    def apply_theme(self):
        qss = self.theme_manager.get_stylesheet()
        QApplication.instance().setStyleSheet(qss)

    def refresh_components(self):
        self.scanner = ModelScanner(self.models_dir)
        self.command_builder = CommandBuilder(
            base_executable=os.path.join(self.server_dir, "llama-server.exe"),
            models_dir=self.models_dir,
        )

    def refresh_models(self):
        self.available_models = self.scanner.scan()
        # Update model combo box if it exists
        if hasattr(self, "inputs") and "model" in self.inputs:
            combo = self.inputs["model"].input_widget
            current = combo.currentText()
            combo.clear()
            combo.addItems(self.available_models)
            # Try to restore the previous selection
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            # Trigger mmproj update for the current selection
            self._update_mmproj_options()

    def _update_mmproj_options(self):
        """Update the mmproj combo box based on the currently selected model."""
        if not hasattr(self, "inputs"):
            return
        if "mmproj" not in self.inputs or "model" not in self.inputs:
            return

        model_combo = self.inputs["model"].input_widget
        mmproj_combo = self.inputs["mmproj"].input_widget

        selected_model = model_combo.currentText()

        # Get mmproj files available for this model's directory
        mmproj_options = (
            self.scanner.get_mmproj_options(selected_model) if selected_model else []
        )

        # Save current mmproj selection if any
        current_mmproj = mmproj_combo.currentText()

        mmproj_combo.clear()
        mmproj_combo.addItem("")  # Empty = no mmproj (always first option)

        if mmproj_options:
            for mp in mmproj_options:
                # Show just the filename for cleaner display, store full relative path
                display_name = os.path.basename(mp)
                mmproj_combo.addItem(display_name, mp)

            # Enable the combo
            mmproj_combo.setEnabled(True)

            # Try to restore previous selection
            idx = mmproj_combo.findText(current_mmproj)
            if idx >= 0:
                mmproj_combo.setCurrentIndex(idx)
        else:
            mmproj_combo.setEnabled(False)

    def _on_model_changed(self, text):
        """Called when the model combo box selection changes."""
        self._update_mmproj_options()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        sidebar_layout = QVBoxLayout()
        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.on_profile_selected)
        sidebar_layout.addWidget(self.profile_list)

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("New Profile")
        self.btn_new.clicked.connect(self.new_profile)
        self.btn_delete = QPushButton("Delete Profile")
        self.btn_delete.clicked.connect(self.delete_profile)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_delete)
        sidebar_layout.addLayout(btn_layout)

        self.btn_delete_all = QPushButton("Delete All Profiles")
        self.btn_delete_all.setObjectName("btn_delete_all")
        self.btn_delete_all.clicked.connect(self.delete_all_profiles)
        sidebar_layout.addWidget(self.btn_delete_all)

        self.btn_settings = QPushButton("Settings")
        self.btn_settings.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.btn_settings)

        self.btn_edit_mode = QPushButton("Edit GUI Mode")
        self.btn_edit_mode.setCheckable(True)
        self.btn_edit_mode.clicked.connect(self.toggle_edit_mode)
        sidebar_layout.addWidget(self.btn_edit_mode)

        main_layout.addLayout(sidebar_layout, 1)

        # Main Area
        right_layout = QVBoxLayout()

        # Scroll Area for Parameters
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.param_container = QWidget()
        self.param_layout = QVBoxLayout(self.param_container)
        self.param_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.param_container)

        right_layout.addWidget(self.scroll)

        # Edit Mode List (Hidden by default)
        self.edit_list = QListWidget()
        self.edit_list.setDragDropMode(QListWidget.InternalMove)
        self.edit_list.setSelectionMode(QListWidget.SingleSelection)
        self.edit_list.itemDoubleClicked.connect(self.edit_list_item_dbl_clicked)
        self.edit_list.setVisible(False)
        right_layout.addWidget(self.edit_list)

        # Edit Mode Controls (Hidden by default)
        self.edit_controls = QWidget()
        edit_ctrl_layout = QHBoxLayout(self.edit_controls)
        self.btn_add_param = QPushButton("Add Parameter")
        self.btn_add_param.clicked.connect(self.add_parameter)
        self.btn_edit_theme = QPushButton("Edit Theme")
        self.btn_edit_theme.clicked.connect(self.open_theme_editor)
        self.btn_reset_gui = QPushButton("Reset Default GUI")
        self.btn_reset_gui.clicked.connect(self.reset_gui)
        edit_ctrl_layout.addWidget(self.btn_add_param)
        edit_ctrl_layout.addWidget(self.btn_edit_theme)
        edit_ctrl_layout.addWidget(self.btn_reset_gui)
        self.edit_controls.setVisible(False)
        right_layout.addWidget(self.edit_controls)

        # Action Buttons
        action_layout = QHBoxLayout()

        self.btn_open_chat = QPushButton("Open Chat")
        self.btn_open_chat.clicked.connect(self.open_chat)
        self.btn_open_chat.setEnabled(False)

        self.btn_monitor_gpu = QPushButton("Monitor GPU")
        self.btn_monitor_gpu.clicked.connect(self.monitor_gpu)

        self.btn_stop = QPushButton("Stop Server")
        self.btn_stop.setObjectName("btn_stop")  # For styling
        self.btn_stop.clicked.connect(self.stop_server)
        self.btn_stop.setEnabled(False)

        self.btn_save = QPushButton("Save Profile")
        self.btn_save.clicked.connect(self.save_profile)

        self.btn_launch = QPushButton("Launch")
        self.btn_launch.clicked.connect(self.launch_model)

        action_layout.addWidget(self.btn_open_chat)
        action_layout.addWidget(self.btn_monitor_gpu)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_stop)
        action_layout.addWidget(self.btn_save)
        action_layout.addWidget(self.btn_launch)

        right_layout.addLayout(action_layout)

        main_layout.addLayout(right_layout, 3)

        self.inputs = {}
        self.create_parameter_inputs()

    def create_parameter_inputs(self):
        # Clear existing
        for i in reversed(range(self.param_layout.count())):
            self.param_layout.itemAt(i).widget().setParent(None)
        self.inputs = {}

        params = self.gui_config.get_params()

        for p in params:
            label = p.get("label", "Unknown")
            key = p.get("key", "")
            type_ = p.get("type", "text")
            default = p.get("default", "")
            options = p.get("options", None)

            # Special handling for 'model' - inject available models from scanner
            if key == "model":
                options = self.available_models

            # Special handling for 'mmproj' - will be populated dynamically
            if key == "mmproj":
                options = [""]  # Start with just empty (no mmproj)

            inp = ParameterInput(label, type_, default, options)
            self.param_layout.addWidget(inp)
            self.inputs[key] = inp

        # Connect model combo change to update mmproj options
        if "model" in self.inputs:
            model_widget = self.inputs["model"].input_widget
            model_widget.currentTextChanged.connect(self._on_model_changed)

        # Disable mmproj combo initially until a model is selected
        if "mmproj" in self.inputs:
            self.inputs["mmproj"].input_widget.setEnabled(False)

        # Connect offload-mode combo to toggle n-cpu-moe / fit-target enabled state
        if "offload-mode" in self.inputs:
            offload_widget = self.inputs["offload-mode"].input_widget
            offload_widget.currentTextChanged.connect(self._on_offload_mode_changed)
            # Set initial state
            self._on_offload_mode_changed(offload_widget.currentText())

    def _on_offload_mode_changed(self, text):
        """Enable/disable n-cpu-moe and fit-target based on offload mode selection."""
        dimmed = "color: #585b70;"
        is_fit = text == "fit"

        # n-cpu-moe: enabled when mode is n-cpu-moe, disabled when fit
        if "n-cpu-moe" in self.inputs:
            moe_input = self.inputs["n-cpu-moe"]
            moe_input.input_widget.setEnabled(not is_fit)
            moe_input.label.setStyleSheet(dimmed if is_fit else "")

        # fit-target: enabled when mode is fit, disabled when n-cpu-moe
        if "fit-target" in self.inputs:
            fit_input = self.inputs["fit-target"]
            fit_input.input_widget.setEnabled(is_fit)
            fit_input.label.setStyleSheet("" if is_fit else dimmed)

    def toggle_edit_mode(self, checked):
        if checked:
            self.btn_edit_mode.setText("Save GUI Changes")
            self.scroll.setVisible(False)
            self.edit_list.setVisible(True)
            self.edit_controls.setVisible(True)
            self.populate_edit_list()
            # Disable other actions
            self.btn_launch.setEnabled(False)
        else:
            self.btn_edit_mode.setText("Edit GUI Mode")
            self.save_edit_list()
            self.edit_list.setVisible(False)
            self.edit_controls.setVisible(False)
            self.scroll.setVisible(True)
            self.create_parameter_inputs()
            self.btn_launch.setEnabled(True)

    def populate_edit_list(self):
        self.edit_list.clear()
        params = self.gui_config.get_params()
        for p in params:
            from PyQt5.QtWidgets import QListWidgetItem

            item = QListWidgetItem(f"{p['label']} ({p['key']})")
            item.setData(Qt.UserRole, p)
            self.edit_list.addItem(item)

    def save_edit_list(self):
        new_params = []
        for i in range(self.edit_list.count()):
            item = self.edit_list.item(i)
            new_params.append(item.data(Qt.UserRole))
        self.gui_config.save(new_params)

    def edit_list_item_dbl_clicked(self, item):
        data = item.data(Qt.UserRole)
        dialog = ParameterEditDialog(data, self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            item.setData(Qt.UserRole, new_data)
            item.setText(f"{new_data['label']} ({new_data['key']})")

    def add_parameter(self):
        dialog = ParameterEditDialog(None, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            from PyQt5.QtWidgets import QListWidgetItem

            item = QListWidgetItem(f"{data['label']} ({data['key']})")
            item.setData(Qt.UserRole, data)
            self.edit_list.addItem(item)

    def reset_gui(self):
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset GUI to defaults?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            import core.gui_config

            self.gui_config.save(core.gui_config.DEFAULT_PARAMS)
            self.populate_edit_list()

    def open_theme_editor(self):
        dialog = ThemeEditorDialog(self.theme_manager, self)
        dialog.exec_()
        # Ensure theme is applied after close (in case they saved)
        self.apply_theme()

    def open_settings(self):
        dialog = SettingsDialog(self.server_dir, self.models_dir, self)
        if dialog.exec_() == QDialog.Accepted:
            new_server_dir, new_models_dir = dialog.get_paths()

            if new_server_dir != self.server_dir or new_models_dir != self.models_dir:
                self.server_dir = new_server_dir
                self.models_dir = new_models_dir

                self.settings_manager.set("server_dir", self.server_dir)
                self.settings_manager.set("models_dir", self.models_dir)

                self.refresh_components()
                self.refresh_models()
                QMessageBox.information(
                    self, "Settings Saved", "Settings updated successfully."
                )

    def load_profile_list(self):
        self.profile_list.clear()
        names = self.profile_manager.get_profile_names()
        self.profile_list.addItems(names)

    def on_profile_selected(self, item):
        name = item.text()
        self.current_profile_name = name
        data = self.profile_manager.get_profile(name)
        self.load_form_data(data)

    def load_form_data(self, data):
        if not data:
            return
        params = data.get("parameters", {})

        # Load model first so that mmproj options get populated via the signal
        if "model" in params and "model" in self.inputs:
            self.inputs["model"].set_value(params["model"])

        # Then load mmproj (the combo should now have the right options)
        if "mmproj" in params and "mmproj" in self.inputs:
            mmproj_val = params["mmproj"]
            if mmproj_val:
                combo = self.inputs["mmproj"].input_widget
                # Try matching by display name (basename) first
                basename = os.path.basename(mmproj_val)
                idx = combo.findText(basename)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    # Try matching by full relative path stored in item data
                    for i in range(combo.count()):
                        if combo.itemData(i) == mmproj_val:
                            combo.setCurrentIndex(i)
                            break

        # Load all other parameters
        for key, inp in self.inputs.items():
            if key in ("model", "mmproj"):
                continue  # Already handled above
            if key in params:
                inp.set_value(params[key])

    def get_form_data(self):
        data = {}
        for key, inp in self.inputs.items():
            if key == "mmproj":
                # Store the full relative path (from itemData), not just display name
                combo = inp.input_widget
                idx = combo.currentIndex()
                rel_path = combo.itemData(idx)
                # If itemData is None (the empty "" entry), store empty string
                data[key] = rel_path if rel_path else ""
            else:
                data[key] = inp.get_value()
        return data

    def new_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name:
            if name in self.profile_manager.get_profile_names():
                QMessageBox.warning(self, "Error", "Profile already exists!")
                return

            # Create default profile
            default_data = {
                "name": name,
                "parameters": self.get_form_data(),  # Use current defaults
            }
            self.profile_manager.save_profile(name, default_data)
            self.load_profile_list()
            # Select the new item
            items = self.profile_list.findItems(name, Qt.MatchExactly)
            if items:
                self.profile_list.setCurrentItem(items[0])
                self.on_profile_selected(items[0])

    def delete_profile(self):
        if not self.current_profile_name:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.current_profile_name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.profile_manager.delete_profile(self.current_profile_name)
            self.current_profile_name = None
            self.load_profile_list()

    def delete_all_profiles(self):
        count = len(self.profile_manager.get_profile_names())
        if count == 0:
            QMessageBox.information(
                self, "No Profiles", "There are no profiles to delete."
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete All Profiles",
            f"Are you sure you want to delete ALL {count} profiles?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.profile_manager.delete_all_profiles()
            self.current_profile_name = None
            self.load_profile_list()

    def save_profile(self):
        if not self.current_profile_name:
            self.new_profile()
            return

        data = {"name": self.current_profile_name, "parameters": self.get_form_data()}
        self.profile_manager.save_profile(self.current_profile_name, data)
        QMessageBox.information(
            self, "Saved", f"Profile '{self.current_profile_name}' saved."
        )

    def launch_model(self):
        if self.server_process:
            reply = QMessageBox.question(
                self,
                "Server Running",
                "A server is already running. Stop it and start new?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.stop_server()
            else:
                return

        params = self.get_form_data()

        # Validate model
        if not params.get("model"):
            QMessageBox.warning(self, "Error", "Please select a model.")
            return

        cmd_list, env = self.command_builder.build_command(params)
        cmd_str = self.command_builder.build_command_string(params)

        print(f"Launching: {cmd_str}")

        try:
            # Launch in new terminal
            # Use server_dir as cwd
            self.server_process = subprocess.Popen(
                cmd_list,
                cwd=self.server_dir,
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

            self.btn_launch.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.btn_open_chat.setEnabled(True)

            # Start monitoring
            self.status_timer.start(1000)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch: {e}")

    def check_server_status(self):
        if self.server_process:
            if self.server_process.poll() is not None:
                # Process has exited
                self.server_process = None
                self.status_timer.stop()
                self.btn_launch.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.btn_open_chat.setEnabled(False)

    def stop_server(self):
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process = None
                self.status_timer.stop()
                self.btn_launch.setEnabled(True)
                self.btn_stop.setEnabled(False)
                self.btn_open_chat.setEnabled(False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to stop server: {e}")
        else:
            # Reset UI just in case
            self.status_timer.stop()
            self.btn_launch.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.btn_open_chat.setEnabled(False)

    def open_chat(self):
        params = self.get_form_data()
        port = params.get("port", 8080)
        url = f"http://localhost:{port}"
        webbrowser.open(url)

    def monitor_gpu(self):
        try:
            subprocess.Popen(
                ["nvidia-smi", "-l", "1"], creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to launch nvidia-smi: {e}")
