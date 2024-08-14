import pytz
import numpy as np
import logging
import plotly.graph_objects as go

from datetime import datetime, timezone
from plotly.express.colors import sample_colorscale

from weathergov.constants import Metrics
from weathergov.app.constants import DataLabels


logger = logging.getLogger(__name__)


def get_colorscale(df, colorscale, coloring_parameter):
    if coloring_parameter is Metrics.Temperature:
        logger.info(f"Coloring map by temperature")
        return get_colorscale_by_temperature(df, colorscale, coloring_parameter)
    else:
        logger.warning(f"Coloring with parameter {coloring_parameter} have not been implemented yet")
        return "blue", [], []


def get_colorscale_by_temperature(df, colorscale, coloring_parameter):
    df.loc[df[coloring_parameter] < -99911990, coloring_parameter] = np.nan
    ind_nan = df[coloring_parameter].isna()
    print(df.head())

    # Fill nan values with mean value, this is temporary step only to create an array of colors
    # using sample_colorscale() function. Later, all the nans will be replaced with the default
    # color
    temperature_mean = df[coloring_parameter].mean()
    df.loc[ind_nan, coloring_parameter] = temperature_mean

    colorbar_tick_step = 5
    x_min = (int(df[coloring_parameter].min()) // colorbar_tick_step) * colorbar_tick_step
    x_max = (1 + int(df[coloring_parameter].max()) // colorbar_tick_step) * colorbar_tick_step
    n_ticks = 1 + int(x_max - x_min) // colorbar_tick_step

    colorscale_tick_values = np.linspace(0, 1, n_ticks)
    colorscale_tick_labels = [f"{v:.2f}°" for v in (colorscale_tick_values * (x_max - x_min) + x_min).tolist()]

    # -8.33 49.93 : that is going to be good
    values = df[coloring_parameter].apply(lambda x: (x - x_min) / (x_max - x_min))
    colors = sample_colorscale(colorscale, values)

    # Replace all the nans with gray color
    df.loc[ind_nan, 'color'] = 'rgba(100, 100, 100, 0.5)'
    return colors, colorscale_tick_values, colorscale_tick_labels


def get_map(app,
            colorscale='jet',
            coloring_parameter=Metrics.Temperature,
            show_inactive_stations=True) -> go.Figure:
    #
    # coloring_parameter = Metrics.Temperature

    #
    # Get the data from Redis
    # We store a connection object inside the app
    df = app.rc.get_observation_stations_info()
    logger.info(f"Generating a figure with coloring by {coloring_parameter}")

    # Create a colormap
    colors, colorscale_tick_values, colorscale_tick_labels = get_colorscale(df, colorscale, coloring_parameter)

    #
    #
    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='markers',
            customdata=df[DataLabels.FigureCustomData],
            hovertemplate="<b>Station name:</b> %{customdata[0]}<br>" +
                          "<b>Station ID:</b> %{customdata[1]}<br><br>" +
                          "Latitude: %{lat:,.6f}°<br>" +
                          "Longitude: %{lon:.6f}°<br>" +
                          "Elevation: %{customdata[2]:,.1f}<br>" +
                          "Time zone: %{customdata[3]}<br>" +
                          "URL: %{customdata[4]}" +
                          "<extra></extra>",
            marker={
                "color": colors,
                "colorbar": dict(thickness=10,
                                 tickvals=colorscale_tick_values,
                                 ticktext=colorscale_tick_labels,
                                 outlinewidth=0,
                                 orientation='h',
                                 y=1,
                                 bgcolor='white'),
                "cmin": 0,
                "cmax": 1,
                "showscale": True,
                "colorscale": colorscale
            },
        )
    )

    fig.update_layout(
        autosize=True,
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_bounds={"west": -127, "east": -65, "south": 22, "north": 54},
        # clickmode='event+select'
    )

    return fig


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
