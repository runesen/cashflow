import datetime as dt
import pandas as pd
import typing as T
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from budget.utils.logging_utils import init_logger
matplotlib.use('MacOSX')

logger = init_logger()

# we only consider time pr month
today = dt.date.today().replace(day=1)
#today = today + relativedelta(months=+1)
print(today)


class Income:
    def __init__(
        self,
        name: str,
        monthly_amount: float,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = []
    ):
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d,a in zip(change_at_dates, change_by_amounts)}
        self.monthly_amounts = pd.DataFrame(columns=['date', 'amount']).set_index('date')
        self.cumulative_amounts = pd.DataFrame({'date': [today], 'cumulative_amount': 0}).set_index('date')
        self.last_date = today
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
        return df

class Expense:
    def __init__(
        self,
        name: str,
        monthly_amount: float,
        change_at_dates: T.List[dt.date] = [],
        change_by_amounts: T.List[float] = []
    ):
        self.current_date = today  # internal date reference, to be updated continuously
        self.name = name
        self.monthly_amount = monthly_amount
        self.change_dict = {d: a for d,a in zip(change_at_dates, change_by_amounts)}
        self.monthly_expenses = pd.DataFrame(columns=['date', 'amount']).set_index('date')
        self.cumulative_amounts = pd.DataFrame({'date': [today], 'cumulative_amount': 0}).set_index('date')
        self.last_date = today
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
        return df


class Saving:
    def __init__(
        self,
        name: str,
        initial_amount: float,
        monthly_amount: float | None,
        monthly_interest_rate: float,
    ):
        self.name = name
        self.current_date = today  # internal date reference, to be updated continuously
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
        return df

class Budget:
    def __init__(
        self,
        incomes: T.List[Income],
        expenses: T.List[Expense],
        savings: T.List[Saving]
    ):
        self.incomes = incomes
        self.expenses = expenses
        self.savings = savings
        self.n_incomes = len(incomes)
        self.n_expenses = len(expenses)
        self.n_savings = len(savings)
        self.current_date = today
        self.income_summary = None
        self.expense_summary = None
        self.saving_summary = None
        pass

    def update(self) -> None:
        for i in self.incomes:
            i.update()
        for e in self.expenses:
            e.update()
        for s in self.savings:
            s.update()
            pass
        pass
    
    def get_summary(self):
        income_summary = pd.DataFrame()
        expense_summary = pd.DataFrame()
        saving_summary = pd.DataFrame()
        for i in self.incomes:
            income_summary = pd.concat(([income_summary, i.get_summary()]))
        for e in self.expenses:
            expense_summary = pd.concat(([expense_summary, e.get_summary()]))
        for s in self.savings:
            saving_summary = pd.concat(([saving_summary, s.get_summary()]))
        self.income_summary = income_summary
        self.expense_summary = expense_summary
        self.saving_summary = saving_summary
        pass
        

#############################################
# GET STATIC VARIABLES
#############################################


###############
# INCOME
###############
# Salary
current_income = 31000
changes_in_years = [2030, 2040, 2050, 2060]
changes_by_amounts = [5000, 5000, 5000, 5000]

###############
# EXPENSES
###############
# Rental
monthly_rent = 8500
# Fixed expenses
monthly_fixed_expenses = 1200
# Leisure
monthly_leisure_expenses = 5000

###############
# SAVINGS
###############
# Pension
pension_initial_deposit = 300000
pension_monthly_deposit = 5000
monthly_payment_dkk = 5000
pension_age_years = 69
pension_monthly_interest_rate = .02
folkepension_yearly_dkk = 80000

# Saving account variables
current_savings = 300000
savings_interest_rate = .01
savings_monthly_deposit = 2000

#############################################
# INSTANTIATE CLASSES
#############################################

salary_income = Income(
    name = "Salary",
    monthly_amount =  current_income,
)

rental_expense = Expense(
    name = "Rent",
    monthly_amount=monthly_rent,
)

fixed_expense = Expense(
    name = "Fixed",
    monthly_amount=monthly_fixed_expenses
)

leisure_expense = Expense(
    name = "Leisure",
    monthly_amount=monthly_leisure_expenses
)

pension_savings = Saving(
    name = "Pension",
    initial_amount=pension_initial_deposit,
    monthly_amount=pension_monthly_deposit,
    monthly_interest_rate=pension_monthly_interest_rate
)

deposit_savings = Saving(
    name = "Deposit Account",
    initial_amount=current_savings,
    monthly_amount=savings_monthly_deposit,
    monthly_interest_rate=savings_interest_rate
)

account_savings = Saving(
    name = "Bank Account",
    initial_amount=current_savings,
    monthly_amount=savings_monthly_deposit,
    monthly_interest_rate=savings_interest_rate
)

INCOMES = [
    salary_income
]

EXPENSES = [
    rental_expense,
    fixed_expense,
    leisure_expense,
]

SAVINGS = [
    pension_savings,
    deposit_savings,
    account_savings
]

budget = Budget(
    incomes=INCOMES,
    expenses=EXPENSES,
    savings=SAVINGS,
)

#############################################
# SIMULATE LIFE
#############################################

for month in range(100):
    budget.update()
    date = budget.incomes[0].current_date

    # payouts
    money = 0
    for income in budget.incomes:
        money += income.payout()
        pass

    # expenses
    for expense in budget.expenses:
        money = expense.spend(money)
        pass

    # savings
    for saving in budget.savings[:-1]:
        money = saving.deposit(money)
        pass

    # check balance
    if money < 0:
        if -money >= budget.savings[-1].get_current_savings():
            logger.error(f"{date}: You've run out of money!")
            break
        else:
            logger.warning(f"{date}: You're monthly balance is negative. Taking {-money} DKK out of your bank account.")

    # add remainder to bank account
    budget.savings[-1].deposit(money, money)

    # get interests
    for saving in budget.savings:
        money = saving.get_interests()
        pass

budget.get_summary()

# monthly budget at a certain timepoint
date = today + relativedelta(months=12)
fig, axes = plt.subplots()
positions = np.arange(0,3)
incomes_sum = 0
for i in budget.incomes:
    i_value = budget.income_summary.query(f'name == "{i.name}"').loc[date]['amount']
    axes.bar(x = positions[0], height = i_value, width = .75, label = i.name, bottom = incomes_sum)
    incomes_sum += i_value
savings_sum = 0
for s in budget.savings:
    s_value = budget.saving_summary.query(f'name == "{s.name}"').loc[date]['amount']
    axes.bar(x = positions[2], height = s_value, width = .75, label = s.name, bottom = savings_sum)
    savings_sum += s_value
expenses_sum = 0
for e in budget.expenses:
    e_value = budget.expense_summary.query(f'name == "{e.name}"').loc[date]['amount']
    axes.bar(x = positions[1], height = e_value, width = .75, label = e.name, bottom = expenses_sum + savings_sum)
    expenses_sum += e_value
axes.legend()
axes.set_xticks(positions)
axes.set_xticklabels(["Incomes", "Expenses", "Savings"])
axes.set_ylabel("Amount (DKK)")
axes.set_title(f"Monthly Budget ({date})")