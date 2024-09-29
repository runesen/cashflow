import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from cashflow.engines.components import Income, Credit, Saving, Expense
from cashflow.engines.budget import Budget
import datetime as dt
from dateutil.relativedelta import relativedelta
from cashflow.utils.plotting import (
    plot_budget_across_time,
    plot_aggregated_budget,
    plot_components_across_time,
)
from cashflow.utils.logging_utils import init_logger

logger = init_logger()

# we only consider time pr month
today = dt.date.today().replace(day=1)

st.set_page_config(page_icon="📈", page_title="Cashflows")

st.markdown(
    """
    # **Cashflow**
    A simple tool for simulating and visualizing your private economy. Test. Test. Test.
"""
)

st.sidebar.markdown("# Please supply information ")

st.sidebar.markdown(
    """
    ## Basic information
    """
)

age = st.sidebar.text_input(label="Current age", value="33", key=f"age")
retirement_age = st.sidebar.text_input(
    label="Expected retirement age", value="67", key=f"retirement_age"
)
expected_lifespan = st.sidebar.text_input(
    label="Expected lifespan", value="90", key=f"expected_lifespan"
)
year_of_retirement = dt.date.today().year + int(retirement_age) - int(age)
year_of_death = dt.date.today().year + int(expected_lifespan) - int(age)

st.sidebar.markdown(
    """
    ## Incomes
    """
)

if "num_incomes" not in st.session_state:
    st.session_state["num_incomes"] = 0

if st.sidebar.button("Add income"):
    st.session_state["num_incomes"] += 1

INCOMES = []

for i in range(1, st.session_state["num_incomes"] + 1):
    name = st.sidebar.text_input(
        label="Income name", value="Salary", key=f"income_name_{i}"
    )
    monthly_amount = st.sidebar.number_input(
        label="monthly amount (DKK)", value=30000, key=f"income_monthly_amount_{i}"
    )
    if f"num_raises_{i}" not in st.session_state:
        st.session_state[f"num_raises_{i}"] = 0

    if st.sidebar.button("Add raise", key=f"raise_button_{i}"):
        st.session_state[f"num_raises_{i}"] += 1

    raise_years = []
    raise_amounts = []
    for j in range(1, st.session_state[f"num_raises_{i}"] + 1):
        raise_years.append(
            st.sidebar.number_input(label="Year", value=2025, key=f"raise_year_{j}")
        )
        raise_amounts.append(
            st.sidebar.number_input(label="Amount", value=1000, key=f"raise_amount_{j}")
        )
    raise_dates = [dt.date(year, 1, 1) for year in raise_years]

    income = Income(
        name=name,
        monthly_amount=monthly_amount,
        change_at_dates=raise_dates,
        change_by_amounts=raise_amounts,
        last_income_date=dt.date(year_of_retirement, 1, 1),
    )

    INCOMES.append(income)


st.sidebar.markdown(
    """
    ## Expenses
    """
)

if "num_expenses" not in st.session_state:
    st.session_state["num_expenses"] = 0

if st.sidebar.button("Add expense"):
    st.session_state["num_expenses"] += 1

EXPENSES = []

for num in range(1, st.session_state["num_expenses"] + 1):
    name = st.sidebar.text_input(
        label="Expense name", value="Expense", key=f"expense_name_{num}"
    )
    monthly_amount = st.sidebar.number_input(
        label="monthly amount (DKK)", value=10000, key=f"expense_monthly_amount_{num}"
    )
    expense = Expense(name=name, monthly_amount=monthly_amount)
    EXPENSES.append(expense)


st.sidebar.markdown(
    """
    ## Savings
    """
)

if "num_savings" not in st.session_state:
    st.session_state["num_savings"] = 0

if st.sidebar.button("Add saving"):
    st.session_state["num_savings"] += 1

SAVINGS = []

for num in range(1, st.session_state["num_savings"] + 1):
    name = st.sidebar.text_input(
        label="Saving name", value="Saving", key=f"saving_name_{num}"
    )
    monthly_amount = st.sidebar.number_input(
        label="monthly amount (DKK)", value=5000, key=f"saving_monthly_amount_{num}"
    )
    initial_amount = st.sidebar.number_input(
        label="current amount (DKK)", value=10000, key=f"saving_initial_amount_{num}"
    )
    interest_rate = st.sidebar.number_input(
        label="annual interest rate", value=0.02, key=f"saving_interest_rate_{num}"
    )
    saving = Saving(
        name=name,
        monthly_amount=monthly_amount,
        initial_amount=initial_amount,
        interest_rate=interest_rate,
        interest_frequency="annually",
    )
    SAVINGS.append(saving)

st.sidebar.markdown(
    """
    ## Credits
    """
)

if "num_credits" not in st.session_state:
    st.session_state["num_credits"] = 0

if st.sidebar.button("Add credit"):
    st.session_state["num_credits"] += 1

CREDITS = []

for num in range(1, st.session_state["num_credits"] + 1):
    name = st.sidebar.text_input(
        label="Credit name", value="Credit", key=f"credit_name_{num}"
    )
    total_amount = st.sidebar.number_input(
        label="total amount (DKK)", value=3000000, key=f"credit_total_amount_{num}"
    )
    initial_payoff = st.sidebar.number_input(
        label="initial payoff (DKK)", value=500000, key=f"credit_initial_payoff_{num}"
    )
    loan_duration = st.sidebar.number_input(
        label="loan duration (years)", value=30, key=f"credit_loan_duration_{num}"
    )
    annual_interest_rate = st.sidebar.number_input(
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

budget = Budget(incomes=INCOMES, expenses=EXPENSES, savings=SAVINGS, credits=CREDITS)

##################
# RUN SIMULATION #
##################

budget.run()
budget.get_summary()

#############
# VISUALIZE #
#############

if st.button("Simulate Income"):
    #######################################
    # PLOT CUMULATIVE INCOMES ACROSS TIME #
    #######################################

    fig = plot_components_across_time(
        components=budget.incomes,
        from_date=dt.date.today(),
        to_date=dt.date(year_of_death, 1, 1),
        stacked=False,
        cumulative=False,
        agg="mean",
    )
    st.pyplot(fig)


if st.button("Simulate Saving"):
    #######################################
    # PLOT SAVINGS ACROSS TIME #
    #######################################

    fig = plot_components_across_time(
        components=budget.savings,
        from_date=dt.date.today(),
        to_date=dt.date(year_of_death, 1, 1),
        stacked=True,
        cumulative=True,
        agg="sum",
    )
    st.pyplot(fig)


if False:
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

    #############################################
    # PLOT BUDGET ACROSS TIME
    #############################################

    from_date = budget.incomes[0].summary.index[1]
    to_date = budget.incomes[0].summary.index[-1]

    fig = plot_budget_across_time(
        budget=budget, from_date=from_date, to_date=to_date, cumulative=False
    )
    st.pyplot(fig)

    #############################################
    # PLOT CUMULATIVE BUDGET ACROSS TIME
    #############################################

    fig = plot_budget_across_time(
        budget=budget, from_date=from_date, to_date=to_date, cumulative=True
    )
    st.pyplot(fig)

    #############################################
    # PLOT SAVINGS BUDGET ACROSS TIME
    #############################################
