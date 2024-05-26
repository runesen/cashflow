import typing as T
import pandas as pd
import datetime as dt
from cashflow.engines.components import Income, Expense, Saving, Credit


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

    def get_summary(self):
        for x in self.incomes + self.expenses + self.savings:
            x.get_summary()

    def update(self):
        for x in self.incomes + self.expenses + self.savings + self.credits:
            x.update()
            pass
        pass
