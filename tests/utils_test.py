import pytest
from stock_sim.utils import pull_random_range, pick_random_date

def test_pick_random_date():
    """Test that a random date is picked correctly."""
    random_date = pick_random_date("^GSPC", 10)
    assert random_date.year >= 1927  # Ensure the date is within the expected range

def test_pull_random_range():
    """Test pulling a random data range from a CSV."""
    result = pull_random_range("./stock_sim/database/AAPL.csv", 5)
    assert len(result) > 0  # Ensure data is returned
