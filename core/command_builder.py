import os


class CommandBuilder:
    def __init__(self, base_executable=".\\llama-server.exe", models_dir=""):
        self.base_executable = base_executable
        self.models_dir = models_dir

    def build_command(self, params):
        """
        Builds the command list for subprocess and environment variables.
        params: dict of parameters
        Returns: (cmd_list, env_dict)
        """
        cmd = [self.base_executable]
        env = os.environ.copy()

        # Model path (supports relative paths with subfolders)
        if "model" in params and params["model"]:
            model_path = os.path.join(
                self.models_dir, params["model"].replace("/", os.sep)
            )
            cmd.extend(["-m", model_path])

        # Multimodal projector path
        if "mmproj" in params and params["mmproj"]:
            mmproj_path = os.path.join(
                self.models_dir, params["mmproj"].replace("/", os.sep)
            )
            cmd.extend(["--mmproj", mmproj_path])

        # Boolean flags
        if params.get("jinja", False):
            cmd.append("--jinja")

        if params.get("host_0000", False):
            cmd.extend(["--host", "0.0.0.0"])

        if params.get("flash-attn", True):  # Default on
            cmd.extend(["--flash-attn", "on"])

        # Offload mode: --fit or --n-cpu-moe <value>
        offload_mode = params.get("offload-mode", "n-cpu-moe")
        if offload_mode == "fit":
            cmd.append("--fit")
        else:
            # Manual n-cpu-moe
            n_cpu_moe = params.get("n-cpu-moe")
            if n_cpu_moe is not None:
                val = str(n_cpu_moe)
                if val:
                    cmd.extend(["--n-cpu-moe", val])

        # Key-Value pairs
        mappings = {
            "reasoning-format": "--reasoning-format",
            "port": "--port",
            "ctx-size": "--ctx-size",
            "ub": "-ub",
            "ngl": "-ngl",
            "temp": "--temp",
            "top-p": "--top-p",
            "top-k": "--top-k",
            "repeat-penalty": "--repeat-penalty",
            "split-mode": "--split-mode",
            "main-gpu": "--main-gpu",
            "ts": "-ts",
            "ctk": "-ctk",
            "ctv": "-ctv",
        }

        for key, arg in mappings.items():
            if key in params and params[key] is not None:
                val = str(params[key])
                if val:  # Only add if not empty string
                    cmd.extend([arg, val])

        # Environment Variables
        if "reasoning-effort" in params and params["reasoning-effort"]:
            effort = params["reasoning-effort"]
            if effort in ["low", "medium", "high"]:
                env["LLAMA_CHAT_TEMPLATE_KWARGS"] = f'{{"reasoning_effort":"{effort}"}}'

        return cmd, env

    def build_command_string(self, params):
        """Builds a string representation for display or bat file."""
        cmd_list, env = self.build_command(params)

        # Quote arguments with spaces
        quoted_cmd = []
        for part in cmd_list:
            if " " in part:
                quoted_cmd.append(f'"{part}"')
            else:
                quoted_cmd.append(part)

        cmd_str = " ".join(quoted_cmd)

        # Prepend env var setting for display (PowerShell style as requested)
        env_str = ""
        if "LLAMA_CHAT_TEMPLATE_KWARGS" in env and env[
            "LLAMA_CHAT_TEMPLATE_KWARGS"
        ] != os.environ.get("LLAMA_CHAT_TEMPLATE_KWARGS"):
            val = env["LLAMA_CHAT_TEMPLATE_KWARGS"]
            env_str = f"$env:LLAMA_CHAT_TEMPLATE_KWARGS = '{val}'; "

        return env_str + cmd_str
