import typing as T
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime as dt
from budget.utils.colors import colors


class Income:
    def __init__(
        self,
        name: str,
        monthly_amount: float,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = [],

    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d,a in zip(change_at_dates, change_by_amounts)}
        self.monthly_amounts = pd.DataFrame(columns=['date', 'amount']).set_index('date')
        self.cumulative_amounts = pd.DataFrame({'date': [today], 'cumulative_amount': 0}).set_index('date')
        self.last_date = today
        self.color = colors.get_color(type='income')
        self.plot_position = 0
        pass

    def payout(self) -> float:
        """Get monthly payout."""
        # Check for change
        assert self.current_date not in self.monthly_amounts.index, "You only earn this income once per month."
        self.monthly_amounts.loc[self.current_date] = self.monthly_amount
        self.cumulative_amounts.loc[self.current_date] = (
            self.monthly_amount +
            self.cumulative_amounts.loc[self.last_date]
        )
        self.last_date = self.current_date
        return self.monthly_amount

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        if self.current_date in self.change_dict:
            self.monthly_amount += self.change_dict.get(self.current_date)
            pass

    def get_summary(self):
        df = self.monthly_amounts.merge(self.cumulative_amounts, on='date', how='right', validate='1:1')
        df['name'] = self.name
        self.summary = df
        return df


class Expense:
    def __init__(
        self,
        name: str,
        monthly_amount: float,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = []
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d,a in zip(change_at_dates, change_by_amounts)}
        self.monthly_expenses = pd.DataFrame(columns=['date', 'amount']).set_index('date')
        self.cumulative_amounts = pd.DataFrame({'date': [today], 'cumulative_amount': 0}).set_index('date')
        self.last_date = today
        self.color = colors.get_color(type='expense')
        self.plot_position = 1
        pass

    def spend(self, money: float, amount: float | None = None) -> float:
        """Spend monthly expenses."""
        # Check for change
        assert self.current_date not in self.monthly_expenses.index, "You can only spend this expense once per month."
        assert (amount is not None) or (self.monthly_amount is not None), \
            "You must either specify an amount here, or in the constructor."
        # If no amount is supplied, use fixed, specified amount
        if amount is None:
            amount = self.monthly_amount
        self.monthly_expenses.loc[self.current_date] = amount
        self.cumulative_amounts.loc[self.current_date] = (
            amount +
            self.cumulative_amounts.loc[self.last_date]
        )
        self.last_date = self.current_date
        return money - amount

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        if self.current_date in self.change_dict:
            self.monthly_amount += self.change_dict.get(self.current_date)
            pass

    def get_summary(self):
        df = self.monthly_expenses.merge(self.cumulative_amounts, on='date', how='right', validate='1:1')
        df['name'] = self.name
        self.summary = df
        return df


class Saving:
    def __init__(
        self,
        name: str,
        initial_amount: float,
        monthly_amount: float | None,
        monthly_interest_rate: float,
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.initial_amount = initial_amount
        self.current_savings = initial_amount
        self.monthly_amount = monthly_amount
        self.monthly_interest_rate = monthly_interest_rate
        self.monthly_amounts = pd.DataFrame(columns=['date', 'amount']).set_index('date')
        self.monthly_interests = pd.DataFrame(columns=['date', 'interest']).set_index('date')
        self.cumulative_amount = pd.DataFrame({'date': [today], 'cumulative_amount': initial_amount}).set_index(
            'date')
        self.cumulative_interests = pd.DataFrame({'date': [today], 'cumulative_interests': 0}).set_index('date')
        self.last_date = today
        self.color = colors.get_color(type='saving')
        self.plot_position = 2
        pass

    def deposit(
        self,
        money: float,
        amount: float | None = None
    ):
        """Deposit amount on the account at the current date."""
        assert self.current_date not in self.monthly_amounts.index, "You can only make one deposit per month."
        assert (amount is not None) or (self.monthly_amount is not None), \
            "You must either specify an amount here, or in the constructor."
        # If no amount is supplied, use fixed, specified amount
        if amount is None:
            amount = self.monthly_amount
        # Update monthly deposit
        self.monthly_amounts.loc[self.current_date] = amount
        # Update cumulative deposit
        self.cumulative_amount.loc[self.current_date] = (
            amount +
            self.cumulative_amount.loc[self.last_date]
        )
        return money - amount

    def get_interests(
        self,
    ):
        """Get monthly interests."""
        # Get interests
        self.monthly_interests.loc[self.current_date] = (
            (
                self.cumulative_amount.loc[self.last_date].values +
                self.cumulative_interests.loc[self.last_date].values
            ) * self.monthly_interest_rate)
        # Update cumulative interests
        self.cumulative_interests.loc[self.current_date] = (
            self.monthly_interests.loc[self.current_date].values +
            self.cumulative_interests.loc[self.last_date].values
        )
        pass

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        pass

    def get_current_savings(self):
        cumulative_amount = self.cumulative_amount.loc[self.current_date]
        cumulative_interests = self.cumulative_interests.loc[self.current_date]
        return cumulative_amount + cumulative_interests

    def get_summary(
        self
    ):
        df = self.monthly_amounts
        df = df.merge(self.cumulative_amount, on='date', how="right", validate="1:1")
        df = df.merge(self.monthly_interests, on='date', how="left", validate="1:1")
        df = df.merge(self.cumulative_interests, on='date', how="left", validate="1:1")
        df["cumulative_savings"] = df["cumulative_amount"] + df["cumulative_interests"]
        df = df[df.columns[[0, 1, 4, 2, 3]]]
        df['name'] = self.name
        self.summary = df
        return df
