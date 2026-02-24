# Llama.cpp Launcher

A PyQt5 GUI launcher for [llama.cpp](https://github.com/ggerganov/llama.cpp)'s `llama-server`.

## Features

- **Recursive model discovery** - Scans all subdirectories in your models folder for `.gguf` files
- **Multimodal projector (mmproj) support** - Automatically detects mmproj files in the same folder as a model and lets you choose between BF16/F32 variants
- **Profile system** - Save and load different launch configurations
- **Customizable GUI** - Add/remove/reorder parameters via Edit GUI Mode
- **Themeable** - Built-in theme editor
- **GPU monitoring** - One-click nvidia-smi launch
- **Network exposure** - Toggle 0.0.0.0 binding for network access

## Architecture

```
launcher/
  main.pyw           - Entry point
  core/
    model_scanner.py  - Recursive .gguf discovery + mmproj detection
    command_builder.py- Builds llama-server CLI commands
    profile_manager.py- Save/load launch profiles
    settings_manager.py- Persistent app settings (paths)
    gui_config.py     - GUI parameter layout (customizable)
    theme_manager.py  - QSS theme system
  ui/
    main_window.py    - Main application window
    widgets.py        - Custom input widgets
    theme_editor.py   - Theme customization dialog
    styles.py         - Style utilities
```

## Setup

1. Place the `launcher/` folder inside your llama.cpp build directory (next to `llama-server.exe`)
2. Put your models in a `models/` folder at the same level
3. Run `python main.pyw` or double-click `run.bat`

### Expected directory structure

```
llama-cpp/
  llama-server.exe
  launcher/          <-- this project
  models/
    model-a.gguf
    some-vision-model/
      model-b.gguf
      mmproj-BF16.gguf
      mmproj-F32.gguf
```

## Requirements

- Python 3.8+
- PyQt5 (`pip install PyQt5`)
