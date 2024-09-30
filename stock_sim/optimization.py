from .sim_engine import run_2v_sims, run_stat_sim, run_time_sim

def find_best_2v(params: dict, v1: dict, v2: dict, min_cash_threshold=10000):
    multi_results = run_2v_sims(params, v1, v2)
    
    # Initialize a list to collect all results
    all_results = []

    # Iterate over the simulation results to collect all results
    for ridx in range(len(multi_results['Net'])):
        for vidx in range(len(multi_results['Net'][0])):
            # Map indices to input parameter values
            v1_value = v1['min'] + v1['increment'] * ridx
            v2_value = v2['min'] + v2['increment'] * vidx

            net_value = multi_results['Net'][ridx][vidx]
            cash_value = multi_results['Cash'][ridx][vidx]
            min_cash_value = multi_results['min_cash'][ridx][vidx]
            retirement_year_value = multi_results['retirement_year'][ridx][vidx]

            # Skip results where retirement is not possible (e.g., retirement_year_value is None or -1)
            if retirement_year_value is None or retirement_year_value == -1:
                continue

            # Collect the result only if min_cash is above the threshold
            if min_cash_value >= min_cash_threshold:
                all_results.append({
                    v1['name']: v1_value,
                    v2['name']: v2_value,
                    'Retirement Year': retirement_year_value,
                    'Net': net_value,
                    'min_cash': min_cash_value
                })
    
    # If no results meet the criteria, inform the user
    if not all_results:
        print("No results meet the criteria.")
        return

    # Sort the results by Retirement Year (ascending), then by Net (descending)
    sorted_results = sorted(
        all_results, 
        key=lambda x: (x['Retirement Year'], -x['Net'])
    )

    # Select the top 10 results
    top_10_results = sorted_results[:10]

    # Print the top 10 results
    for idx, result in enumerate(top_10_results, start=1):
        print(f"Rank {idx}: {v1['name']}: {result[v1['name']]:,.3f}, "
              f"{v2['name']}: {result[v2['name']]:,.3f}, "
              f"Retirement Year: {result['Retirement Year']}, "
              f"Net: ${result['Net']:,.2f}, "
              f"Min Cash: ${result['min_cash']:,.2f}")
