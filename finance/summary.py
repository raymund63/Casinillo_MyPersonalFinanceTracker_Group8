"""finance.summary
Small helper functions to summarize financial records.

These are lightweight utilities you can import from the main app
to compute totals and simple aggregates.
"""
from typing import List, Dict


def total_by_type(records: List[Dict]) -> Dict[str, float]:
    """Return total amounts grouped by record_type ('expense' or 'income').

    Args:
        records: iterable of dict-like objects with keys 'amount' and 'record_type'.

    Returns:
        dict with sums for each record_type.
    """
    totals = {}
    for r in records:
        t = r.get('record_type', 'expense')
        amt = float(r.get('amount', 0))
        totals[t] = totals.get(t, 0.0) + amt
    return totals


def net_total(records: List[Dict]) -> float:
    """Compute net total (income - expenses).

    Treat records with 'record_type' == 'income' as positive, others as negative.
    """
    net = 0.0
    for r in records:
        amt = float(r.get('amount', 0))
        if r.get('record_type') == 'income':
            net += amt
        else:
            net -= amt
    return net
