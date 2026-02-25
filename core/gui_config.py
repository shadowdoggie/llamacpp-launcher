import json
import os
import copy

DEFAULT_PARAMS = [
    {"label": "Model", "key": "model", "type": "combo", "default": [], "options": []},
    {
        "label": "Multimodal Projector (mmproj)",
        "key": "mmproj",
        "type": "combo",
        "default": "",
        "options": [""],
    },
    {"label": "Port", "key": "port", "type": "int", "default": 8080},
    {"label": "Context Size", "key": "ctx-size", "type": "int", "default": 32000},
    {"label": "GPU Layers (-ngl)", "key": "ngl", "type": "int", "default": 999},
    {"label": "Batch Size (-ub)", "key": "ub", "type": "int", "default": 512},
    {
        "label": "Offload Mode",
        "key": "offload-mode",
        "type": "combo",
        "default": "n-cpu-moe",
        "options": ["n-cpu-moe", "fit"],
    },
    {"label": "CPU MoE Layers", "key": "n-cpu-moe", "type": "int", "default": 0},
    {
        "label": "Fit Target (MiB buffer)",
        "key": "fit-target",
        "type": "int",
        "default": 1024,
    },
    {"label": "Temperature", "key": "temp", "type": "float", "default": 0.7},
    {"label": "Top P", "key": "top-p", "type": "float", "default": 0.8},
    {"label": "Min P", "key": "min-p", "type": "float", "default": 0.0},
    {"label": "Top K", "key": "top-k", "type": "int", "default": 20},
    {
        "label": "Repeat Penalty",
        "key": "repeat-penalty",
        "type": "float",
        "default": 1.05,
    },
    {"label": "Main GPU", "key": "main-gpu", "type": "int", "default": 0},
    {
        "label": "Split Mode",
        "key": "split-mode",
        "type": "combo",
        "default": "none",
        "options": ["none", "layer", "row"],
    },
    {"label": "Tensor Split (-ts)", "key": "ts", "type": "text", "default": ""},
    {"label": "Flash Attention", "key": "flash-attn", "type": "bool", "default": True},
    {
        "label": "Expose to Network (0.0.0.0)",
        "key": "host_0000",
        "type": "bool",
        "default": False,
    },
    {"label": "Jinja Template", "key": "jinja", "type": "bool", "default": True},
    {
        "label": "Reasoning Format",
        "key": "reasoning-format",
        "type": "combo",
        "default": "auto",
        "options": ["auto", "none", "deepseek", "deepseek-legacy"],
    },
    {
        "label": "Reasoning Effort",
        "key": "reasoning-effort",
        "type": "combo",
        "default": "",
        "options": ["", "low", "medium", "high"],
    },
    {
        "label": "Cache Type K (-ctk)",
        "key": "ctk",
        "type": "combo",
        "default": "",
        "options": [
            "",
            "f16",
            "bf16",
            "q8_0",
            "q4_0",
            "q4_1",
            "iq4_nl",
            "q5_0",
            "q5_1",
            "f32",
        ],
    },
    {
        "label": "Cache Type V (-ctv)",
        "key": "ctv",
        "type": "combo",
        "default": "",
        "options": [
            "",
            "f16",
            "bf16",
            "q8_0",
            "q4_0",
            "q4_1",
            "iq4_nl",
            "q5_0",
            "q5_1",
            "f32",
        ],
    },
]


class GuiConfig:
    def __init__(self, filepath):
        self.filepath = filepath
        self.params = []
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.params = json.load(f)
            except Exception as e:
                print(f"Error loading gui config: {e}")
                self.params = copy.deepcopy(DEFAULT_PARAMS)
        else:
            self.params = copy.deepcopy(DEFAULT_PARAMS)

    def save(self, params):
        self.params = params
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.params, f, indent=4)
        except Exception as e:
            print(f"Error saving gui config: {e}")

    def get_params(self):
        return self.params
