# Changelog

## 2026-02-25 - Recursive Model Scanning & Multimodal Projector Support

### Added
- **Recursive model scanning**: Models are now discovered in all subdirectories, not just the top level of the models folder. Models display as `subfolder/model.gguf` relative paths.
- **Multimodal projector (mmproj) support**: New "Multimodal Projector (mmproj)" dropdown in the GUI.
  - Automatically detects `mmproj-*.gguf` files in the same folder as the selected model.
  - Dynamically updates available mmproj options when the model selection changes.
  - Supports choosing between variants (e.g., BF16 vs F32) when multiple are available.
  - Disabled/greyed out when no mmproj files exist for the selected model.
  - Passes `--mmproj <path>` flag to llama-server when a projector is selected.
- mmproj selection is saved/restored with profiles.

### Changed
- Default models directory changed from `0_models` to `models` to match actual folder structure.
- Model combo box now shows relative paths (e.g., `qwen3.5 35b/Qwen3.5-35B-A3B-Q4_K_M.gguf`) instead of flat filenames.
- Models sorted by depth (top-level first) then alphabetically.

### Fixed
- Models in subdirectories were previously invisible to the launcher.
