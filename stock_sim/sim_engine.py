'''
DOCSTRING
This module allows for development and testing of investment strategies from a high level
'''
from statistics import median
from multiprocessing import Pool
import numpy as np
import time

from stock_sim.utils import pick_random_date
from .finance import *
from .visualization import *
import cProfile
import pstats
import io
import os

def run_sim(**kwargs) -> list:
    '''
    Main numerical simulation method - weekly datapoints, quarterly dividends, paychecks, taxes
    '''
    # Assigning kwargs to local variables
    expenses = sum(kwargs['expenses'].values()) if isinstance(kwargs['expenses'], dict) else kwargs['expenses']
    annual_tax = kwargs['annualized_taxes']
    house_loan = kwargs['house_loan']
    down_pay_amt = kwargs['house_cost']*kwargs['down_pay_fraction']
    month_mortgage = get_monthly_cost(kwargs['house_cost'],
                                      kwargs['mortgage_interest_rate'],
                                      kwargs['loan_length'], down_pay_amt)
    house_start_year = kwargs['year_loan_start']
    cash_floor = kwargs['cash_floor']
    cash_ceiling = kwargs['cash_ceiling']
    retirement_income_goal = kwargs['retirement_income_goal']
    # Handle the dynamic 'start_date' field in config
    if kwargs['start_date'] == "random" and kwargs['backtest']:
        duration = kwargs["years"]
        start = pick_random_date(kwargs["backtest_ticker"], duration)
        kwargs['start_date'] = start
    # Setting up Investment class with starting params
    invest = Investments(
                        kwargs['start_cash'],
                        kwargs['income'],
                        kwargs['avg_growth'],
                        kwargs['dividend_growth'],
                        expenses,
                        kwargs['taxes'],
                        std_dev=kwargs['std_dev'],
                        years=kwargs['years'],
                        backtest=kwargs['backtest'], 
                        fixed_start_date=kwargs['start_date'],
                        tick=kwargs['backtest_ticker']
                        )
    invest.assets['stocks'] = kwargs['start_cash']
    invest.assets['cash'] = 0
    invest.assets['bonds'] = 0

    # Defining flags and precomputed values
    min_cash = {"val": kwargs['start_cash'], "year": -1}
    pre_tax_dividend = kwargs['pre_tax_dividend']
    assets_over_time = [0]
    cash_over_time = [0]
    was_negative = [False, False]
    retirement_year = -1
    weekly_expenses = invest.get_weekly_expenses() if isinstance(expenses, dict) else expenses*12/52
    if kwargs['use_avg_growth']:
        invest.std_dev = 0
    div_tax = 0

    # Main loop staged between years and weeks (52 weeks per year)
    for year in range(invest.years):
        invest.week = 0
        # Handling yearly events and checks
        if year == kwargs['cash_injection_year']:
            invest.add_cash(kwargs['cash_injection_amt'], cash_floor)
        if kwargs['promotion']['enabled'] and year in kwargs['promotion']['years']:
            promotion_year_index = kwargs['promotion']['years'].index(year)
            invest.set_income(kwargs['promotion']['salaries'][promotion_year_index])

        house_loan_month = month_mortgage if year > house_start_year and house_loan else 0
        if year == house_start_year and house_loan:
            invest.subtract_value(down_pay_amt, cash_floor)

        house_loan_month = 0 if year > house_start_year + kwargs['loan_length'] else house_loan_month

        house_payment_week = house_loan_month*12/52
        weekly_income = invest.get_weekly_income()
        annual_dividends = 0

        for week in range(1,53):
            '''
            Biweekly paycheck, calculate the net cash gain, run the compounding formula after
            investing a fixed percentage of income or cash, and calculate dividends once per quarter
            '''
            net_week = 0
            post_tax = 0
            curr_cash = invest.assets['cash']
            if curr_cash < min_cash['val'] and year > 0:
                min_cash['val'] = curr_cash
                min_cash['year'] = year
            if week%2 == 0:
                net_week = weekly_income - weekly_expenses - house_payment_week
                post_tax = (2*net_week if annual_tax
                            else (2*net_week-2*invest.calculate_taxes_owed_cached(invest.income)[1]/52))
                #print(f"Net week: {net_week}, post-tax: {post_tax}, weekly income: {weekly_income}, weekly_expenses: {weekly_expenses}")
                invest.add_cash(post_tax, cash_floor)
            invest.run_investment_strategy(post_tax, strategy=kwargs['strategy'],
                                           invest_factor=kwargs['invest_factor'],
                                           cash_base_factor=kwargs['cash_base_factor'],
                                           cash_base_amt=kwargs['cash_base_amt'],
                                           cash_ceiling = cash_ceiling)
            if week%13 == 0: # finds quarters
                dividend = invest.get_dividends()
                if (pre_tax_dividend):
                    tax_amt = invest.calculate_taxes_owed_cached(invest.income, dividend / 4)[0]['federal_dividend']
                    #print("Div to tax:", dividend, tax_amt)
                    invest.assets['stocks'] += dividend-tax_amt
                else:
                    invest.assets['stocks'] += dividend
                annual_dividends += dividend
            if kwargs['check_negative']:
                val = invest.get_asset_value()
                assets_over_time.append(val)
                cash = invest.assets['cash']
                cash_over_time.append(cash)
                was_negative[0] = True if cash < 0 else was_negative[0]
                was_negative = [True, True] if val < 0 else was_negative
            invest.week += 1
            if invest.calculate_passive_income(kwargs['retirement_usage']) >= retirement_income_goal and retirement_year == -1:
                retirement_year = year
        # Subtract taxes once per year
        if annual_tax:
            tax_amt = invest.calculate_taxes_owed_cached(invest.income, annual_dividends)[1]
            div_tax = tax_amt
            invest.subtract_value(tax_amt)
        elif (not pre_tax_dividend):
            tax_amt = invest.calculate_taxes_owed_cached(invest.income, annual_dividends)[0]['federal_dividend']
            div_tax = tax_amt
            invest.subtract_value(tax_amt)
        invest.income *= kwargs['raise_factor']
        invest.year += 1
    if min_cash['year'] == -1:
        min_cash['val'] = cash_ceiling
    vals = [
            invest.get_income(),
            invest.get_all_values(),
            invest.calculate_passive_income(kwargs['retirement_usage']),
            [assets_over_time, cash_over_time],
            div_tax,
            was_negative,
            min_cash,
            retirement_year
            ]
    #print(f"Contributions: {invest.contributions}, Assets: {invest.get_all_values()[1]}, Net Growth: {invest.get_all_values()[1]-invest.contributions}")
    return vals

