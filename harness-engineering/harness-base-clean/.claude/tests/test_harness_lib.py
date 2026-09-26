from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import support  # noqa: F401  (configura sys.path)
import harness_lib as hl

try:
    import yaml  # PyYAML, opcional: solo para comprobar paridad
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

SAMPLE = """version: 1
title: "Titulo: con dos puntos #1"
quoted: 'It''s ok'
flow: [FR-01, "NFR-02"]
empty_list: []
empty_map: {}
number: 3
ratio: 0.25
flag: false
nothing: null
block: |
  linea 1
  # no es comentario
folded: >-
  una
  frase
long_plain: texto que
  continua aqui
items:
  - id: AC-001
    covers: [FR-01]
  - plain item
nested:
  a:
    b: 1
  list_same_indent:
  - x
"""


class YamlSubsetTests(unittest.TestCase):
    def test_parses_supported_subset(self) -> None:
        data = hl.loads_yaml(SAMPLE)
        self.assertEqual("Titulo: con dos puntos #1", data["title"])
        self.assertEqual("It's ok", data["quoted"])
        self.assertEqual(["FR-01", "NFR-02"], data["flow"])
        self.assertEqual("linea 1\n# no es comentario\n", data["block"])
        self.assertEqual("una frase", data["folded"])
        self.assertEqual("texto que continua aqui", data["long_plain"])
        self.assertEqual({"id": "AC-001", "covers": ["FR-01"]}, data["items"][0])
        self.assertEqual(["x"], data["nested"]["list_same_indent"])

    @unittest.skipIf(yaml is None, "PyYAML no instalado")
    def test_matches_pyyaml(self) -> None:
        self.assertEqual(yaml.safe_load(SAMPLE), hl.loads_yaml(SAMPLE))

    def test_dump_roundtrip(self) -> None:
        data = {"a": "x: y", "b": ["1", "yes", ""], "c": {"d": None, "e": [{"f": 1.5}]}, "g": "multi\nline", "h": []}
        text = hl.dumps_yaml(data)
        self.assertEqual(data, hl.loads_yaml(text))
        if yaml is not None:
            self.assertEqual(data, yaml.safe_load(text))

    def test_dump_never_writes_unreadable_state(self) -> None:
        data = {"response": "@diego revisa el alcance", "reason": "- no", "x": "&ancla", "y": "!tag", "z": "a: b"}
        self.assertEqual(data, hl.loads_yaml(hl.dumps_yaml(data)))
        with tempfile.TemporaryDirectory() as tmp:
            hl.dump_yaml(Path(tmp) / "state.yaml", data)
            self.assertEqual(data, hl.load_yaml(Path(tmp) / "state.yaml"))

    def test_rejects_unsupported_or_ambiguous_yaml(self) -> None:
        for bad in ("a: b: c", "a: &x 1", "a: 1\na: 2", "a:\n\tb: 1", "a: [1, [2]]", "a: 'open"):
            with self.subTest(bad=bad), self.assertRaises(hl.YamlError):
                hl.loads_yaml(bad)

    def test_frontmatter_accepts_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_bytes("\ufeff---\nname: demo\ndescription: prueba\n---\n# demo\n".encode("utf-8"))
            self.assertEqual("demo", hl.frontmatter(path)["name"])


if __name__ == "__main__":
    unittest.main()
