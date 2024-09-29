import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from cashflow.engines.components import Income, Credit, Saving, Expense
from cashflow.engines.budget import Budget
import datetime as dt
from dateutil.relativedelta import relativedelta
from cashflow.utils.plotting import plot_budget_across_time, plot_aggregated_budget
from cashflow.utils.logging_utils import init_logger

logger = init_logger()

# we only consider time pr month
today = dt.date.today().replace(day=1)

st.set_page_config(page_icon="📈", page_title="Lifelong Budget")

st.markdown(
    """
    # **Cashflow**
    A simple tool for simulating and visualizing your private economy. Test. Test. Test.
"""
)

st.markdown(
    """
    ## Incomes
    """
)

if "num_incomes" not in st.session_state:
    st.session_state["num_incomes"] = 0

if st.button("Add income"):
    st.session_state["num_incomes"] += 1

INCOMES = []

for num in range(1, st.session_state["num_incomes"] + 1):
    name = st.text_input(label="Income name", value="Salary", key=f"income_name_{num}")
    monthly_amount = st.number_input(
        label="monthly amount (DKK)", value=30000, key=f"income_monthly_amount_{num}"
    )
    income = Income(name=name, monthly_amount=monthly_amount)
    INCOMES.append(income)

st.markdown(
    """
    ## Expenses
    """
)

if "num_expenses" not in st.session_state:
    st.session_state["num_expenses"] = 0

if st.button("Add expense"):
    st.session_state["num_expenses"] += 1

EXPENSES = []

for num in range(1, st.session_state["num_expenses"] + 1):
    name = st.text_input(
        label="Expense name", value="Expense", key=f"expense_name_{num}"
    )
    monthly_amount = st.number_input(
        label="monthly amount (DKK)", value=10000, key=f"expense_monthly_amount_{num}"
    )
    expense = Expense(name=name, monthly_amount=monthly_amount)
    EXPENSES.append(expense)

st.markdown(
    """
    ## Credits
    """
)

if "num_credits" not in st.session_state:
    st.session_state["num_credits"] = 0

if st.button("Add credit"):
    st.session_state["num_credits"] += 1

CREDITS = []

for num in range(1, st.session_state["num_credits"] + 1):
    name = st.text_input(label="Credit name", value="Credit", key=f"credit_name_{num}")
    total_amount = st.number_input(
        label="total amount (DKK)", value=3000000, key=f"credit_total_amount_{num}"
    )
    initial_payoff = st.number_input(
        label="initial payoff (DKK)", value=500000, key=f"credit_initial_payoff_{num}"
    )
    loan_duration = st.number_input(
        label="loan duration (years)", value=30, key=f"credit_loan_duration_{num}"
    )
    annual_interest_rate = st.number_input(
        label="annual interest rate",
        value=0.05,
        key=f"credit_annual_interest_rate_{num}",
    )
    credit = Credit(
        name=name,
        credit_amount=total_amount,
        initial_payoff=initial_payoff,
        loan_duration=loan_duration,
        annual_interest_rate=annual_interest_rate,
    )
    CREDITS.append(credit)

st.markdown(
    """
    ## Savings
    """
)

if "num_savings" not in st.session_state:
    st.session_state["num_savings"] = 0

if st.button("Add saving"):
    st.session_state["num_savings"] += 1

SAVINGS = []

for num in range(1, st.session_state["num_savings"] + 1):
    name = st.text_input(label="Saving name", value="Saving", key=f"saving_name_{num}")
    monthly_amount = st.number_input(
        label="monthly amount (DKK)", value=5000, key=f"saving_monthly_amount_{num}"
    )
    initial_amount = st.number_input(
        label="current amount (DKK)", value=10000, key=f"saving_initial_amount_{num}"
    )
    interest_rate = st.number_input(
        label="interest rate", value=0.02, key=f"saving_interest_rate_{num}"
    )
    interest_frequency = st.selectbox(
        label="frequency",
        options=["monthly", "annually"],
        key=f"saving_interest_frequency_{num}",
    )
    saving = Saving(
        name=name,
        monthly_amount=monthly_amount,
        initial_amount=initial_amount,
        interest_rate=interest_rate,
        interest_frequency=interest_frequency,
    )
    SAVINGS.append(saving)

budget = Budget(incomes=INCOMES, expenses=EXPENSES, savings=SAVINGS, credits=CREDITS)

#############################################
# SIMULATE LIFE
#############################################

for month in range(30 * 12):
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
            logger.warning(
                f"{date}: You're monthly balance is negative. Taking {-money} DKK out of your bank account."
            )

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
    title=f"Budget ({date})",
)
st.pyplot(fig)