def multiprocess_sim(parameter: dict) -> tuple[float, float, float, bool, dict]:
    '''
    For use within multiprocessing to allow the simulations to be run and resultant independently
    '''
    # profile_dir = "profiles"
    # if not os.path.exists(profile_dir):
    #     os.makedirs(profile_dir)
    # pr = cProfile.Profile()
    # pr.enable()

    # Your simulation logic here
    results = run_sim(**parameter)

    # pr.disable()
    
    # # Save profiling data to a binary file (e.g., .prof)
    # profile_file = os.path.join(profile_dir, f"profile_worker_{os.getpid()}.prof")
    # pr.dump_stats(profile_file)

    net_assets = results[1][0] + results[1][1]
    cash_results = results[1][0]
    div_tax = results[4]
    was_negative = results[5]
    min_cash = results[6]['val']
    retirement_year = results[7]

    return net_assets, cash_results, div_tax, was_negative, min_cash, retirement_year

def run_2v_sims(params: dict, dimX: dict, dimY: dict) -> dict:
    '''
    Observe large scale effects resulting from changing two variables
    '''
    # dimX format: {min_x, max_x, x_increment, x_parameter}
    # Simulation variable bound assignment
    params['use_avg_growth'] = True

    min_x = dimX['min']
    max_x = dimX['max']
    x_increment = dimX['increment']

    min_y = dimY['min']
    max_y = dimY['max']
    y_increment = dimY['increment']

    raw_x = []
    x_set = []
    raw_y = []
    y_set = []

    # Defining the set of values to be used in the x-axis
    if (isinstance(min_x, float) or isinstance(max_x, float) or isinstance(x_increment, float)):
        min_x = int(min_x * 1000)
        max_x = int(max_x * 1000)
        x_increment = int(x_increment * 1000)
        raw_x = [float(n)/1000 for n in range(min_x, max_x + 1, x_increment)]
        x_set = list(enumerate(raw_x))
    elif (dimX['name'] == "promotion"):
        pass
    else:
        raw_x = list(range(min_x, max_x + 1, x_increment))
        x_set = list(enumerate(raw_x))

    # Defining the set of values to be used in the y-axis
    if (isinstance(min_y, float) or isinstance(max_y, float) or isinstance(y_increment, float)):
        min_y = int(min_y * 1000)
        max_y = int(max_y * 1000)
        y_increment = int(y_increment * 1000)
        raw_y = [float(n)/1000 for n in range(min_y, max_y + 1, y_increment)]
        y_set = list(enumerate(raw_y))
    elif dimY['name'] == "promotion":
        pass
    else:
        raw_y = list(range(min_y, max_y + 1, y_increment))
        y_set = list(enumerate(raw_y))

    # Defining empty arrays to populate with results
    net_assets = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    cash_results = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    div_tax = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    contained_negative = [[[False, False] for _ in range(len(y_set))] for _ in range(len(x_set))]
    min_cash = [[{"val": 0, "year": -1} for _ in range(len(y_set))] for _ in range(len(x_set))]
    retirement_year = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    # Setting up an array of modified parameters based on the changing variables in multiprocessing
    param_list = [[{} for _ in range(len(y_set))] for _ in range(len(x_set))]
    for x in enumerate(x_set):
        for y in enumerate(y_set):
            params[dimX['name']] = x[1][1]
            params[dimY['name']] = y[1][1]
            param_list[x[0]][y[0]] = dict(params)

    # Multiprocessing to handle running each simulation on separate threads in parallel (timed)
    print(len(param_list), len(param_list[0]))
    iterations = len(param_list) * len(param_list[0])
    iteration_idx = 0
    start_time = time.perf_counter()
    with Pool() as pool:
        '''
        Each 1D array within the 2D list of modified parameters
        is passed into the pool for multiprocessing, where the
        results are expanded to populate the result value arrays
        in their corresponding indices
        '''
        for param in enumerate(param_list):
            print(f'Batch {iteration_idx}/{len(param_list)}')
            iteration_idx += 1
            multisim_results = pool.map(multiprocess_sim, param[1])
            for n in enumerate(multisim_results):
                net_assets[param[0]][n[0]],\
                cash_results[param[0]][n[0]],\
                div_tax[param[0]][n[0]], contained_negative[param[0]][n[0]], \
                min_cash[param[0]][n[0]], retirement_year[param[0]][n[0]] = n[1]
                
    end_time = time.perf_counter()
    print(f"The simulation took {end_time-start_time:,.2f} seconds")

    # Determine how to transform the raw cash values to a tax ratio
    if params['display_tax_ratio']:
        for n in enumerate(cash_results):
            for m in enumerate(n[1]):
                tax_val = div_tax[n[0]][m[0]]
                # binary scale
                current_cash_result = cash_results[n[0]][m[0]]
                cash_tax_ratios = {
                    'primary_target': [2*tax_val, 4*tax_val, 0.5, 0.5],
                    'secondary_target': [1.5*tax_val, 10*tax_val, 0.25, 0.75],
                    'ternary_target': [1.1*tax_val, 50*tax_val, 0.1, 0.9],
                    'quaternary_target': [1*tax_val, 100*tax_val, 0.05, 0.95],
                }
                tax_factor = 0
                for bracket in cash_tax_ratios.values():
                    if bracket[0] <= current_cash_result <= bracket[1]:
                        tax_factor = (bracket[2] if (current_cash_result <
                                                median([cash_tax_ratios['primary_target'][0],
                                                        cash_tax_ratios['primary_target'][1]]))
                                                else bracket[3])
                        break
                if current_cash_result > cash_tax_ratios['quaternary_target'][1]:
                    tax_factor = 1
                if contained_negative[n[0]][m[0]][0] or contained_negative[n[0]][m[0]][1]:
                    tax_factor = -0.1
                cash_results[n[0]][m[0]] = tax_factor

    # Handling data to be plotted
    med_assets = np.median(net_assets)
    med_cash = np.median(cash_results)
    print(f"Median Net Assets: {med_assets:,.2f}\nMedian Net Cash: {med_cash:,.2f}")

    z = net_assets
    ztitle = "Liquid Assets ($)"

    z2 = min_cash
    z2title="Resulting Cash ($)"
    if params['display_tax_ratio']:
        z2title = "Cash-Tax Ratio Bracket (0-1)"
    create_3d_graph(raw_y, raw_x, z, dimY['name'], dimX['name'], ztitle, z2, z2title,
                   params['display_tax_ratio'], params['check_negative'])
    return ({"Net": z, "Cash": cash_results, "min_cash": min_cash, "retirement_year": retirement_year})

