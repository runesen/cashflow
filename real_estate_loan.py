from cashflow.engines.components import Saving, Expense, Income

real_estate_price = 2500000
initial_payment = 300000
loan_duration = 30
annual_interests = 0.06

monthly_payment = (
    (1 + annual_interests) ** (loan_duration - 1) /
    ((1 + annual_interests) ** loan_duration - 1) *
    (real_estate_price - initial_payment) *
    annual_interests
) / 12

income = Income(
    name = "income",

)

interest_expense = Expense(
    name = "real_estate_interests",
)

real_estate = Saving(
    name = "real_estate",
    initial_amount=initial_payment,
    monthly_interest_rate=0
)


for month in range(100):
    interest_expense.update()
    real_estate.update()

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