import numpy as np

tax_rates = {
    "virginia_us_tax_rates_single": {
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
            },
"florida_married_us_tax_rates": {
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
            },
"virginia_married_us_tax_rates": {
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

                }},
"andorra_tax_rates": {
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
                }},
"virginia_us_tax_rates_single_flat": {
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
            },
"virginia_us_tax_rates_married_flat": {
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

def get_monthly_cost(house_cost: float, interest_rate: float, term_length: float, down_pay_amt: float) -> float:
    """Calculates mortgage payment costs"""
    monthly_interest_rate: float = interest_rate / 12
    number_of_payments: float = term_length * 12

    monthly_payment: float = ((house_cost-down_pay_amt) *
                       (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
                       / ((1 + monthly_interest_rate) ** number_of_payments - 1))
    return monthly_payment
