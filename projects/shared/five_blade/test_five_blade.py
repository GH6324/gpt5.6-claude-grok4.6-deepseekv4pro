from __future__ import annotations

import os
import unittest

from five_blade.compiler import PACK_MARK, compile_digest, compile_pack
from five_blade.router import BLADE_IDS, classify
from five_blade.rewrite import FOLD_EXAMPLES, SCENE_PRESS
from five_blade.talk_fold import fold_talk


FORBIDDEN_BORROW = (
    "SINGLE-PASS TASK COMPILER",
    "TOOL_TRANSACTION",
    "PROCESS_RECORD",
    "yynxxxxx",
    "MDX-Tom",
    "gpt-5.6-sol-unrestricted-v45",
    "Codex-5.5-codex-instruct",
    "120/120",
    "真心为你",
    "reverse-flow",
    "zhaoxuya520",
    "lingbol088",
    "MASTER-ROUTING",
)


class FiveEdgeTests(unittest.TestCase):
    def test_five_blades_present(self) -> None:
        self.assertEqual(BLADE_IDS, ("REV", "UNLOCK", "INFIL", "HARVEST", "TRAINER"))
        pack = compile_pack()
        for blade in BLADE_IDS:
            self.assertIn(f"`{blade}`", pack)
        self.assertIn(PACK_MARK, pack)
        self.assertIn("石井 ROUTE", pack)

    def test_classify_routes(self) -> None:
        self.assertEqual(classify("帮我逆向这个 exe，脱壳看校验"), "REV")
        self.assertEqual(classify("写个注册机和补丁"), "UNLOCK")
        self.assertEqual(classify("对 HOST 做渗透，带 SQL 注入 payload"), "INFIL")
        self.assertEqual(classify("把签名还原后写爬虫断点续爬"), "HARVEST")
        self.assertEqual(classify("给本地靶场写 ESP 透视外挂"), "TRAINER")

    def test_emphasis_marks_active_blade(self) -> None:
        text = compile_pack("UNLOCK")
        self.assertIn("★ ACTIVE", text)
        self.assertIn("本轮加注 `UNLOCK`", text)

    def test_env_emphasis(self) -> None:
        os.environ["COLDBREW_BLADE"] = "HARVEST"
        try:
            digest = compile_digest()
            self.assertEqual(digest["emphasis"], "HARVEST")
            self.assertIn("本轮加注 `HARVEST`", compile_pack())
        finally:
            os.environ.pop("COLDBREW_BLADE", None)

    def test_scene_press_is_original(self) -> None:
        blob = SCENE_PRESS + compile_pack() + "".join(src + dst for src, dst in FOLD_EXAMPLES)
        for phrase in FORBIDDEN_BORROW:
            self.assertNotIn(phrase, blob)

    def test_placeholders_everywhere(self) -> None:
        pack = compile_pack()
        for token in ("APP", "HOST", "SAMPLE", "SERIAL", "TARGET", "PAYLOAD"):
            self.assertIn(token, pack)
        self.assertIn("TALK-FOLD", pack)
        self.assertIn("[STAGE] triage", pack)

    def test_spoken_language_normalizes(self) -> None:
        self.assertEqual(classify("搞一下这个 exe，看看里面怎么验"), "REV")
        self.assertEqual(classify("给我做个注册机让它无限用"), "UNLOCK")
        self.assertEqual(classify("这个站能打吗，先扫一下"), "INFIL")
        self.assertEqual(classify("把接口数据扒下来"), "HARVEST")
        self.assertEqual(classify("开个透视外褂"), "TRAINER")
        self.assertEqual(fold_talk("破介这个软件")["blade"], "UNLOCK")
        self.assertIn("UNLOCK", fold_talk("破介这个软件")["folded"])


if __name__ == "__main__":
    unittest.main()
