import datetime as dt
import typing as T
import matplotlib
import pandas as pd
from cashflow.engines.budget_class import Budget
from cashflow.utils.logging_utils import init_logger

logger = init_logger()


def plot_budget_across_time(
    budget: Budget,
    ax: matplotlib.axes._axes.Axes,
    from_date: dt.date | None = None,
    to_date: dt.date | None = None,
    cumulative: bool = False,
):
    # Fill with default values
    if from_date is None:
        from_date = budget.incomes[0].summary.index[1]
    if to_date is None:
        to_date = budget.incomes[0].summary.index[-1]
    # define date range
    date_range = (
        budget.incomes[0]
        .summary.index[
            (budget.incomes[0].summary.index >= from_date)
            & (budget.incomes[0].summary.index <= to_date)
        ]
        .drop_duplicates()
    )
    # add incomes on positive half
    _plot_stacked_curves(
        objects=budget.incomes,
        date_range=date_range,
        cumulative=cumulative,
        ax=ax,
        sign=1,
    )
    # add expenses & savings on negative half
    _plot_stacked_curves(
        objects=budget.expenses + budget.savings,
        date_range=date_range,
        cumulative=cumulative,
        ax=ax,
        sign=-1,
    )
    ax.axhline(y=0, ls="--", c="black", lw=1)
    ax.legend()
    title = "budget across time" + (" (cumulative)" if cumulative else "")
    ax.set_title(title)
    pass


def _plot_stacked_bars(
    components: T.List,
    from_date: dt.date,
    to_date: dt.date,
    ax: matplotlib.axes._axes.Axes,
    agg: str,
    bottom: float = 0,
    sign: int = 1,
):
    components_sum = bottom
    for c in components:
        c_amounts = (
            sign
            * c.summary[(c.summary.index >= from_date) & (c.summary.index <= to_date)][
                "amount"
            ]
        )
        c_value = (
            c_amounts.sum()
            if agg == "sum"
            else c_amounts.mean()
            if agg == "mean"
            else logger.error("Unknown aggregation")
        )
        ax.bar(
            x=c.plot_position,
            height=c_value,
            width=0.75,
            label=c.name,
            bottom=components_sum,
            color=c.color,
        )
        components_sum += c_value
        pass
    return components_sum


# TODO: adjust plotting to allow for negative values of account_savings counting towards incomes.
def plot_aggregated_budget(
    budget: Budget,
    from_date: dt.date,
    to_date: dt.date,
    ax: matplotlib.axes._axes.Axes,
    agg: str,
    title: str | None = None,
    flip: bool = False,
    add_ylab: bool = True,
    add_legend: bool = True,
):
    _plot_stacked_bars(
        components=budget.incomes,
        from_date=from_date,
        to_date=to_date,
        ax=ax,
        agg=agg,
        bottom=0,
    )
    bottom_components = budget.savings if not flip else budget.expenses
    top_components = budget.expenses if not flip else budget.savings
    bottom_sum = _plot_stacked_bars(
        components=bottom_components,
        from_date=from_date,
        to_date=to_date,
        ax=ax,
        agg=agg,
        bottom=0,
        sign=-1 if flip else 1,
    )
    _plot_stacked_bars(
        components=top_components,
        from_date=from_date,
        to_date=to_date,
        ax=ax,
        agg=agg,
        bottom=bottom_sum,
        sign=-1 if flip else 1,
    )
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["Incomes", "Expenses", "Savings"])
    if title is None:
        title = f"aggregated budget ({agg})"
    ax.set_title(title)
    if flip:
        ax.axhline(y=0, ls="--", c="black", lw=1)
    if add_ylab:
        ax.set_ylabel("Amount (DKK)")
    if add_legend:
        ax.legend()
    pass


def _plot_stacked_curves(
    objects: T.List,
    date_range: T.List,
    cumulative: bool,
    ax: matplotlib.axes._axes.Axes,
    sign: int = 1,
):
    sum_of_values = pd.Series(0, index=date_range)
    for o in objects:
        o_amounts = o.summary.loc[date_range]["amount"]
        o_values = o_amounts if not cumulative else o_amounts.cumsum()
        sum_of_values_new = sum_of_values + sign * o_values
        ax.plot(sum_of_values_new, label=o.name, color=o.color)
        ax.fill_between(
            x=sum_of_values.index, y1=sum_of_values, y2=sum_of_values_new, color=o.color
        )
        sum_of_values = sum_of_values_new
        pass
    pass
