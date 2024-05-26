import typing as T
import pandas as pd
import datetime as dt
from cashflow.engines.components import Income, Expense, Saving

class Budget:
    def __init__(
        self,
        incomes: T.List[Income],
        expenses: T.List[Expense],
        savings: T.List[Saving],
    ):
        self.incomes = incomes
        self.expenses = expenses
        self.savings = savings
        self.n_incomes = len(incomes)
        self.n_expenses = len(expenses)
        self.n_savings = len(savings)
        self.current_date = dt.date.today().replace(day=1)  # internal date reference, to be updated continuously
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
        summary = pd.DataFrame()
        for x in self.incomes + self.expenses + self.savings:
            summary = pd.concat(([summary, x.get_summary()]))
        self.summary = summary
        return summary
