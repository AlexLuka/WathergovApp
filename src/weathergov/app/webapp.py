# import json
import logging
import dash_bootstrap_components as dbc

from time import time
from dash import Dash, Input, Output, State, callback
from dotenv import load_dotenv
# from dash_bootstrap_components.themes import LUMEN

from weathergov.app.layout import get_layout
from weathergov.app.components import Components
from weathergov.utils.redis_utils import RedisClient
from weathergov.app.viz import (get_ts_figure,
                                get_ts_figure_polar,
                                get_default_figure,
                                get_temperature_ts_figure,
                                get_map)
from weathergov.utils.logging_utils import init_logger


logger = logging.getLogger(__name__)


app = Dash(
    __name__,
    title="Simple Weather App",
    external_stylesheets=[
        dbc.themes.LUMEN,
        # dbc.themes.BOOTSTRAP
    ],
    add_log_handler=logger
)
app.rc = None


@callback(
    # Output('click-data', 'children'),
    Output(Components.WeatherStationInfoPanelName, 'children'),
    Output(Components.WeatherStationInfoPanelStationID, "children"),
    Output(Components.WeatherStationInfoPanelElevationAboveGround, "children"),
    #
    # Figures output
    Output(Components.get_collapse_graph_id("temperature"), "figure"),
    Output(Components.get_collapse_graph_id("pressure"), "figure"),
    Output(Components.get_collapse_graph_id("wind speed"), "figure"),
    Output(Components.get_collapse_graph_id("wind direction"), "figure"),
    Output(Components.get_collapse_graph_id("Humidity"), "figure"),
    Input(Components.GraphMap, 'clickData'))
def display_click_data(click_data):
    """
        When we click the data we 100% sure that the data is present on the map,
        and before adding it to the map, we save it to the app!
    :param click_data:
    :return:
    """
    if click_data is None:
        # If the click_data is None, therefore no data is present.
        # This is due to the event was fired on load
        fig = get_default_figure()
        return "", "", "", fig, fig, fig, fig, fig

    point = click_data['points'][0]

    elevation_units = point['customdata'][5]
    elevation_units = elevation_units.split(":")[-1]

    # Example of a 'point' data
    # {
    #   "curveNumber": 0,
    #   "pointNumber": 17097,
    #   "pointIndex": 17097,
    #   "lon": "-87.05",
    #   "lat": "44.055",
    #   "bbox": {
    #       "x0": 861.5483870967741,
    #       "x1": 863.5483870967741,
    #       "y0": 367.852296661568,
    #       "y1": 369.852296661568
    #   },
    #   "customdata": [
    #       "RAWLEY POINT EAST, WI (269)",
    #       "NDBC45210",
    #       "0",
    #       "America/Chicago",
    #       "https://api.weather.gov/stations/NDBC45210",
    #       "wmoUnit:m"
    #   ]
    # }

    station_id = point['customdata'][1]
    time_zone = point['customdata'][3]
    ts_now = int(time() * 1000)

    # Get 1 week of temperature data for selected station by station iD
    data = app.rc.get_timeseries_data_multi(
        station_id=station_id,
        data_keywords=["temperature", "barometric_pressure", "wind_speed", "wind_direction", "relative_humidity"],
        ts_from=ts_now - 24 * 3600 * 1000 * 7,
        ts_to=ts_now
    )

    # return json.dumps(point, indent=2)
    return (point['customdata'][0],
            dbc.NavLink(
                station_id,
                href=point['customdata'][4],
                external_link='True',
                target='_blank',
                active=True
            ),
            f"{point['customdata'][2]} {elevation_units}",
            get_temperature_ts_figure(x=data['temperature'][0], y=data['temperature'][1], tz=time_zone),
            get_ts_figure(x=data['barometric_pressure'][0], y=data['barometric_pressure'][1]),
            get_ts_figure(x=data['wind_speed'][0], y=data['wind_speed'][1]),
            get_ts_figure_polar(r=data['wind_direction'][0], direction=data['wind_direction'][1]),
            get_ts_figure(x=data['relative_humidity'][0], y=data['relative_humidity'][1]),
            )


