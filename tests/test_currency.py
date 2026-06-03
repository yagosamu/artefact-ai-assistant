"""Tests for the currency converter HTTP layer.

All tests mock httpx via respx. They won't touch the real Frankfurter API.
"""

import httpx
import pytest
import respx

from artefact_ai_assistant.tools.currency import (
    FRANKFURTER_URL,
    fetch_conversion,
)


class TestFetchConversion:
    @respx.mock
    def test_happy_path_returns_parsed_dict(self):
        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "amount": 1000.0,
                    "base": "USD",
                    "date": "2025-12-03",
                    "rates": {"BRL": 5234.50},
                },
            )
        )

        result = fetch_conversion(1000, "usd", "brl")

        assert result["amount"] == 1000
        assert result["from"] == "USD"          # uppercased
        assert result["to"] == "BRL"
        assert result["converted"] == 5234.50
        assert result["rate"] == 5.2345          # 5234.50 / 1000
        assert result["date"] == "2025-12-03"

    @respx.mock
    def test_http_error_raises(self):
        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(422, json={"message": "not found"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            fetch_conversion(100, "USD", "XYZ")

    @respx.mock
    def test_missing_target_currency_raises(self):
        # Edge case: API returns 200 but the requested currency isn't in rates.
        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(
                200,
                json={"amount": 100.0, "base": "USD", "date": "x", "rates": {}},
            )
        )

        with pytest.raises(ValueError, match="Unknown target currency"):
            fetch_conversion(100, "USD", "BRL")

    @respx.mock
    def test_network_timeout_raises(self):
        respx.get(FRANKFURTER_URL).mock(side_effect=httpx.TimeoutException("slow"))

        with pytest.raises(httpx.TimeoutException):
            fetch_conversion(100, "USD", "BRL")

    @respx.mock
    def test_zero_amount_handles_division_safely(self):
        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(
                200,
                json={"amount": 0, "base": "USD", "date": "x", "rates": {"BRL": 0}},
            )
        )

        result = fetch_conversion(0, "USD", "BRL")
        assert result["rate"] == 0   # No ZeroDivisionError


class TestCurrencyToolWrapper:
    @respx.mock
    def test_invoke_returns_formatted_string(self):
        from artefact_ai_assistant.tools.currency import currency_converter

        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "amount": 1000.0,
                    "base": "USD",
                    "date": "2025-12-03",
                    "rates": {"BRL": 5234.50},
                },
            )
        )

        result = currency_converter.invoke({
            "amount": 1000,
            "from_currency": "USD",
            "to_currency": "BRL",
        })

        assert "5234.50 BRL" in result
        assert "2025-12-03" in result
        assert "rate" in result.lower()

    @respx.mock
    def test_invoke_returns_error_string_on_api_failure(self):
        from artefact_ai_assistant.tools.currency import currency_converter

        respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(422, json={"message": "not found"})
        )

        result = currency_converter.invoke({
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "XYZ",
        })

        assert result.startswith("Error")
        assert "422" in result

    def test_tool_metadata(self):
        from artefact_ai_assistant.tools.currency import currency_converter

        assert currency_converter.name == "currency_converter"
        assert "currency" in currency_converter.description.lower()
        assert "amount" in currency_converter.args
        assert "from_currency" in currency_converter.args
        assert "to_currency" in currency_converter.args