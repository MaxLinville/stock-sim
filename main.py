import json
from datetime import datetime, timedelta
from stock_sim.sim_engine import run_2v_sims, run_stat_sim, run_time_sim, run_stat_sim_retirement
from stock_sim.finance import tax_rates
from stock_sim.utils import pick_random_date
from stock_sim.optimization import find_best_2v
import pandas as pd
import os
import cProfile
import pstats

def load_config(file_path):
    """ Load configuration from a JSON file """
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def main():
    # Load the parameters from the config file
    current_path = os.path.dirname(__file__)
    filename = "idealConfig"
    config_path = f"./stock_sim/database/configs/{filename}.json"
    params = load_config(os.path.join(current_path,config_path))
    
    # Convert the tax bracket identifier from the string in the config to the actual tax rates
    params['taxes'] = tax_rates[params['taxes']]

    # Uncomment any simulation you want to run
    # run_stat_sim(params, 500)
    # run_stat_sim_retirement(params, 500)
    run_time_sim(params)
    # run_2v_sims(params, 
    #             {'min': 0, 'max': 1, 'increment': 0.1, 'name': 'cash_base_factor'},
    #             {'min': 0, 'max': 1, 'increment': 0.1, 'name': 'invest_factor'}
    #             )

    # Run the optimization simulation
    # find_best_2v(params, 
    #             {'min': 0.01, 'max': 1, 'increment': 0.01, 'name': 'invest_factor'},
    #             {'min': 66000, 'max': 150000, 'increment': 1000, 'name': 'income'})

if __name__ == '__main__':
    main()
