"""tools.pretty_print
Small formatting helpers used across the project.
"""

def pretty_currency(amount: float, symbol: str = "₱") -> str:
    """Format a number as currency with two decimals and thousands separators.

    Examples:
        pretty_currency(1234.5) -> '₱1,234.50'
    """
    try:
        amt = float(amount)
    except (TypeError, ValueError):
        amt = 0.0
    negative = amt < 0
    amt = abs(amt)
    formatted = f"{amt:,.2f}"
    return f"-{symbol}{formatted}" if negative else f"{symbol}{formatted}"
