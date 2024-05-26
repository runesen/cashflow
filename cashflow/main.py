import datetime as dt
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from cashflow.engines.budget_class import Budget
from cashflow.engines.components import Income, Expense, Saving, Credit
from cashflow.utils.logging_utils import init_logger
import matplotlib
from cashflow.utils.plotting import plot_budget_across_time, plot_aggregated_budget
matplotlib.use('MacOSX')

logger = init_logger()

# we only consider time pr month
today = dt.date.today().replace(day=1)
#today = today + relativedelta(months=+1)
print(today)

#############################################
# GET STATIC VARIABLES
#############################################


###############
# INCOME
###############
# Salary
current_income = 40000
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


###############
# CREDITS
###############
real_estate_credit = 3000000
real_estate_initial_payment = 300000
real_estate_annual_interests = 0.05
real_estate_credit_duration = 30



#############################################
# INSTANTIATE CLASSES
#############################################

salary_income = Income(
    name = "Salary",
    monthly_amount =  current_income,
    change_at_dates=[dt.date(2025, 1, 1), dt.date(2027, 1, 1), dt.date(2030, 1, 1)],
    change_by_amounts=[1000, 3000, 4000]
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
    interest_rate=pension_monthly_interest_rate,
    interest_frequency="monthly"
)

deposit_savings = Saving(
    name = "Deposit Account",
    initial_amount=current_savings,
    monthly_amount=savings_monthly_deposit,
    interest_rate=savings_interest_rate,
    interest_frequency="monthly"
)

account_savings = Saving(
    name = "Bank Account",
    initial_amount=current_savings,
    monthly_amount=savings_monthly_deposit,
    interest_rate=savings_interest_rate,
    interest_frequency="monthly"
)

real_estate = Credit(
    name="real_estate",
    initial_payoff=real_estate_initial_payment,
    loan_duration=real_estate_credit_duration,
    annual_interest_rate=real_estate_annual_interests,
    credit_amount=real_estate_credit
)

INCOMES = [
    salary_income
]

EXPENSES = [
    #rental_expense,
    fixed_expense,
    leisure_expense,
]

SAVINGS = [
    account_savings,
    pension_savings,
    deposit_savings,
]

CREDITS = [
    real_estate
]

budget = Budget(
    incomes=INCOMES,
    expenses=EXPENSES,
    savings=SAVINGS,
    credits=CREDITS
)

#############################################
# SIMULATE LIFE
#############################################

for month in range(30*12):
    budget.update()
    date = budget.incomes[0].current_date

    # payouts
    money = 0
    for income in budget.incomes:
        money += income.payout()
        pass

    # expenses
    for expense in budget.expenses:
        if not expense.is_credit_controlled:
            money -= expense.spend()
        pass

    # savings
    for saving in budget.savings[1:]:
        if not saving.is_credit_controlled:
            money -= saving.deposit()
        pass

    # credits
    for credit in budget.credits:
        money -= credit.payoff()
        pass

    # check balance
    if money < 0:
        if -money >= budget.savings[0].current_savings:
            logger.error(f"{date}: You've run out of money!")
            break
        else:
            logger.warning(f"{date}: You're monthly balance is negative. Taking {-money} DKK out of your bank account.")

    # add remainder to bank account
    budget.savings[0].deposit(money)

    # get (positive) saving interests
    for saving in budget.savings:
        saving.get_interests()
        pass

    # add (negative) credit interests
    for credit in budget.credits:
        credit.add_interests()
        pass

budget.get_summary()

#############################################
# PLOT STATIC BUDGET
#############################################
date = today + relativedelta(months=30)

fig, axes = plt.subplots()
plot_aggregated_budget(
    budget=budget,
    from_date=date,
    to_date=date,
    ax=axes,
    agg="mean",
    title=f'Budget ({date})'
)

#############################################
# PLOT BUDGET ACROSS TIME
#############################################

from_date = budget.incomes[0].summary.index[1]
to_date = budget.incomes[0].summary.index[-1]

fig, axes = plt.subplots(1, 2, figsize = (10,3), width_ratios=[3, 1], sharey='all')
plot_budget_across_time(
    budget,
    ax=axes[0],
    from_date=from_date,
    to_date=to_date,
    cumulative=False
)
plot_aggregated_budget(
    budget=budget,
    from_date=from_date,
    to_date=to_date,
    ax=axes[1],
    agg='mean',
    flip=True,
    add_ylab=False,
    add_legend=False
)


#############################################
# PLOT CUMULATIVE BUDGET ACROSS TIME
#############################################

fig, axes = plt.subplots(1, 2, figsize = (10,3), width_ratios=[3, 1], sharey='all')
plot_budget_across_time(
    budget=budget,
    ax=axes[0],
    from_date=from_date,
    to_date=to_date,
    cumulative=True
)
plot_aggregated_budget(
    budget=budget,
    from_date=from_date,
    to_date=to_date,
    ax=axes[1],
    agg='sum',
    flip=True,
    add_ylab=False,
    add_legend=False
)