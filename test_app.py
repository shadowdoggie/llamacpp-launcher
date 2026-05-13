import unittest
import os
import json
import shutil
from core.command_builder import CommandBuilder
from core.profile_manager import ProfileManager

class TestLauncher(unittest.TestCase):
    def test_command_builder(self):
        builder = CommandBuilder(base_executable="llama-server.exe", models_dir="C:\\models")
        params = {
            "model": "my_model.gguf",
            "port": 8081,
            "ctx-size": 4096,
            "flash-attn": True,
            "jinja": False,
            "preserve-thinking": True,
            "reasoning-effort": "medium",
            "spec-type": "draft-mtp",
            "spec-draft-n-max": 2,
            "parallel": 0,
        }
        cmd, env = builder.build_command(params)
        
        # Check command args
        self.assertEqual(cmd[0], "llama-server.exe")
        self.assertIn("-m", cmd)
        self.assertIn("C:\\models\\my_model.gguf", cmd)
        self.assertIn("--port", cmd)
        self.assertIn("8081", cmd)
        self.assertIn("--spec-type", cmd)
        self.assertIn("draft-mtp", cmd)
        self.assertIn("--spec-draft-n-max", cmd)
        self.assertIn("2", cmd)
        self.assertIn("--parallel", cmd)
        self.assertIn("1", cmd)
        
        # Check env vars
        self.assertIn("LLAMA_CHAT_TEMPLATE_KWARGS", env)
        self.assertEqual(
            env["LLAMA_CHAT_TEMPLATE_KWARGS"],
            '{"preserve_thinking":true,"reasoning_effort":"medium"}',
        )

    def test_profile_manager(self):
        test_file = "test_profiles.json"
        if os.path.exists(test_file):
            os.remove(test_file)
        
        pm = ProfileManager(test_file)
        pm.save_profile("Test1", {"foo": "bar"})
        
        pm2 = ProfileManager(test_file)
        self.assertEqual(pm2.get_profile("Test1")["foo"], "bar")
        
        pm2.delete_profile("Test1")
        self.assertIsNone(pm2.get_profile("Test1"))
        
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
