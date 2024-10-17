from datetime import timedelta, datetime
import random
import pandas as pd

def pull_random_range(file_path, num_years, starting_date=None):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path, parse_dates=['Date'])

            # Sort by date to ensure it's ordered
            df = df.sort_values(by='Date')

            # Ensure the Date column is in datetime format

            # Get the date range from the DataFrame
            start_date = df['Date'].min()
            end_date = df['Date'].max()

            # Calculate the maximum allowed start date to ensure a full range of num_years
            max_start_date = end_date - timedelta(days=num_years * 400)

            # Ensure we are not starting too late in the data
            if max_start_date < start_date:
                raise ValueError(
                    "The dataset does not contain enough data for the specified number of years.")
            if starting_date is None:
                # Pick a random start date within the allowed range
                random_start_date = start_date + \
                    (max_start_date - start_date) * random.random()
            else:
                random_start_date = starting_date
            #print(random_start_date)
            # Calculate the end date based on the random start date
            random_end_date = random_start_date + timedelta(days=num_years * 400)

            # Filter the DataFrame to the selected date range
            mask = (df['Date'] >= random_start_date) & (df['Date'] <= random_end_date)
            selected_data = df.loc[mask]
            #print(random_start_date, random_end_date)
            return list(selected_data['Close'])

def pick_random_date(tick, num_years):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f'./stock_sim/database/{tick}.csv', parse_dates=['Date'])

    # Sort by date to ensure it's ordered
    df = df.sort_values(by='Date')

    # Ensure the Date column is in datetime format

    # Get the date range from the DataFrame
    start_date = df['Date'].min()
    end_date = df['Date'].max()

    # Calculate the maximum allowed start date to ensure a full range of num_years
    max_start_date = end_date - timedelta(days=num_years * 400)

    # Ensure we are not starting too late in the data
    if max_start_date < start_date:
        raise ValueError(
            "The dataset does not contain enough data for the specified number of years.")

    # Pick a random start date within the allowed range
    random_start_date = start_date + \
        (max_start_date - start_date) * random.random()
    #print(random_start_date, random_end_date)
    return random_start_date