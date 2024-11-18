import typing as T
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime as dt
from cashflow.utils.colors import colors
from cashflow.utils.logging_utils import init_logger

logger = init_logger()


class Income:
    def __init__(
        self,
        name: str = "income",
        monthly_amount: float = 50000,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = [],
        last_income_date: dt.date = dt.date(2050, 1, 1),
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d, a in zip(change_at_dates, change_by_amounts)}
        self.last_income_date = last_income_date
        self.monthly_amounts = pd.DataFrame(columns=["date", "amount"]).set_index(
            "date"
        )
        self.cumulative_amounts = pd.DataFrame(
            {"date": [today], "cumulative_amount": 0}
        ).set_index("date")
        self.last_date = today
        self.color = colors.get_color(type="income", name=name)
        self.plot_position = 0
        self.type = "Income"
        pass

    def payout(self) -> float:
        """Get monthly payout."""
        # Check for change
        assert (
            self.current_date not in self.monthly_amounts.index
        ), "You only earn this income once per month."
        self.monthly_amounts.loc[self.current_date] = self.monthly_amount
        self.cumulative_amounts.loc[self.current_date] = (
            self.monthly_amount + self.cumulative_amounts.loc[self.last_date]
        )
        self.last_date = self.current_date
        return self.monthly_amount

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        if self.current_date in self.change_dict:
            self.monthly_amount += self.change_dict.get(self.current_date)
        if self.current_date > self.last_income_date:
            self.monthly_amount = 0

    def get_summary(self):
        df = self.monthly_amounts.merge(
            self.cumulative_amounts, on="date", how="right", validate="1:1"
        )
        df["name"] = self.name
        self.summary = df
        return df


class Expense:
    def __init__(
        self,
        name: str = "expense",
        monthly_amount: float | None = None,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = [],
        is_credit_controlled: bool = False,
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d, a in zip(change_at_dates, change_by_amounts)}
        self.monthly_expenses = pd.DataFrame(columns=["date", "amount"]).set_index(
            "date"
        )
        self.cumulative_amounts = pd.DataFrame(
            {"date": [today], "cumulative_amount": 0}
        ).set_index("date")
        self.last_date = today
        self.color = colors.get_color(type="expense", name=name)
        self.plot_position = 1
        self.is_credit_controlled = is_credit_controlled
        self.type = "Expense"
        pass

    def spend(self, amount: float | None = None) -> float:
        """Spend monthly expenses."""
        # Check for change
        assert (
            self.current_date not in self.monthly_expenses.index
        ), "You can only spend this expense once per month."
        assert (amount is not None) or (
            self.monthly_amount is not None
        ), "You must either specify an amount here, or in the constructor."
        # If no amount is supplied, use fixed, specified amount
        if amount is None:
            amount = self.monthly_amount
        self.monthly_expenses.loc[self.current_date] = amount
        self.cumulative_amounts.loc[self.current_date] = (
            amount + self.cumulative_amounts.loc[self.last_date]
        )
        self.last_date = self.current_date
        return amount

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        if self.current_date in self.change_dict:
            self.monthly_amount += self.change_dict.get(self.current_date)
            pass

    def get_summary(self):
        df = self.monthly_expenses.merge(
            self.cumulative_amounts, on="date", how="right", validate="1:1"
        )
        df["name"] = self.name
        self.summary = df
        return df


