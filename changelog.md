# Changelog

## 2026-02-25 - Fix GPU params locked in fit mode

### Fixed
- GPU allocation fields (Split Mode, GPU Layers, Main GPU, Tensor Split) are no longer disabled when Offload Mode is set to "fit". Labels are still dimmed to indicate they're ignored by `--fit`, but the widgets remain editable so users can pre-configure them for manual mode.

---

## 2026-02-25 - Fix --fit mode, CLI Flag Audit, Dark Theme, Bulk Delete

### Added
- **Delete All Profiles** button in sidebar (red, with confirmation dialog showing profile count).
- **Offload Mode toggle**: New "Offload Mode" combo switches between `fit` (automatic) and `n-cpu-moe` (manual).
- **Fit Target (MiB buffer)**: New int input for `--fit-target`, only active in fit mode. Defaults to 1024 MiB; only emitted when changed from default.

### Changed
- **Dark theme overhaul**: Replaced the unreadable light-purple background with a proper dark color scheme (Catppuccin Mocha-inspired). Dark backgrounds with high-contrast light text throughout.
- Default theme in `theme_manager.py` updated to match.
- Delete All Profiles button styled with red destructive-action colors.
- Split Mode default changed from `layer` to `none` (single GPU is the common case).

### Fixed (CLI flags audited against actual `llama-server --help` + GitHub discussion #18049)
- **`--fit` mode was completely broken**: sending `-ngl`, `--split-mode`, `--tensor-split`, or `--main-gpu` disables `--fit` entirely (per the feature author). In fit mode, these flags are now omitted so `--fit` can auto-manage GPU allocation. In manual mode, `--fit off` is explicitly sent.
- GPU-related inputs (GPU Layers, Split Mode, Main GPU, Tensor Split) are now greyed out in the UI when fit mode is selected, since they're auto-managed.
- `--flash-attn` now emits `on`/`off` properly; when unchecked emits `--flash-attn off` instead of silently still sending `on`.
- `--jinja` / `--no-jinja` handled correctly (jinja is enabled by default in current llama-server).
- `--n-cpu-moe 0` no longer emitted when value is 0 (pointless).
- Reasoning Format options updated: added `auto` (new server default) and `deepseek-legacy`; removed invalid `function`.
- Cache Type K/V options updated with full set: `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`, `f32`.

---

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