# Current order: [
#         "Temperature",
#         "Pressure",
#         "Wind Speed",
#         "Wind Direction",
#         "Humidity"
#     ]
# need to make it dynamic in the future
@callback(
    Output(Components.get_collapse_id("Temperature"), "is_open"),
    Output(Components.get_collapse_id("Pressure"), "is_open"),
    Output(Components.get_collapse_id("Wind Speed"), "is_open"),
    Output(Components.get_collapse_id("Wind Direction"), "is_open"),
    Output(Components.get_collapse_id("Humidity"), "is_open"),
    #
    Output(Components.get_collapse_label_id("Temperature"), "n_clicks"),
    Output(Components.get_collapse_label_id("Pressure"), "n_clicks"),
    Output(Components.get_collapse_label_id("Wind Speed"), "n_clicks"),
    Output(Components.get_collapse_label_id("Wind Direction"), "n_clicks"),
    Output(Components.get_collapse_label_id("Humidity"), "n_clicks"),
    #
    Input(Components.get_collapse_label_id("Temperature"), "n_clicks"),
    Input(Components.get_collapse_label_id("Pressure"), "n_clicks"),
    Input(Components.get_collapse_label_id("Wind Speed"), "n_clicks"),
    Input(Components.get_collapse_label_id("Wind Direction"), "n_clicks"),
    Input(Components.get_collapse_label_id("Humidity"), "n_clicks"),
    #
    State(Components.get_collapse_id("Temperature"), "is_open"),
    State(Components.get_collapse_id("Pressure"), "is_open"),
    State(Components.get_collapse_id("Wind Speed"), "is_open"),
    State(Components.get_collapse_id("Wind Direction"), "is_open"),
    State(Components.get_collapse_id("Humidity"), "is_open"),
)
def toggle_collapse(n1, n2, n3, n4, n5, is_open_1, is_open_2, is_open_3, is_open_4, is_open_5):
    """
        The logic is the following:
        We are going to close all the collapses and open the one that have been clicked
    """

    # Here the step is failing if the n-ith are None values
    try:
        ind = [n1, n2, n3, n4, n5].index(1)
    except ValueError:
        return is_open_1, is_open_2, is_open_3, is_open_4, is_open_5, 0, 0, 0, 0, 0

    is_open = [is_open_1, is_open_2, is_open_3, is_open_4, is_open_5]

    for i in range(5):
        if i == ind:
            is_open[i] = not is_open[i]
        else:
            is_open[i] = False

    return is_open + [0, 0, 0, 0, 0]


@callback(
    Output("dd-menu", "label"),
    Output("dd-button-1", "n_clicks"),
    Output("dd-button-2", "n_clicks"),
    Output("dd-button-3", "n_clicks"),
    Output("dd-button-4", "n_clicks"),
    Output(Components.GraphMap, "figure"),
    Input("dd-button-1", "n_clicks"),
    Input("dd-button-2", "n_clicks"),
    Input("dd-button-3", "n_clicks"),
    Input("dd-button-4", "n_clicks"),
    State("dd-button-1", "children"),
    State("dd-button-2", "children"),
    State("dd-button-3", "children"),
    State("dd-button-4", "children"),
    config_prevent_initial_callbacks=True
)
def update_map_color_scheme(n1, n2, n3, n4, b1_label, b2_label, b3_label, b4_label):

    if n1 > 0:
        label = "temperature"
    elif n2 > 0:
        label = "barometric_pressure_val"
    elif n3 > 0:
        label = "wind_speed_val"
    elif n4 > 0:
        label = "relative_humidity_val"
    else:
        label = "temperature"

    fig = get_map(app, coloring_parameter=label)
    print(f"New map have been created with label={label}")

    return label, 0, 0, 0, 0, fig


def main():
    init_logger("weathergov")
    app.rc = RedisClient()
    app.layout = get_layout(app)


if __name__ == "__main__":
    load_dotenv(dotenv_path="/Users/alexeylukyanov/Projects/WeatherData/.env")
    main()
    app.run_server(debug=True, use_reloader=True, port=8080)
