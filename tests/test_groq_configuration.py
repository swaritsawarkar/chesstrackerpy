import ast
import io
import pathlib
import unittest
from contextlib import redirect_stdout


SOURCE_PATH = pathlib.Path(__file__).parents[1] / "cv_chess_play.py"


def load_analyze_game_without_app_startup():
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    analyze_game = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "analyze_game"
    )
    module = ast.Module(body=[analyze_game], type_ignores=[])
    namespace = {"GROQ_API_KEY": ""}
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["analyze_game"]


class GroqConfigurationTests(unittest.TestCase):
    def test_missing_key_skips_optional_explanation_before_engine_use(self):
        analyze_game = load_analyze_game_without_app_startup()
        output = io.StringIO()

        with redirect_stdout(output):
            analyze_game([])

        self.assertIn("GROQ_API_KEY is not set", output.getvalue())


if __name__ == "__main__":
    unittest.main()
