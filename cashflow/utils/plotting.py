import datetime as dt
import typing as T
import matplotlib
import pandas as pd
from matplotlib import pyplot as plt

from cashflow.engines.budget import Budget
from cashflow.engines.components import Income, Saving, Expense
from cashflow.utils.logging_utils import init_logger
import matplotlib.pyplot as plt

logger = init_logger()


def plot_budget_across_time(
    budget: Budget,
    from_date: dt.date | None = None,
    to_date: dt.date | None = None,
    cumulative: bool = False,
):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3), width_ratios=[3, 1], sharey="all")

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
    _plot_stacked_curves(components=budget.incomes, date_range=date_range, cumulative=cumulative, ax=axes[0], sign=1)
    # add expenses & savings on negative half
    _plot_stacked_curves(components=budget.expenses + budget.savings, date_range=date_range, cumulative=cumulative,
                         ax=axes[0], sign=-1)
    axes[0].axhline(y=0, ls="--", c="black", lw=1)
    axes[0].legend()
    title = "budget across time" + (" (cumulative)" if cumulative else "")
    axes[0].set_title(title)

    plot_aggregated_budget(
        budget=budget,
        from_date=from_date,
        to_date=to_date,
        ax=axes[1],
        agg="sum" if cumulative else "mean",
        flip=True,
        add_ylab=False,
        add_legend=False,
    )

    fig.tight_layout()

    return fig


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


def _plot_unstacked_bars(
    components: T.List,
    from_date: dt.date,
    to_date: dt.date,
    ax: matplotlib.axes._axes.Axes,
    agg: str,
):
    for x, c in enumerate(components):
        c_amounts = (
            c.summary[(c.summary.index >= from_date) & (c.summary.index <= to_date)][
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
            x=x,
            height=c_value,
            width=0.75,
            label=c.name,
            color=c.color,
        )
        pass
    positions = [i for i in range(len(components))]
    labels = [c.name for c in components]
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    return None


def plot_bars(
    stacked: bool = True,
    **kwargs
):
    return _plot_stacked_bars(**kwargs) if stacked else _plot_unstacked_bars(**kwargs)


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
    components: T.List,
    date_range: T.List,
    cumulative: bool,
    ax: matplotlib.axes._axes.Axes,
    sign: int = 1,
):
    sum_of_values = pd.Series(0, index=date_range)
    for c in components:
        c_amounts = c.summary.loc[date_range]["amount"]
        c_values = sign * (c_amounts if not cumulative else c_amounts.cumsum())
        sum_of_values_new = sum_of_values + c_values
        ax.plot(sum_of_values_new, label=c.name, color=c.color)
        ax.fill_between(
            x=sum_of_values.index, y1=sum_of_values, y2=sum_of_values_new, color=c.color
        )
        sum_of_values = sum_of_values_new
        pass
    pass


def _plot_unstacked_curves(
    components: T.List,
    date_range: T.List,
    cumulative: bool,
    ax: matplotlib.axes._axes.Axes,
    sign: int = 1,
):
    for c in components:
        c_amounts = c.summary.loc[date_range]["amount"]
        c_values = sign * (c_amounts if not cumulative else c_amounts.cumsum())
        ax.plot(c_values, label=c.name, color=c.color)
        pass
    pass


def plot_curves(
    stacked: bool = True,
    **kwargs
):
    return _plot_stacked_curves(**kwargs) if stacked else _plot_unstacked_curves(**kwargs)


def plot_components_across_time(
    components: T.List[Income | Saving | Expense],
    from_date: dt.date | None = None,
    to_date: dt.date | None = None,
    cumulative: bool = True,
    stacked: bool = True,
    agg: str = "sum"
):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3), width_ratios=[3, 1])

    # Fill with default values
    if from_date is None:
        from_date = components[0].summary.index[1]
    if to_date is None:
        to_date = components[0].summary.index[-1]
    # define date range
    date_range = (
        components[0]
        .summary.index[
            (components[0].summary.index >= from_date)
            & (components[0].summary.index <= to_date)
            ]
        .drop_duplicates()
    )

    plot_curves(
        components=components,
        date_range=date_range,
        cumulative=cumulative,
        ax=axes[0],
        sign=1,
        stacked=stacked
    )

    plot_bars(
        components=components,
        from_date=from_date,
        to_date=to_date,
        ax=axes[1],
        agg=agg,
        stacked=stacked
    )

    type = components[0].type
    title = f"Monthly {type.lower()}s across time" + (" (cumulative)" if cumulative else "")
    axes[0].set_title(title)
    axes[0].legend()

    axes[1].set_title(f"Aggregated {type}s ({agg})")
    fig.tight_layout()

    return fig
