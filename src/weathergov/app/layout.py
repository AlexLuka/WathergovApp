import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import html, dcc

from weathergov.app.viz import get_map
from weathergov.app.components import Components


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def get_navbar():

    logo = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    dropdown = dbc.DropdownMenu(
        label="Menu",
        children=[
            dbc.DropdownMenuItem("Temperature", id="dd-button-1", n_clicks=0),
            dbc.DropdownMenuItem("Pressure", id="dd-button-2", n_clicks=0),
            dbc.DropdownMenuItem("Wind speed", id="dd-button-3", n_clicks=0),
            dbc.DropdownMenuItem("Humidity", id="dd-button-4", n_clicks=0),
        ],
        id="dd-menu",
        align_end=True,
        color="primary"
    )

    search_bar = dbc.Row(
        [
            dbc.Col(
                dropdown,
                width="auto"
            ),
            # dbc.Col(dbc.Input(type="search", placeholder="Search")),
            # dbc.Col(
            #     dbc.Button(
            #         "Search", color="primary", className="ms-2", n_clicks=0
            #     ),
            #     width="auto",
            # ),
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
