"""Tests for safe_calculate.

Two groups: correctness (does the math) and safety (rejects anything that
isn't math). The safety group is the whole point of using AST.
"""

import pytest

from artefact_ai_assistant.tools.calculator import safe_calculate


class TestCorrectness:
    @pytest.mark.parametrize(
        "expression,expected",
        [
            ("1 + 1", 2),
            ("128 * 46", 5888),
            ("10 - 3", 7),
            ("20 / 4", 5.0),
            ("(2 + 3) * 4", 20),
            ("2 ** 10", 1024),
            ("-5 + 10", 5),
            ("7 % 3", 1),
            ("10 // 3", 3),
            ("1.5 + 2.5", 4.0),
        ],
    )
    def test_basic_arithmetic(self, expression, expected):
        assert safe_calculate(expression) == expected


class TestSafety:
    @pytest.mark.parametrize(
        "malicious",
        [
            "__import__('os').system('echo pwned')",
            "open('test.txt', 'w').write('boom')",
            "exec('print(1)')",
            "lambda: 1",
            "1 if True else 2",
            "[1, 2, 3]",
        ],
    )
    def test_rejects_non_math(self, malicious):
        with pytest.raises((ValueError, SyntaxError)):
            safe_calculate(malicious)

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            safe_calculate("1 / 0")

    def test_invalid_syntax(self):
        with pytest.raises(SyntaxError):
            safe_calculate("1 + + +")


class TestToolWrapper:
    """The @tool wrapper layer. It verifies LangChain integration shape."""

    def test_invoke_returns_string_result(self):
        from artefact_ai_assistant.tools.calculator import calculator
        assert calculator.invoke({"expression": "128 * 46"}) == "5888"

    def test_invoke_returns_error_string_on_bad_input(self):
        from artefact_ai_assistant.tools.calculator import calculator
        result = calculator.invoke({"expression": "__import__('os')"})
        assert result.startswith("Error")

    def test_invoke_returns_error_string_on_division_by_zero(self):
        from artefact_ai_assistant.tools.calculator import calculator
        result = calculator.invoke({"expression": "1 / 0"})
        assert "division by zero" in result

    def test_tool_metadata(self):
        from artefact_ai_assistant.tools.calculator import calculator
        assert calculator.name == "calculator"
        assert "math" in calculator.description.lower()
        # args_schema é gerado pela LangChain a partir do type hint
        assert "expression" in calculator.args.keys()