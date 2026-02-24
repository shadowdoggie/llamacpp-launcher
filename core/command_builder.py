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
        if params.get("jinja", True):
            cmd.append("--jinja")
        else:
            cmd.append("--no-jinja")

        if params.get("host_0000", False):
            cmd.extend(["--host", "0.0.0.0"])

        # Flash attention (on/off/auto - default is auto, so only emit if explicitly set)
        fa = params.get("flash-attn")
        if fa is True:
            cmd.extend(["--flash-attn", "on"])
        elif fa is False:
            cmd.extend(["--flash-attn", "off"])
        # if None/missing, leave as auto (server default)

        # Offload mode: --fit or manual --n-cpu-moe
        # IMPORTANT: --fit is ON by default in llama-server, but it gets DISABLED
        # if the user explicitly sets -ngl, --tensor-split, or --override-tensor.
        # So in fit mode we must NOT send those flags. In manual mode we send
        # --fit off to disable it and allow full manual control.
        offload_mode = params.get("offload-mode", "n-cpu-moe")
        is_fit_mode = offload_mode == "fit"

        if is_fit_mode:
            # --fit is already on by default, no need to send --fit on
            # Only send fit-target if changed from default (1024 MiB)
            fit_target = params.get("fit-target")
            if fit_target is not None and int(fit_target) != 1024:
                cmd.extend(["--fit-target", str(fit_target)])
        else:
            # Manual mode: disable --fit so it doesn't interfere
            cmd.extend(["--fit", "off"])
            # Manual n-cpu-moe - only emit if > 0
            n_cpu_moe = params.get("n-cpu-moe")
            if n_cpu_moe is not None and int(n_cpu_moe) > 0:
                cmd.extend(["--n-cpu-moe", str(n_cpu_moe)])

        # Key-Value pairs
        mappings = {
            "reasoning-format": "--reasoning-format",
            "port": "--port",
            "ctx-size": "--ctx-size",
            "ub": "-ub",
            "temp": "--temp",
            "top-p": "--top-p",
            "top-k": "--top-k",
            "repeat-penalty": "--repeat-penalty",
            "ctk": "-ctk",
            "ctv": "-ctv",
        }

        # These flags disable --fit when explicitly set, so skip them in fit mode
        if not is_fit_mode:
            mappings["ngl"] = "-ngl"
            mappings["split-mode"] = "--split-mode"
            mappings["main-gpu"] = "--main-gpu"
            mappings["ts"] = "-ts"

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
