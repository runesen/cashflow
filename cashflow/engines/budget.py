import typing as T
import pandas as pd
import datetime as dt
from cashflow.engines.components import Income, Expense, Saving, Credit
from cashflow.utils.logging_utils import init_logger

logger = init_logger()


class Budget:
    def __init__(
        self,
        incomes: T.List[Income],
        expenses: T.List[Expense],
        savings: T.List[Saving],
        credits: T.List[Credit],
    ):
        self.incomes = incomes
        self.expenses = expenses + [c.interests for c in credits]
        self.savings = savings + [c.ownership for c in credits]
        self.credits = credits
        pass

    def run(self):
        for month in range(60 * 12):
            self.update()
            date = self.incomes[0].current_date

            # payouts
            money = 0
            for income in self.incomes:
                money += income.payout()
                pass

            # expenses
            for expense in self.expenses:
                if not expense.is_credit_controlled:
                    money -= expense.spend()
                pass

            # savings
            for saving in self.savings[1:]:
                if not saving.is_credit_controlled:
                    money -= saving.deposit()
                pass

            # credits
            for credit in self.credits:
                money -= credit.payoff()
                pass

            # check balance
            if money < 0:
                if -money >= self.savings[0].current_savings:
                    logger.error(f"{date}: You've run out of money!")
                    break
                else:
                    logger.warning(
                        f"{date}: You're monthly balance is negative. Taking {-money} DKK out of your bank account."
                    )

            # add remainder to bank account
            self.savings[0].deposit(money)

            # get (positive) saving interests
            for saving in self.savings:
                saving.get_interests()
                pass

            # add (negative) credit interests
            for credit in self.credits:
                credit.add_interests()
                pass

    def get_summary(self):
        for x in self.incomes + self.expenses + self.savings:
            x.get_summary()

    def update(self):
        for x in self.incomes + self.expenses + self.savings + self.credits:
            x.update()
            pass
        pass