def run_stat_sim(params: dict, sim_count: int = 100) -> None:
    '''
    Generate a distribution of results from time variant samples with fixed parameters
    '''
    # Set up arrays and parameters for results
    params['use_avg_growth'] = False
    sims = list(range(sim_count))
    net_assets = list(range(sim_count))
    cash_results = list(range(sim_count))

    # Prepare an array of parameters to feed into the multiprocessor
    param_set = [params for _ in range(sim_count)]

    # Multiprocessing used to run the each simulation, unordered
    start_time = time.perf_counter()
    with Pool() as pool:
        results = pool.imap_unordered(multiprocess_sim, param_set)
        for n in enumerate(results):
            print(n[0])
            net_assets[n[0]] = n[1][0]
            cash_results[n[0]] = n[1][1]
    end_time = time.perf_counter()

    # Handling results for plotting
    x = sims
    y = net_assets
    ytitle = "Net Assets ($)"
    print(f"The simulation took {end_time-start_time:,.2f} seconds")
    print(
        f"""Med. Cash:\t{np.median(cash_results):,.2f}
        Med. Net Assets:\t{np.median(net_assets):,.2f}"""
        )
    create_stat_graph(x, y, ytitle)

def run_stat_sim_retirement(params: dict, sim_count: int = 100) -> None:
    '''
    Generate a distribution of results from time variant samples with fixed parameters
    '''
    # Set up arrays and parameters for results
    params['use_avg_growth'] = False
    sims = list(range(sim_count))
    retirement_year = list(range(sim_count))
    cash_results = list(range(sim_count))

    # Prepare an array of parameters to feed into the multiprocessor
    param_set = [params for _ in range(sim_count)]

    # Multiprocessing used to run the each simulation, unordered
    start_time = time.perf_counter()
    with Pool() as pool:
        results = pool.imap_unordered(multiprocess_sim, param_set)
        for n in enumerate(results):
            print(n[0])
            retirement_year[n[0]] = n[1][5]
            cash_results[n[0]] = n[1][1]
    end_time = time.perf_counter()

    # Handling results for plotting
    x = sims
    y = retirement_year
    ytitle = "Net Assets ($)"
    print(f"The simulation took {end_time-start_time:,.2f} seconds")
    print(
        f"""Med. Cash:\t{np.median(cash_results):,.2f}
        Med. Net Assets:\t{np.median(retirement_year):,.2f}"""
        )
    create_stat_graph(x, y, ytitle)

def run_time_sim(params: dict) -> None:
    '''
    Observe how fixed parameter settings change over time
    '''
    params['is_multi_sim'] = False
    results = run_sim(**params)
    result_data = results[3]
    print(f"Passive income: {results[2]}")
    x = list(range(52 * params['years'] + 1))
    y = result_data[0]
    y2 = result_data[1]
    xtitle = "Year"
    ytitle = "Liquid Assets ($)"
    y2title = "Available Cash"
    create_2d_time_graph(x, y, xtitle, ytitle, y2, y2title)

def main() -> None:
    """Main function for selecting sims"""
    # Parameter set to be parsed into any simulation form
    pass

if __name__ == '__main__':
    main()
