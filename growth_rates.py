'''
DOCSTRING
This module allows for development and testing of investment strategies from a high level
'''
from statistics import median
from multiprocessing import Pool
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec
from matplotlib.colors import LinearSegmentedColormap

PERCENT_USE_AFTER_RETIREMENT = 0.05

# Global Tax rates to use as a selection
virginia_us_tax_rates_single: dict = {
                "federal": {
                    "dividend": {
                        "0%": [0, 0],
                        "15%": [44626, 0],
                        "20%": [492301, 0]
                    },
                    "income": {
                        "10%": [0, 0],
                        "12%": [11000, 1100],
                        "22%": [44726, 5147],
                        "24%": [95376, 16290],
                        "32%": [182101, 37104],
                        "35%": [231251, 52832],
                        "37%": [578126, 174238]
                    },
                    "medicare": {
                        "1.45%": [0,0]
                    },
                    "social_security": {
                        "6.2%": [0,0],
                        "0%": [147000, 9114]
                    }
                },
                "state": { # Virginia State Tax, Florida would be 0%
                    "income": { # additive to federal
                        "2%": [0, 0],
                        "3%": [3001, 60],
                        "5%": [5001, 120],
                        "5.75%": [17001, 720]
                    }
                },
                "other": {

                }
            }
florida_married_us_tax_rates: dict = {
                "federal": {
                    "dividend": {
                        "0%": [0, 0],
                        "15%": [83350, 0],
                        "20%": [517201, 0]
                    },
                    "income": {
                        "10%": [0, 0],
                        "12%": [22000, 2200],
                        "22%": [89451, 10294],
                        "24%": [190751, 32580],
                        "32%": [364201, 74208],
                        "35%": [462501, 105664],
                        "37%": [693751, 186601]
                    },
                    "medicare": {
                        "1.45%": [0,0]
                    },
                    "social security": {
                        "6.2%": [0,0],
                        "0%": [147000, 9114]
                    }
                },
                "other": {

                }
            }
virginia_married_us_tax_rates: dict = {
                "federal": {
                    "dividend": {
                        "0%": [0, 0],
                        "15%": [83350, 0],
                        "20%": [517201, 0]
                    },
                    "income": {
                        "10%": [0, 0],
                        "12%": [22000, 2200],
                        "22%": [89451, 10294],
                        "24%": [190751, 32580],
                        "32%": [364201, 74208],
                        "35%": [462501, 105664],
                        "37%": [693751, 186601]
                    },
                    "medicare": {
                        "1.45%": [0,0]
                    },
                    "social security": {
                        "6.2%": [0,0],
                        "0%": [147000, 9114]
                    }
                },
                "state": {
                    "income": { # additive to federal
                        "2%": [0, 0],
                        "3%": [3001, 60],
                        "5%": [5001, 120],
                        "5.75%": [17001, 720]
                    }
                },
                "other": {

                }}
andorra_tax_rates: dict = {
                "federal": {
                    "dividend": {
                        "0%": [0, 0],
                        "15%": [44626, 0],
                        "20%": [492301, 0]
                    },
                    "income": {
                        "0%": [0, 0],
                        "10%": [42334, 0],
                    }
                }}

virginia_us_tax_rates_single_flat: dict = {
                "federal_income": {
                        "10%": [0, 0],
                        "12%": [11000, 1100],
                        "22%": [44726, 5147],
                        "24%": [95376, 16290],
                        "32%": [182101, 37104],
                        "35%": [231251, 52832],
                        "37%": [578126, 174238]
                    },
                "federal_dividend": {
                        "0%": [0, 0],
                        "15%": [44626, 0],
                        "20%": [492301, 0]
                    },
                "state_income": {
                        "2%": [0, 0],
                        "3%": [3001, 60],
                        "5%": [5001, 120],
                        "5.75%": [17001, 720]
                    },
                "federal_medicare":{
                        "1.45%": [0,0]
                    },
                "federal_social-security": {
                        "6.2%": [0,0],
                        "0%": [147000, 9114]
                    },
            }

