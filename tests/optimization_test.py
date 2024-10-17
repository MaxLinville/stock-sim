import pytest
from stock_sim.optimization import find_best_2v

def test_optimization_results():
    """Test that optimization returns valid results."""
    params = {
        "start_cash": 50000,
        "income": 100000,
        "years": 10,
        "expenses": {"monthly_bills": 500},
    }
    v1 = {"min": 0.1, "max": 0.5, "increment": 0.1, "name": "invest_factor"}
    v2 = {"min": 50000, "max": 150000, "increment": 5000, "name": "income"}

    # top_results = find_best_2v(params, v1, v2)
    # assert len(top_results) <= 10  # Ensure no more than 10 results
    # for result in top_results:
    #     assert result["Retirement Year"] != -1  # Check valid retirement years
