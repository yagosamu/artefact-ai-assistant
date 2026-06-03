"""Currency converter using the Frankfurter API (ECB rates, no auth needed).

https://api.frankfurter.app/latest?amount=1000&from=USD&to=BRL
"""


import httpx
from langchain_core.tools import tool

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def fetch_conversion(amount: float, from_currency: str, to_currency: str) -> dict:
    """Call Frankfurter and return a parsed result.

    Returns a dict with the converted amount, the implied rate, and the date
    of the quote. Raises httpx.HTTPError on network or HTTP failures, and
    ValueError if the response doesn't contain the requested target currency.
    """
    response = httpx.get(
        FRANKFURTER_URL,
        params={
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
        },
        timeout=10.0,
    )
    response.raise_for_status()
    data = response.json()

    converted = data.get("rates", {}).get(to_currency.upper())
    if converted is None:
        raise ValueError(f"Unknown target currency: {to_currency}")

    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "converted": converted,
        "rate": converted / amount if amount else 0,
        "date": data.get("date"),
    }

@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another using current ECB exchange rates.

    Use this when the user wants to convert money between currencies. Returns
    the converted amount along with the implied rate and the quote date.

    Args:
        amount: The amount to convert (e.g. 1500.50).
        from_currency: Source currency as 3-letter ISO code (e.g. "USD", "EUR").
        to_currency: Target currency as 3-letter ISO code (e.g. "BRL", "JPY").
    """
    try:
        result = fetch_conversion(amount, from_currency, to_currency)
    except ValueError as e:
        return f"Error: {e}"
    except httpx.HTTPStatusError as e:
        return f"Error: API returned {e.response.status_code}. Likely cause: invalid currency code."
    except httpx.HTTPError as e:
        return f"Error: could not reach exchange rate API — {e}"

    return (
        f"{result['amount']} {result['from']} = "
        f"{result['converted']:.2f} {result['to']} "
        f"(rate: {result['rate']:.4f}, as of {result['date']})"
    )