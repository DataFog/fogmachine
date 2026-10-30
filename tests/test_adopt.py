import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("adopt", Path(__file__).resolve().parents[1] / "scripts/adopt.py")
adopt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adopt)

class AdoptionTests(unittest.TestCase):
    def test_tags_and_malformed_images_fail(self):
        for value in ("latest", "ghcr.io/datafog/fogmachine:main", "ghcr.io/datafog/fogmachine@sha256:xyz"):
            with self.assertRaises(ValueError):
                adopt.configuration("core", value)

    def test_both_profiles_use_same_immutable_image(self):
        import json
        image = "ghcr.io/datafog/fogmachine@sha256:" + "a" * 64
        for profile in ("core", "mcp"):
            files = adopt.configuration(profile, image)
            config = json.loads(files[".devcontainer/devcontainer.json"])
            self.assertEqual(config["image"], image)
            self.assertTrue(config["postCreateCommand"].endswith(" && ./dev setup"))
            self.assertIn("sudo chown -R ubuntu:ubuntu", config["postCreateCommand"])
            self.assertTrue(config["mounts"])
        self.assertEqual(adopt.configuration("core", image)[".cursor/Dockerfile"], "FROM " + image + "\n")
