import pandas as pd
from cashflow.utils.logging_utils import init_logger

logger = init_logger()

EXPENSE_COLORS = ("#EB2F2F", "#FFA588", "#FEB0C2", "#FFBE00")
INCOME_COLORS = ("#7FB26B", "#206A14", "#9B8E17")
SAVING_COLORS = ("#3C7AFD", "#8246D0", "#78EFFF", "#001B9C", "#590581", "#00FFD8")

class Colors:

    def __init__(
        self,
        expense_colors = EXPENSE_COLORS,
        income_colors = INCOME_COLORS,
        saving_colors = SAVING_COLORS,
    ):
        df_color = pd.concat([
            pd.DataFrame({'color': expense_colors, 'type': 'expense'}),
            pd.DataFrame({'color': income_colors, 'type': 'income'}),
            pd.DataFrame({'color': saving_colors, 'type': 'saving'})
        ])
        df_color['used'] = False
        self.df_color = df_color.set_index('color')
        pass

    def get_color(self, type: str):
        available_colors = self.df_color.query(f'(type == "{type}") and (not used)').index
        if len(available_colors) == 0:
            logger.error(f"No more colors of type {type}!")
        chosen_color = available_colors[0]
        self.df_color.loc[
            chosen_color,
            "used"
        ] = True
        return chosen_color


colors = Colors()