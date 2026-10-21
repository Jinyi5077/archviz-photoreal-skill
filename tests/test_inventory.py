import base64
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/archviz-photoreal/scripts/inventory_render_set.py"
SPEC = importlib.util.spec_from_file_location("inventory_render_set", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j9mUAAAAASUVORK5CYII=")


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def write(self, name, content=PNG):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_chinese_name_and_channels_are_read_only(self):
        paths = [self.write(name) for name in (
            "图片.png", "图片_AI_Albedo.png", "图片_AI_Normal.png", "图片_AI_Material.png")]
        before = {path: path.read_bytes() for path in paths}
        result = MODULE.inventory(self.root)
        self.assertEqual(result["view_count"], 1)
        view = result["views"][0]
        self.assertEqual(view["view"], "图片")
        self.assertEqual(view["missing_ai_passes"], [])
        self.assertEqual(view["issues"], [])
        self.assertEqual(view["files"]["beauty"][0]["dimensions"], [1, 1])
        self.assertEqual(view["visual_inspection"], "required_not_performed")
        self.assertEqual(before, {path: path.read_bytes() for path in paths})

    def test_wrong_sized_pass_is_not_accepted_as_aligned(self):
        self.write("view.png")
        altered = PNG[:16] + (2).to_bytes(4, "big") + PNG[20:]
        self.write("view_AI_Normal.png", altered)
        view = MODULE.inventory(self.root)["views"][0]
        self.assertIn("dimension_mismatch:view_AI_Normal.png", view["issues"])

    def test_duplicate_beauty_and_orphan_are_reported(self):
        self.write("view.png")
        self.write("view.jpg")
        self.write("other_AI_Normal.png")
        views = {item["view"]: item for item in MODULE.inventory(self.root)["views"]}
        self.assertIn("duplicate_role:beauty", views["view"]["issues"])
        self.assertIn("orphan_passes_no_beauty", views["other"]["issues"])

    def test_explicit_selection_does_not_read_output_subdirectory(self):
        self.write("场景 2.png")
        self.write("场景 10.png")
        self.write("generated/场景 2_超写实.png")
        result = MODULE.inventory(self.root, ["场景 2", "不存在"])
        self.assertEqual(result["view_count"], 1)
        self.assertEqual(result["requested_views_not_found"], ["不存在"])

    def test_unknown_ai_channel_not_misidentified_as_main(self):
        self.write("view.png")
        self.write("view_AI_Unknown.png")
        result = MODULE.inventory(self.root)
        self.assertEqual(result["view_count"], 1)
        self.assertEqual(result["unclassified_ai_files"], ["view_AI_Unknown.png"])


if __name__ == "__main__":
    unittest.main()
