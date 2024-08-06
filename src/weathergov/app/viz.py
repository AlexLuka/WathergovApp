import pytz
import plotly.graph_objects as go

from datetime import datetime, timezone


def get_default_figure():
    fig = go.Figure()

    fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig


def get_temperature_ts_figure(x: list, y: list, tz=None):
    """
        Convert temperature
    :param x:
    :param y:
    :param tz:
    :return:
    """
    if tz is None:
        ts = [datetime.fromtimestamp(xi / 1000, tz=timezone.utc) for xi in x]
    else:
        ts = [datetime.fromtimestamp(xi / 1000, tz=pytz.timezone(tz)) for xi in x]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ts,
            y=y,
            mode='lines+markers'
        )
    )

    fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig


def get_ts_figure(x: list, y: list):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines+markers'
        )
    )

    fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig


def get_ts_figure_polar(r: list, direction: list):
    fig = go.Figure()

    try:
        r0 = r[0]
        r = [ri - r0 for ri in r]
    except IndexError:
        pass

    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=direction,
            mode='markers',
        )
    )

    fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig
