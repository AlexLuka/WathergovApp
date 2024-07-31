import dash_bootstrap_components as dbc

from dash import html


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


def get_layout():
    return dbc.Container(
        [
            get_navbar(),
            # dbc.Row(
            #     [
            #         dbc.Col(
            #             html.P("This is column 1"),
            #             width=12,
            #             style={"height": "100px", "background-color": "red"},
            #         ),
            #         # dbc.Col(
            #         #     html.P("This is column 2"),
            #         #     width=4,
            #         #     style={"height": "100%", "background-color": "green"},
            #         # ),
            #     ],
            #     # class_name="h-25",
            # ),
            dbc.Row(
                [
                    dbc.Col(
                        html.P("This is column 3"),
                        width=9,
                        style={"height": "100%", "background-color": "blue"},
                    ),
                    dbc.Col(
                        html.P("This is column 4"),
                        width=3,
                        style={"height": "100%", "background-color": "cyan"},
                    ),
                ],
                class_name="h-100",
            )
        ],
        # style={"height": "100vh"},
        fluid=True
    )
