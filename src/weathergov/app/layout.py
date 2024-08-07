import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import html, dcc
from plotly.express.colors import sample_colorscale

from weathergov.app.components import Components
from weathergov.app.constants import DataLabels


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_map(app, colorscale='jet') -> go.Figure:
    #
    #
    # Get the data
    df = app.rc.get_observation_stations_info()
    app.df = df

    # print(df.head())

    # Create a colormap
    ind_nan = df['temperature'].isna()

    # Fill nan values with mean
    temperature_mean = df['temperature'].mean()
    df.loc[ind_nan, 'temperature'] = temperature_mean

    colorbar_tick_step = 5
    x_min = (int(df['temperature'].min()) // colorbar_tick_step) * colorbar_tick_step
    x_max = (1 + int(df['temperature'].max()) // colorbar_tick_step) * colorbar_tick_step
    n_ticks = 1 + int(x_max - x_min) // colorbar_tick_step

    x_bar = np.linspace(0, 1, n_ticks)
    t_bar = [f"{v:.2f}°" for v in (x_bar * (x_max - x_min) + x_min).tolist()]

    # -8.33 49.93 : that is going to be good
    df['temperature'] = df['temperature'].apply(lambda x: (x - x_min) / (x_max - x_min))
    df['color'] = sample_colorscale(colorscale, df['temperature'])

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
                "colorbar": dict(thickness=5,
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


def get_navbar():

    logo = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    search_bar = dbc.Row(
        [
            dbc.Col(dbc.Input(type="search", placeholder="Search")),
            dbc.Col(
                dbc.Button(
                    "Search", color="primary", className="ms-2", n_clicks=0
                ),
                width="auto",
            ),
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=logo, height="30px")),
                            dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://plotly.com",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    search_bar,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            fluid=True
        ),
        color="dark",
        dark=True,
    )
    return navbar


def get_collapse_item(item_label, item_label_id, collapse_id, graph_id):
    temp_fig = go.Figure()
    temp_fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return [
        dbc.Button(
            item_label,
            id=item_label_id,
            class_name="d-grid col-12",
            color="light"
        ),
        dbc.Collapse(
            dcc.Graph(
                figure=temp_fig,
                style={"height": "100%"},
                id=graph_id
            ),
            id=collapse_id,
            is_open=False,
        )
    ]


def get_collapse():
    # temp_fig = go.Figure()
    # temp_fig.update_layout(
    #     autosize=True,
    #     height=300,
    #     margin={"r": 0, "t": 0, "l": 0, "b": 0},
    # )

    collapse = []
    labels = [
        "Temperature",
        "Pressure",
        "Wind Speed",
        "Wind Direction",
        "Humidity"
    ]

    for i in range(5):
        collapse.extend(
            get_collapse_item(
                labels[i],
                Components.get_collapse_label_id(labels[i]),
                Components.get_collapse_id(labels[i]),
                Components.get_collapse_graph_id(labels[i])
            )
        )

    return html.Div(collapse)


def get_rt_graph_pane():

    temp_fig = go.Figure()
    temp_fig.update_layout(
        autosize=True,
        height=300,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return dbc.Container(
        dbc.Stack(
            [
                get_collapse(),
                # dbc.Row(
                #     dcc.Graph(
                #         figure=temp_fig,
                #         style={"height": "100%"}
                #     )
                # )
            ]
        )
    )


def get_weather_station_info_panel():
    left_side_width = 4
    right_side_width = 8

    return dbc.Container(
        dbc.Stack(
            [
                dbc.Row(
                    dbc.Label("Station Information", size='lg')
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Name:", style={"justify-content": "right"}), width=left_side_width),
                        dbc.Col(width=right_side_width, id=Components.WeatherStationInfoPanelName)
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("ID:"), width=left_side_width),
                        dbc.Col(width=right_side_width, id=Components.WeatherStationInfoPanelStationID)
                    ]
                ),
                # TODO Add other attrbutes here
                dbc.Row(
                    [
                        dbc.Col(html.Label("Elevation (m):"), width=left_side_width),
                        dbc.Col(width=right_side_width, id=Components.WeatherStationInfoPanelElevationAboveGround)
                    ]
                ),
                html.Hr(),
                dbc.Row(get_rt_graph_pane()),
                dbc.Row(),
            ],
            gap=1
        ),
        fluid=True
    )


def get_layout(app):
    return dbc.Container(
        [
            get_navbar(),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            figure=get_map(app),
                            style={"height": "100%"},
                            id=Components.GraphMap
                        ),
                        width=9,
                        # style={"background-color": "blue"},
                    ),
                    dbc.Col(
                        get_weather_station_info_panel(),
                        width=3,
                        # style={"background-color": "cyan"},
                    ),
                ],
                class_name="h-100",
            )
        ],
        style={"height": "90vh"},
        class_name="mt-12",
        fluid=True
    )
