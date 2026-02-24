import os


class ModelScanner:
    MMPROJ_INDICATORS = ["mmproj"]

    def __init__(self, models_dir):
        self.models_dir = models_dir
        # Maps relative model path -> list of relative mmproj paths in the same folder
        self._model_mmproj_map = {}

    def _is_mmproj(self, filename):
        """Check if a gguf file is a multimodal projector file."""
        lower = filename.lower()
        return any(ind in lower for ind in self.MMPROJ_INDICATORS)

    def scan(self):
        """Recursively scans the models directory for .gguf model files.

        Returns a list of relative paths (using forward slashes) for all
        non-mmproj .gguf files. Also builds an internal map of which mmproj
        files are available in each model's directory.
        """
        self._model_mmproj_map = {}

        if not os.path.exists(self.models_dir):
            return []

        model_files = []

        for dirpath, dirnames, filenames in os.walk(self.models_dir):
            gguf_files = [f for f in filenames if f.lower().endswith(".gguf")]

            if not gguf_files:
                continue

            # Separate models from mmproj files in this directory
            models_in_dir = []
            mmproj_in_dir = []

            for f in gguf_files:
                if self._is_mmproj(f):
                    mmproj_in_dir.append(f)
                else:
                    models_in_dir.append(f)

            # Build relative paths from models_dir
            rel_dir = os.path.relpath(dirpath, self.models_dir)

            # Compute relative mmproj paths for this directory
            mmproj_rel_paths = []
            for mp in mmproj_in_dir:
                if rel_dir == ".":
                    mmproj_rel_paths.append(mp)
                else:
                    mmproj_rel_paths.append(
                        os.path.join(rel_dir, mp).replace("\\", "/")
                    )

            for m in models_in_dir:
                if rel_dir == ".":
                    rel_path = m
                else:
                    rel_path = os.path.join(rel_dir, m).replace("\\", "/")

                model_files.append(rel_path)
                # Associate mmproj files from the same directory
                self._model_mmproj_map[rel_path] = mmproj_rel_paths

        # Sort: top-level files first, then by folder, then by name
        model_files.sort(key=lambda p: (p.count("/"), p.lower()))

        return model_files

    def get_mmproj_options(self, model_rel_path):
        """Returns a list of mmproj relative paths available for the given model.

        These are the mmproj files found in the same directory as the model.
        Returns an empty list if none are available.
        """
        return self._model_mmproj_map.get(model_rel_path, [])

    def get_full_path(self, rel_path):
        """Returns the absolute path for a model or mmproj given its relative path."""
        return os.path.join(self.models_dir, rel_path.replace("/", os.sep))
