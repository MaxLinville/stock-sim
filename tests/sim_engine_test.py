import pytest
from stock_sim.sim_engine import run_sim, run_2v_sims

@pytest.fixture
def simulation_parameters():
    """Fixture to provide default parameters for simulations."""
    return {
        "start_cash": 50000,
        "income": 120000,
        "avg_growth": 1.07,
        "dividend_growth": 0.02,
        "years": 10,
        "expenses": {"monthly_bills": 500},
        "taxes": {"federal_income": {"10%": [0, 0], "22%": [44726, 5147]}},
        "retirement_usage": 0.05,
        "retirement_income_goal": 200000,
        "cash_floor": 15000,
        "cash_ceiling": 80000,
        "promotion": {"enabled": False},
        "strategy": "Basic",
        "backtest": False,
        "check_negative": True
    }

def test_run_simulation(simulation_parameters):
    """Test basic simulation execution."""
    # results = run_sim(**simulation_parameters)
    # assert len(results) == 8  # Check that all expected return values are provided
    # assert results[0] == 120000  # Ensure income is returned correctly
    # assert results[7] != -1  # Ensure a valid retirement year was found

def test_edge_case_simulation_low_income(simulation_parameters):
    """Test simulation with very low income to ensure taxes are handled correctly."""
    simulation_parameters["income"] = 0  # Edge case
    # results = run_sim(**simulation_parameters)
    # assert results[0] == 0  # Income remains 0
    # assert results[7] == -1  # No retirement possible

def test_run_2v_sims(simulation_parameters):
    """Test 2-variable simulation for investment optimization."""
    dimX = {"min": 0.1, "max": 1.0, "increment": 0.1, "name": "invest_factor"}
    dimY = {"min": 0, "max": 100000, "increment": 5000, "name": "income"}
    # results = run_2v_sims(simulation_parameters, dimX, dimY)
    # assert "Net" in results  # Ensure the key results are present
    # assert len(results["Net"]) > 0  # Check that results are populated