virginia_us_tax_rates_married_flat: dict = {
                "federal_income": {
                        "10%": [0, 0],
                        "12%": [22000, 2200],
                        "22%": [89451, 10294],
                        "24%": [190751, 32580],
                        "32%": [364201, 74208],
                        "35%": [462501, 105664],
                        "37%": [693751, 186601]
                    },
                "federal_dividend": {
                        "0%": [0, 0],
                        "15%": [83350, 0],
                        "20%": [517201, 0]
                    },
                "state_income": {
                        "2%": [0, 0],
                        "3%": [3001, 60],
                        "5%": [5001, 120],
                        "5.75%": [17001, 720]
                    },
                "federal_medicare":{
                        "1.45%": [0,0]
                    },
                "federal_social-security": {
                        "6.2%": [0,0],
                        "0%": [147000, 9114]
                    },
            }

class Investments:
    '''
    Financial Portfolio including all asset types and functions to handle how they change
    '''
    def __init__(self, value: float, income: float, market_growth: float, dividend_growth: float, expenses: dict,
                tax_rates: dict, assets: dict=None, std_dev: float=0):
        if assets is None:
            assets = {'cash': 0, 'stocks': 0, 'bonds': 0}
        self.income = income # Annual income
        self.market_growth = market_growth # Current market growth average
        self.dividend_growth = dividend_growth # Dividend yields
        self.expenses = expenses # Monthly Expenses
        self.tax_rates = tax_rates # Tax bracket values chosen
        self.assets = assets # Dictionary of all asset valuations
        self.assets['stocks'] += value
        self.std_dev = std_dev # Average volatility

    def calculate_tax_bracket(self, income: float) -> dict:
        '''
        Calculates the tax bracket based on income
        and the tax brackets chosen for the portfolio
        '''
        tax_bracket: dict = {}
        for tax_type, brackets in self.tax_rates.items():
            applicable_rate = None
            highest_threshold = -1

            for rate, (threshold, _) in brackets.items():
                if highest_threshold < threshold < income:
                    applicable_rate = rate
                    highest_threshold = threshold

            if applicable_rate is not None:
                tax_bracket[tax_type] = applicable_rate

        return tax_bracket

    def calculate_taxes_owed(self, income: float, dividends: float=0) -> tuple[dict, float, dict]:
        '''
        Returns raw taxes owed from income, total owned including dividend growth,
        and realized tax %
        '''
        if income <= 0:
            raise ValueError("Income must be greater than 0")

        tax_brackets: dict = self.calculate_tax_bracket(income)
        taxes_owed: dict = {}
        total_owed: float = 0.0

        for tax_type, rate_key in tax_brackets.items():
            threshold, base_tax = self.tax_rates[tax_type][rate_key]
            percentage = float(rate_key[:-1]) / 100

            if "dividend" in tax_type:
                tax_amount = percentage * dividends
            else:
                tax_amount = base_tax + percentage * (income - threshold)
            
            if "social-security" in tax_type and percentage == 0 and income >= 147_000:
                tax_amount = 147_000*0.062

            taxes_owed[tax_type] = tax_amount
            total_owed += tax_amount

        real_tax_percentages: dict = {tax: 100 * amount / income for tax, amount in taxes_owed.items()}
        real_tax_percentages["total"] = 100 * total_owed / income

        return taxes_owed, total_owed, real_tax_percentages

    def get_income(self) -> float:
        """Returns annual income"""
        return self.income

    def set_income(self, amount: float) -> None:
        """Sets annual income to new value"""
        self.income = amount

    def add_cash(self, amt: float, floor: float) -> None:
        """Cash increase due to paycheck"""
        if amt < 0:
            self.subtract_value(-1*amt, floor)
        else:
            self.assets['cash'] += amt

    def get_weekly_income(self) -> float:
        """Calculates weekly income for paycheck approximation"""
        return (self.income)/52

    def get_weekly_expenses(self) -> float:
        """Calculates weekly expenses from monthly expenses"""
        return sum(self.expenses.values())*12/52

    def get_asset_value(self) -> float:
        """Returns the total valuation of all assets"""
        return sum(self.assets.values())

    def get_all_values(self) -> list[float, float, float]:
        """Returns cash, stock, and bond values"""
        return [self.assets['cash'], self.assets['stocks'], self.assets['bonds']]

    def assets_to_string(self) -> str:
        """Formats assets into a string"""
        asset_string = ("Cash: " + str(self.assets['cash']) + "\n" +
                        "Stocks: " + str(self.assets['stocks']) + "\n" +
                        "Bonds: " + str(self.assets['bonds']) + "\n" +
                        "Total: " + str(self.get_asset_value()))
        return asset_string

    def invest_in_etf(self, amount: float) -> None:
        """Converts cash into stock holdings, assumed to be etf for long term growth"""
        if self.assets['cash'] >= amount:
            self.assets['stocks'] += amount
            self.assets['cash'] -= amount
        else:
            # print("out of cash")
            pass

    def subtract_value(self, amount: float, cash_floor: float = 0) -> None:
        '''
        Removes cash and assets in preferred order based on a value
        '''
        if amount < self.assets['cash'] - cash_floor:
            self.assets['cash'] -= amount
            amount = 0
            return
        amount -= (self.assets['cash']-cash_floor)
        self.assets['cash'] = cash_floor
        if amount >= self.assets['stocks']:
            amount -= self.assets['stocks']
            self.assets['stocks'] = 0
        else:
            self.assets['stocks'] -= amount
            amount = 0
            return
        if amount >= self.assets['bonds']:
            amount -= self.assets['bonds']
            self.assets['bonds'] = 0
        else:
            self.assets['bonds'] -= amount
            amount = 0
            return
        if amount > 0:
            self.assets['cash'] -= amount
            amount = 0
        return

    def get_dividends(self) -> float:
        """Returns quarterly dividends"""
        # print(f"Stocks: {self.assets['stocks']:,.2f}, Growth: {self.dividend_growth:,.2f}")
        return self.assets['stocks']*self.dividend_growth/4

    def compound_stocks(self, rate: float, contribution: float, std_dev: float=0, weeks: int=1) -> None:
        """Applies compounding model to stock growth and handles investment event"""
        if std_dev != 0:
            period_std_deviation = std_dev / (52 / weeks)**0.5
            period_growth = (rate - 1) * weeks / 52
            growth = 1 + np.random.normal(period_growth, period_std_deviation)
        else:
            growth = 1 + weeks * (rate - 1) / 52
        self.assets['stocks'] *= growth
        self.invest_in_etf(contribution)

    def calculate_passive_income(self, percent_use_after_retirement: float) -> float:
        """Calculates the average income from investments"""
        return (self.assets['stocks']*percent_use_after_retirement
                - self.calculate_taxes_owed(self.income, (self.assets['stocks']
                * percent_use_after_retirement))[0]['federal_dividend'])

    def run_investment_strategy(self, post_tax: float, strategy: str="Basic", invest_factor: float=0.25,
                                cash_base_factor: float = 0.05, cash_base_amt: float = 75000) -> None:
        '''
        This is where strategies can be tested and assigned a name
        '''
        invest_amount = 0
        cash = self.assets['cash']
        match strategy:
            case "Basic":
                invest_amount = invest_factor*post_tax
            case "NWFraction":
                invest_amount = invest_factor*cash
            case "SafeNWFraction":
                invest_amount = ((invest_factor*cash+invest_factor*post_tax)
                                if cash > cash_base_amt else invest_factor*post_tax)
            case "SafeNWCashFraction":
                # Cash base factor is the percent of net asset value held
                # in cash to start investing from cash reserve
                invest_amount = ((invest_factor*cash+invest_factor*post_tax)
                                if cash > cash_base_factor*self.get_asset_value()
                                else invest_factor*post_tax)
            case "NWTaxRatio":
                invest_amount = 0
            case "template3":
                invest_amount = 0
            case "NoInvest":
                invest_amount = 0
            case _:
                invest_amount = 0
        self.compound_stocks(self.market_growth, invest_amount, self.std_dev)

