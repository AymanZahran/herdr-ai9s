import unittest

from lib import (
    created_pane_id,
    decide,
    plugin_pane_id,
    shell_command,
    sidebar_pane,
    tab_label,
    target_pane,
)


class LibTest(unittest.TestCase):
    def test_shell_command_quotes(self):
        self.assertEqual(
            shell_command("claude", ["--resume", "one two"]),
            "claude --resume 'one two'",
        )

    def test_shell_command_rejects_controls(self):
        with self.assertRaises(ValueError):
            shell_command("claude", ["bad\nid"])

    def test_empty_args(self):
        self.assertEqual(shell_command("claude", None), "claude")

    def test_tab_label_clips(self):
        self.assertEqual(tab_label(""), "ai9s")
        self.assertTrue(tab_label("x" * 80).endswith("…"))
        self.assertLessEqual(len(tab_label("x" * 80)), 48)

    def test_target_pane(self):
        self.assertEqual(target_pane("w1:p1", {"focused_pane_id": "w1:p9"}), "w1:p1")
        self.assertEqual(target_pane("  ", {"focused_pane_id": " w1:p4 "}), "w1:p4")
        self.assertEqual(target_pane("", None), "")

    def test_sidebar_pane(self):
        panes = [
            {"pane_id": "w1:p1", "tab_id": "w1:t1", "label": None},
            {"pane_id": "w1:p2", "tab_id": "w1:t1", "label": "ai9s", "focused": False},
            {"pane_id": "w1:p3", "tab_id": "w1:t1", "label": "ai9s", "focused": True},
            {"pane_id": "w1:p4", "tab_id": "w1:t2", "label": "ai9s", "focused": True},
        ]
        self.assertEqual(sidebar_pane(panes, "w1:t1"), ("w1:p3", True))
        self.assertEqual(sidebar_pane(panes[:2], "w1:t1"), ("w1:p2", False))
        self.assertEqual(sidebar_pane([], "w1:t1"), ("", False))

    def test_decide(self):
        self.assertEqual(decide("", False, False, False), ("open", ""))
        self.assertEqual(decide("w1:p2", True, False, True), ("focus", "w1:p2"))
        self.assertEqual(decide("w1:p2", True, True, True), ("close", "w1:p2"))
        self.assertEqual(decide("w1:p2", False, False, False), ("open", ""))

    def test_pane_ids(self):
        opened = {"result": {"plugin_pane": {"pane": {"pane_id": "w1:p9"}}}}
        created = {"result": {"root_pane": {"pane_id": "w1:p3"}, "tab": {"tab_id": "w1:t2"}}}
        self.assertEqual(plugin_pane_id(opened), "w1:p9")
        self.assertEqual(created_pane_id(created), "w1:p3")


if __name__ == "__main__":
    unittest.main()
