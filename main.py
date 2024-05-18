# main.py

from stock_sim.sim_engine import run_2v_sims, run_stat_sim, run_time_sim
from stock_sim.finance import tax_rates

def main():
    # Define your parameters
    params: dict = {
        'start_cash': 0, # Original amount of cash from year 0
        'years': 25, # Length of simulations
        'income': 90_000, # Initial income, updated with raises or promotions
        # Monthly expenses:
        # keys are for readability to the user as they get grouped in the simulation
        'expenses': {
                    'monthly_bills': 600,
                    'groceries': 500,
                    'transportation': 200,
                    'other-goods': 1500,
                    'insurance': 380,
                    'property_taxes': 600,
                    },
        # Select which tax bracket to use from the global list
        'taxes': tax_rates["virginia_us_tax_rates_married_flat"],
        # Generic factor to be used in the designed investing strategy
        'invest_factor': 0.5,
        'avg_growth': 1.07,
        'dividend_growth': 0.02,
        'annualized_taxes': False,
        'house_loan': True,
        'monthly_loan_payment': -1, # Defined in simulation
        'house_cost': 600_000, # Raw cost of house
        'mortgage_interest_rate': 0.06, # Interest rate attached to house financing
        'year_loan_start': 10,
        'down_pay_fraction': 0.03, # Fraction of house cost to down pay
        'loan_length': 15, # Loan term for house (15 or 30 years most common for house)
        'use_avg_growth': False, # Use the idealized market trends when simulating
        'std_dev': 0.15, # Market growth typical standard deviation (volatility)
        'strategy': "SafeNWCashFraction",
        'is_multi_sim': True, # Flag to reduce excessive computation
        'cash_base_factor': 0.125, # Generic factor to be used in the designed investing strategy
        'cash_base_amt': 75000, # Generic value to be used in the designed investing strategy
        'figure_num': 1, # Unused
        'display_tax_ratio': True,
        'cash_floor': 25000, # Determine the minimum amount of cash to avoid going under
        'raise_factor': 1.03, # Cost of living annual raises (3% default)
        'cash_injection_year': -1, # Year for one time cash gift
        'cash_injection_amt': 0, # Amount of cash for cash injection
        'check_negative': True, # Report if cash and/or liquid assets ever became a negative value
        'promotion': {
            'salaries': [120_000, 2],
            'years': [5, 25],
            'enabled': False
        },
        'retirement_usage': 0.05
    }
    
    run_2v_sims(params, 
                {'min': 100_000, 'max': 1_000_000, 'increment': 1_000, 'name': 'income'},
                {'min': 1.00, 'max': 1.20, 'increment': 0.001, 'name': 'avg_growth'}
                )

if __name__ == '__main__':
    main()
