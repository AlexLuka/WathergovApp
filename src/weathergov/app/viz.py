import pytz
import numpy as np
import plotly.graph_objects as go

from datetime import datetime, timezone
from plotly.express.colors import sample_colorscale

from weathergov.app.constants import DataLabels


def get_map(app,
            colorscale='jet',
            coloring_parameter='temperature') -> go.Figure:
    #
    #
    # Get the data from Redis
    # We store a connection object inside the app
    df = app.rc.get_observation_stations_info()
    print(df.head())
    print(f"Generating a figure with coloring by {coloring_parameter}")

    # Create a colormap

    # Get all the indices of NaN values. If value is set to Nan, then we cannot
    # create a color, therefore we are going to make that object gray - default color
    # that indicate that we do not have data for that location
    df.loc[df[coloring_parameter] < 99911990, coloring_parameter] = np.nan
    ind_nan = df[coloring_parameter].isna()

    # Fill nan values with mean value, this is temporary step only to create an array of colors
    # using sample_colorscale() function. Later, all the nans will be replaced with the default
    # color
    temperature_mean = df[coloring_parameter].mean()
    df.loc[ind_nan, coloring_parameter] = temperature_mean

    colorbar_tick_step = 5
    x_min = (int(df[coloring_parameter].min()) // colorbar_tick_step) * colorbar_tick_step
    x_max = (1 + int(df[coloring_parameter].max()) // colorbar_tick_step) * colorbar_tick_step
    n_ticks = 1 + int(x_max - x_min) // colorbar_tick_step

    x_bar = np.linspace(0, 1, n_ticks)
    t_bar = [f"{v:.2f}°" for v in (x_bar * (x_max - x_min) + x_min).tolist()]

    # -8.33 49.93 : that is going to be good
    df[coloring_parameter] = df[coloring_parameter].apply(lambda x: (x - x_min) / (x_max - x_min))
    df['color'] = sample_colorscale(colorscale, df[coloring_parameter])

    # Replace all the nans with gray color
    df.loc[ind_nan, 'color'] = 'rgba(100, 100, 100, 0.5)'

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
                "color": df['color'],
                "colorbar": dict(thickness=10,
                                 tickvals=x_bar,
                                 ticktext=t_bar,
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
