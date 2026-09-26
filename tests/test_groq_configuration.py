import ast
import io
import os
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


def load_start_engine_without_app_startup():
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    start_engine = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "start_engine"
    )
    module = ast.Module(body=[start_engine], type_ignores=[])
    namespace = {"os": os}
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["start_engine"]


def load_finish_game_without_app_startup(save_pgn, analyze_game):
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    finish_game = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "finish_game"
    )
    module = ast.Module(body=[finish_game], type_ignores=[])
    namespace = {"save_pgn": save_pgn, "analyze_game": analyze_game}
    exec(compile(module, str(SOURCE_PATH), "exec"), namespace)
    return namespace["finish_game"]


class GroqConfigurationTests(unittest.TestCase):
    def test_two_player_recording_needs_no_engine_without_groq(self):
        start_engine = load_start_engine_without_app_startup()
        self.assertIsNone(start_engine(2, None, "missing-stockfish.exe"))

    def test_ai_play_requires_engine(self):
        start_engine = load_start_engine_without_app_startup()
        with self.assertRaises(FileNotFoundError):
            start_engine(1, None, "missing-stockfish.exe")

    def test_pgn_is_saved_before_optional_analysis_fails(self):
        saved = []

        def save_pgn(moves, mode):
            saved.append((moves, mode))

        def analyze_game(moves):
            raise RuntimeError("Groq is unavailable")

        finish_game = load_finish_game_without_app_startup(save_pgn, analyze_game)
        with self.assertRaisesRegex(RuntimeError, "Groq is unavailable"):
            finish_game(["move"], 2)
        self.assertEqual(saved, [(["move"], 2)])

    def test_missing_key_skips_optional_explanation_before_engine_use(self):
        analyze_game = load_analyze_game_without_app_startup()
        output = io.StringIO()

        with redirect_stdout(output):
            analyze_game([])

        self.assertIn("GROQ_API_KEY is not set", output.getvalue())


if __name__ == "__main__":
    unittest.main()