class Saving:
    def __init__(
        self,
        name: str = "saving",
        initial_amount: float = 0,
        monthly_amount: float | None = None,
        interest_rate: float = 0,
        interest_frequency: str = "monthly",
        is_credit_controlled: bool = False,
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.initial_amount = initial_amount
        self.current_savings = initial_amount
        self.monthly_amount = monthly_amount
        self.interest_rate = interest_rate
        self.interest_frequency = interest_frequency
        self.monthly_amounts = pd.DataFrame(
            {"date": [today], "amount": initial_amount}
        ).set_index("date")
        self.monthly_interests = pd.DataFrame(columns=["date", "interest"]).set_index(
            "date"
        )
        self.cumulative_amount = pd.DataFrame(
            {"date": [today], "cumulative_amount": initial_amount}
        ).set_index("date")
        self.cumulative_interests = pd.DataFrame(
            {"date": [today], "cumulative_interests": 0}
        ).set_index("date")
        self.last_date = today
        self.color = colors.get_color(type="saving", name=name)
        self.is_credit_controlled = is_credit_controlled
        self.plot_position = 2
        self.type = "Saving"
        pass

    def deposit(self, amount: float | None = None):
        """Deposit amount on the account at the current date."""
        assert (
            self.current_date not in self.monthly_amounts.index
        ), f"{self.name} [{self.current_date}]: You can only make one deposit per month."
        assert (amount is not None) or (
            self.monthly_amount is not None
        ), f"{self.name} [{self.current_date}]: You must either specify an amount here, or in the constructor."
        # If no amount is supplied, use fixed, specified amount
        if amount is None:
            amount = self.monthly_amount
        # Update monthly deposit
        self.monthly_amounts.loc[self.current_date] = amount
        # Update cumulative deposit
        self.cumulative_amount.loc[self.current_date] = (
            amount + self.cumulative_amount.loc[self.last_date]
        )
        # update current savings
        self.current_savings += amount

        return amount

    def get_interests(
        self,
    ):
        """Get monthly interests."""
        if (self.interest_frequency == "annually") & (self.current_date.month != 1):
            interest_rate = 0
        else:
            interest_rate = self.interest_rate

        # Get interests
        interests = (
            self.cumulative_amount.loc[self.last_date].values
            + self.cumulative_interests.loc[self.last_date].values
        ) * interest_rate
        # update monthly interests
        self.monthly_interests.loc[self.current_date] = interests
        # Update cumulative interests
        self.cumulative_interests.loc[self.current_date] = (
            self.cumulative_interests.loc[self.last_date].values + interests
        )
        # update current savings
        self.current_savings += interests
        pass

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        pass

    def get_summary(self):
        df = self.monthly_amounts
        df = df.merge(self.cumulative_amount, on="date", how="right", validate="1:1")
        df = df.merge(self.monthly_interests, on="date", how="left", validate="1:1")
        df = df.merge(self.cumulative_interests, on="date", how="left", validate="1:1")
        df["cumulative_savings"] = df["cumulative_amount"] + df["cumulative_interests"]
        df = df[df.columns[[0, 1, 4, 2, 3]]]
        df["name"] = self.name
        self.summary = df
        return df


class Credit:
    def __init__(
        self,
        name="credit",
        credit_amount: float = 3000000,
        initial_payoff: float = 100000,
        loan_duration: int = 30,
        annual_interest_rate: float = 0.05,
    ):
        today = dt.date.today().replace(day=1)
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.initial_amount = initial_payoff
        self.credit = pd.DataFrame(
            {"date": [today], "credit": credit_amount - initial_payoff}
        ).set_index("date")
        self.annual_interest_rate = annual_interest_rate
        self.monthly_payment = (
            (1 + annual_interest_rate) ** (loan_duration - 1)
            / ((1 + annual_interest_rate) ** loan_duration - 1)
            * (credit_amount - initial_payoff)
            * annual_interest_rate
        ) / 12
        logger.info(
            f"CREDIT [{name}]: monthly payment amounts to {self.monthly_payment}."
        )
        self.interests = Expense(
            name=f"{self.name} (interests)", monthly_amount=0, is_credit_controlled=True
        )
        self.ownership = Saving(
            name=f"{self.name} (ownership)",
            monthly_amount=self.monthly_payment,
            is_credit_controlled=True,
        )
        self.month_counter = 0
        pass

    def update(self):
        self.last_date = self.current_date
        self.current_date += relativedelta(months=+1)
        self.month_counter += 1
        pass

    def payoff(self):
        self.interests.spend()
        self.ownership.deposit()
        self.credit.loc[self.current_date] = (
            self.credit.loc[self.last_date] - self.monthly_payment
        )
        return self.monthly_payment

    def add_interests(self):
        if self.month_counter % 12 == 0:
            interests = (
                self.credit.loc[self.current_date].values[0] * self.annual_interest_rate
            )
            self.credit.loc[self.current_date] += interests
            self.interests.monthly_amount = interests / 12
            self.ownership.monthly_amount = self.monthly_payment - interests / 12
        pass

    def get_summary(self):
        interests_summary = self.interests.get_summary()[
            ["amount", "cumulative_amount"]
        ]
        ownership_summary = self.ownership.get_summary()[
            ["amount", "cumulative_amount"]
        ]
        interests_summary = interests_summary.rename(
            columns={
                "amount": "interests",
                "cumulative_amount": "cumulative_interests",
            }
        )
        ownership_summary = ownership_summary.rename(
            columns={
                "amount": "saving",
                "cumulative_amount": "cumulative_saving",
            }
        )
        summary = interests_summary.merge(
            ownership_summary, on="date", how="inner", validate="1:1"
        )
        summary = summary.merge(self.credit, on="date", how="inner", validate="1:1")
        return summary


if __name__ == "__main__":
    c = Credit(annual_interest_rate=0.05)
    for month in range(30 * 12):
        c.update()
        c.interests.update()
        c.ownership.update()

        c.payoff()

        c.add_interests()

    df_summary = c.get_summary()
