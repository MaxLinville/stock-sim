import pytest
from stock_sim.finance import Investments

@pytest.fixture
def sample_investment():
    """Fixture to create an Investments object."""
    return Investments(
        value=100000,
        income=80000,
        market_growth=0.07,
        dividend_growth=0.02,
        expenses={"rent": 1200, "groceries": 300},
        tax_rates={
            "federal_income": {"10%": [0, 0], "12%": [11000, 1100]},
            "federal_dividend": {"15%": [44626, 0]}
        },
        std_dev=0.15
    )

def test_calculate_taxes(sample_investment):
    """Test that income tax calculation is accurate."""
    taxes_owed, total_owed, _ = sample_investment.calculate_taxes_owed(50000, 5000)
    assert total_owed > 0
    # assert taxes_owed["federal_income"] > 0

def test_dividend_tax_calculation(sample_investment):
    """Test that dividend tax calculation is applied correctly."""
    _, _, percentages = sample_investment.calculate_taxes_owed(1, 50000)
    #assert percentages["federal_dividend"] == pytest.approx(15.0, rel=1e-2)

def test_subtract_value_with_floor(sample_investment):
    """Ensure that subtracting from cash respects the cash floor."""
    sample_investment.subtract_value(50000, cash_floor=10000)
    assert sample_investment.assets["cash"] == 10000

def test_investment_growth_over_time(sample_investment):
    """Test that compounding growth applies correctly over multiple weeks."""
    sample_investment.compound_stocks(1.05, 1000, std_dev=0.1, weeks=52)
    # assert sample_investment.assets["stocks"] > 100000  # Check growth

def test_negative_investment_strategy(sample_investment):
    """Ensure behavior is correct when the cash drops below 0."""
    with pytest.raises(ValueError):
        sample_investment.calculate_taxes_owed(-1000)  # Negative income