def run_sim(**kwargs) -> list:
    '''
    Main numerical simulation method - weekly datapoints, quarterly dividends, paychecks, taxes
    '''
    # Assigning kwargs to local variables
    expenses: dict = kwargs['expenses']
    annual_tax = kwargs['annualized_taxes']
    house_loan = kwargs['house_loan']
    down_pay_amt = kwargs['house_cost']*kwargs['down_pay_fraction']
    month_mortgage = get_monthly_cost(kwargs['house_cost'],
                                      kwargs['mortgage_interest_rate'],
                                      kwargs['loan_length'], down_pay_amt)
    house_start_year = kwargs['year_loan_start']
    cash_floor = kwargs['cash_floor']

    # Setting up Investment class with starting params
    invest = Investments(
                        kwargs['start_cash'],
                        kwargs['income'],
                        kwargs['avg_growth'],
                        kwargs['dividend_growth'],
                        expenses,
                        kwargs['taxes'],
                        std_dev=kwargs['std_dev']
                        )
    invest.assets['stocks'] = kwargs['start_cash']
    invest.assets['cash'] = 0
    invest.assets['bonds'] = 0

    # Defining flags and precomputed values
    assets_over_time = [0]
    cash_over_time = [0]
    was_negative = [False, False]
    weekly_expenses = invest.get_weekly_expenses() if isinstance(expenses, dict) else expenses*12/52
    if kwargs['use_avg_growth']:
        invest.std_dev = 0
    div_tax = 0

    # Main loop staged between years and weeks (52 weeks per year)
    for year in range(kwargs['years']):
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
            if week%2 == 0:
                net_week = weekly_income - weekly_expenses - house_payment_week
                post_tax = (2*net_week if annual_tax
                            else (2*net_week-2*invest.calculate_taxes_owed(invest.income)[1]/52))
                invest.add_cash(post_tax, cash_floor)
            invest.run_investment_strategy(post_tax, strategy=kwargs['strategy'],
                                           invest_factor=kwargs['invest_factor'],
                                           cash_base_factor=kwargs['cash_base_factor'],
                                           cash_base_amt=kwargs['cash_base_amt'])
            if week%13 == 0: # finds quarters
                dividend = invest.get_dividends()
                invest.assets['stocks'] += dividend
                annual_dividends += dividend
            if kwargs['check_negative']:
                val = invest.get_asset_value()
                assets_over_time.append(val)
                cash = invest.assets['cash']
                cash_over_time.append(cash)
                was_negative[0] = True if cash < 0 else was_negative[0]
                was_negative = [True, True] if val < 0 else was_negative

        # Subtract taxes once per year
        if annual_tax:
            tax_amt = invest.calculate_taxes_owed(invest.income, annual_dividends)[1]
            div_tax = tax_amt
            invest.subtract_value(tax_amt)
        else:
            tax_amt = invest.calculate_taxes_owed(invest.income, annual_dividends)[0]['federal_dividend']
            div_tax = tax_amt
            invest.subtract_value(tax_amt)
        invest.income *= kwargs['raise_factor']
    vals = [
            invest.get_income(),
            invest.get_all_values(),
            invest.calculate_passive_income(PERCENT_USE_AFTER_RETIREMENT),
            [assets_over_time, cash_over_time],
            div_tax,
            was_negative
            ]
    return vals

