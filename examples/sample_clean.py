"""Clean example - should get low risk score."""
from typing import Optional

def calculate_total(items: list[float], discount: Optional[float] = None) -> float:
    """Calculate total with optional discount."""
    if not items:
        return 0.0
    if discount is not None:
        if not 0 <= discount <= 1:
            raise ValueError("discount must be 0-1")
        return round(sum(items) * (1 - discount), 2)
    return round(sum(items), 2)

def test_calculate_total():
    assert calculate_total([10, 20]) == 30
    assert calculate_total([10, 20], 0.1) == 27