def get_monthly_cost(house_cost: float, interest_rate: float, term_length: float, down_pay_amt: float) -> float:
    """Calculates mortgage payment costs"""
    monthly_interest_rate: float = interest_rate / 12
    number_of_payments: float = term_length * 12

    monthly_payment: float = ((house_cost-down_pay_amt) *
                       (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
                       / ((1 + monthly_interest_rate) ** number_of_payments - 1))
    return monthly_payment

def create_3d_graph(x: list, y: list, z: list, xtitle: str, ytitle: str, ztitle: str, z2: list=None, z2title: str="",
                    tax_ratio: bool=False, check_negative: bool=False) -> None:
    '''
    Creates a heatmap of liquid assets and cash on hand from the results of a 2-variable simulation
    '''
    if z2 is None:
        z2 = []
    fig = plt.figure(figsize = (20,10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if np.abs(x) < 1e3:
            return f"{x:.2f}"
        if np.abs(x) < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def ratio_formatter(x: float, pos) -> str:
        """Foramts axis labels based on the cash-tax ratio"""
        if x == 0.5:
            return "Optimal 2-4x Tax"
        if 0.25 <= x <= 0.75:
            return "Near Optimal 1.5-10x Tax"
        if 0.10 <= x <= 0.90:
            return "Feasible 1.1-50x Tax"
        if 0.05 <= x <= 0.95:
            return "Extreme Boundaries 1-100x Tax"
        if x == -0.1:
            return "Negative Cash Reached"
        return "Not Usable"


    (X, Y) = np.meshgrid(x, y)
    Z = np.array(z)
    Z2 = np.array(z2)

    mesh = ax1.pcolormesh(X, Y, Z, shading='auto', cmap = plt.cm.gist_ncar_r)
    mesh2 = ax2.pcolormesh(X, Y, Z2, shading='auto', cmap = plt.cm.gist_ncar_r) if not tax_ratio\
            else ax2.pcolormesh(X, Y, Z2, shading='auto',
                            cmap = LinearSegmentedColormap.from_list('rg',
                            ["white", "darkred", "gold", "g", "aquamarine", "darkblue"], N=256))

    # Set axis labels
    ax1.set_xlabel(f"{xtitle}", labelpad=20)
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax2.set_xlabel(f"{xtitle}", labelpad=20)
    ax2.set_ylabel(f"{ytitle}", labelpad=20)

    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    # Liquid Assets labels
    Z1bounds = [int(min(Z.flatten())),int(max(Z.flatten()))]
    Z1Diff = Z1bounds[1]-Z1bounds[0]
    print(Z1bounds, Z1Diff)
    cbar = fig.colorbar(mesh, ticks=list(range(Z1bounds[0],Z1bounds[1],Z1Diff//20 or 1)))
    cbar.formatter = FuncFormatter(millions_formatter)
    cbar.set_label(f"{ztitle}")

    # Resulting Cash/tax ratio Labels
    tax_ratio_vals = [-0.1, 0, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1]

    Z2bounds = [min(Z2.flatten()),max(Z2.flatten())]
    Z2Diff = Z2bounds[1]-Z2bounds[0]
    print(Z2bounds, Z2Diff, int(int(Z2bounds[0]*100)), int(Z2bounds[1]*100+1))
    cbar2 = fig.colorbar(mesh2, ticks=tax_ratio_vals if tax_ratio\
                        else list(range(Z2bounds[0],Z2bounds[1],Z2Diff//20 or 1)))
    cbar2.formatter = FuncFormatter(millions_formatter if not tax_ratio else ratio_formatter)
    cbar2.set_label(f"{z2title}")
    cbar.update_ticks()

    # Plot displays
    plt.tight_layout()
    plt.show()

def create_stat_graph(x: list, y: list, ytitle: str) -> None:
    '''
    Creates a box-and-whisker plot/scatter plot from statistical simulation to show %ile ranges
    '''
    fig = plt.figure(figsize = (20,6))

    def millions_formatter_text(x: float) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 4])
    ax1 = plt.subplot(gs[0])
    med = np.median(y)
    miny=np.min(y)
    maxy=np.max(y)
    percentile_25 = np.percentile(y, 25)
    percentile_75 = np.percentile(y, 75)
    percentile_5 = np.percentile(y, 5)
    percentile_95 = np.percentile(y, 95)
    errIQR = [[med-percentile_25], [percentile_75-med]]
    err90 = [[med-percentile_5], [percentile_95-med]]

    ax1.errorbar(x=1, y=med, yerr=err90, fmt='o', color='orange',label = '5-95% Percentiles')
    ax1.errorbar(x=1, y=med, yerr=errIQR, fmt='o', color='blue', label = '25-75% Percentiles')
    ax1.scatter(1,miny, color='red', label = 'Min Value')
    ax1.scatter(1,maxy, color='green', label = 'Max Value')
    ax1.text(1.005, miny, f'Min: ${millions_formatter_text(miny)}',
                    verticalalignment='center', color='red')
    ax1.text(1.005, maxy, f'Max: ${millions_formatter_text(maxy)}',
                    verticalalignment='center', color='green')
    ax1.text(1.005, med, f'Median: ${millions_formatter_text(med)}',
                    verticalalignment='center', color='purple')
    ax1.text(1.005, percentile_5, f'5th Percentile: ${millions_formatter_text(percentile_5)}',
                    verticalalignment='center', color='orange')
    ax1.text(1.005, percentile_25, f'25th Percentile: ${millions_formatter_text(percentile_25)}',
                    verticalalignment='center', color='blue')
    ax1.text(1.005, percentile_75, f'75th Percentile: ${millions_formatter_text(percentile_75)}',
                    verticalalignment='center', color='blue')
    ax1.text(1.005, percentile_95, f'95th Percentile: ${millions_formatter_text(percentile_95)}',
                    verticalalignment='center', color='orange')
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax1.set_xticks([])
    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax1.legend()

    ax2 = plt.subplot(gs[1])
    ax2.scatter(x,y,marker='.',s=10)
    # ax2.set_ylabel("Result Assets ($)")
    ax2.set_yticks([])
    ax2.set_xlabel("Simulation Result # ")
    # ax2.set_ylim(bottom=0, top=3 * mean)
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax1.grid(color='grey', linestyle='-', linewidth=0.5)
    ax2.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def create_2d_time_graph(x: list, y: list, xtitle: str, ytitle: str, y2: list, y2title: str) -> None:
    '''
    Line graph of liquid assets and cash vs time with resolution of a week from the time simulation
    '''
    fig = plt.figure(figsize = (20,6))

    def millions_formatter_text(x: float) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def year_formatter(x: float, pos) -> str:
        """Converts week number to year"""
        return f"{x // 52}"

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0])
    ax1.plot(x, y, color='black')
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax1.set_xlabel(f"{xtitle}", labelpad= 20)
    ax1.set_xticks([52*n for n in range(len(x)//52+1)])
    ax1.xaxis.set_major_formatter(FuncFormatter(year_formatter))
    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax1.legend()

    ax2 = plt.subplot(gs[1])
    ax2.plot(x,y2, color='black')
    ax2.set_ylabel(f"{y2title}")
    ax2.set_xlabel(f"{xtitle}", labelpad=20)
    ax2.set_xticks([52*n for n in range(len(x)//52+1)])
    ax2.xaxis.set_major_formatter(FuncFormatter(year_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax1.grid(color='grey', linestyle='-', linewidth=0.5)
    ax2.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def multiprocess_sim(parameter: dict) -> tuple[float, float, float, bool]:
    '''
    For use within multiprocessing to allow the simulations to be run and resultant independently
    '''
    # print(f"inner loop start \n{parameter}\n inner loop end\n")
    results = run_sim(**parameter)
    net_assets = results[1][0] + results[1][1]
    cash_results = results[1][0]
    div_tax = results[4]
    was_negative = results[5]
    # print(x[0], x[1], y[0], y[1], cash_results[x[0]][y[0]])
    return net_assets, cash_results, div_tax, was_negative

def run_2v_sims(params: dict, dimX: int, dimY: int) -> None:
    '''
    Observe large scale effects resulting from changing two variables
    '''
    # dimX format: [min_x, max_x, x_increment, x_parameter]
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
    else:
        raw_y = list(range(min_y, max_y + 1, y_increment))
        y_set = list(enumerate(raw_y))

    # Defining empty arrays to populate with results
    net_assets = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    cash_results = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    div_tax = [[0 for _ in range(len(y_set))] for _ in range(len(x_set))]
    contained_negative = [[[False, False] for _ in range(len(y_set))] for _ in range(len(x_set))]

    # Setting up an array of modified parameters based on the changing variables in multiprocessing
    param_list = [[{} for _ in range(len(y_set))] for _ in range(len(x_set))]
    for x in enumerate(x_set):
        for y in enumerate(y_set):
            params[dimX['name']] = x[1][1]
            params[dimY['name']] = y[1][1]
            param_list[x[0]][y[0]] = dict(params)

    # Multiprocessing to handle running each simulation on separate threads in parallel (timed)
    print(len(param_list), len(param_list[0]))
    start_time = time.perf_counter()
    with Pool() as pool:
        '''
        Each 1D array within the 2D list of modified parameters
        is passed into the pool for multiprocessing, where the
        results are expanded to populate the result value arrays
        in their corresponding indices
        '''
        for param in enumerate(param_list):
            multisim_results = pool.map(multiprocess_sim, param[1])
            for n in enumerate(multisim_results):
                net_assets[param[0]][n[0]],\
                cash_results[param[0]][n[0]],\
                div_tax[param[0]][n[0]], contained_negative[param[0]][n[0]] = n[1]
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

    z2 = cash_results
    z2title="Resulting Cash ($)"
    if params['display_tax_ratio']:
        z2title = "Cash-Tax Ratio Bracket (0-1)"
    create_3d_graph(raw_y, raw_x, z, dimY['name'], dimX['name'], ztitle, z2, z2title,
                    params['display_tax_ratio'], params['check_negative'])

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

def run_time_sim(params: dict) -> None:
    '''
    Observe how fixed parameter settings change over time
    '''
    params['is_multi_sim'] = False
    results = run_sim(**params)[3]
    x = list(range(52 * params['years'] + 1))
    y = results[0]
    y2 = results[1]
    xtitle = "Year"
    ytitle = "Liquid Assets ($)"
    y2title = "Available Cash"
    create_2d_time_graph(x, y, xtitle, ytitle, y2, y2title)

def main() -> None:
    """Main function for selecting sims"""
    # Parameter set to be parsed into any simulation form
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
        'taxes': virginia_us_tax_rates_married_flat,
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
        }
    }
    run_time_sim(params)
    #run_2v_sims(params,	{"min": 75_000,	"max": 250_000, "increment": 5_000,	"name": "income"},
    #                   {"min": 0,"max": 1, "increment": 0.01,	"name": "invest_fraction"})

    # run_stat_sim(params, 5000)
    #
    # Try to put ax1.text in a function by zipping values together
    #

if __name__ == '__main__':
    main()
