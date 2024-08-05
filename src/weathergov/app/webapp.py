import json
import logging
import dash_bootstrap_components as dbc

from dash import Dash, Input, Output, callback
from dotenv import load_dotenv
# from dash_bootstrap_components.themes import LUMEN

from weathergov.app.layout import get_layout
from weathergov.app.components import Components
from weathergov.utils.redis_utils import RedisClient


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


@callback(
    # Output('click-data', 'children'),
    Output(Components.WeatherStationInfoPanelName, 'children'),
    Output(Components.WeatherStationInfoPanelStationID, "children"),
    Output(Components.WeatherStationInfoPanelElevationAboveGround, "children"),
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
        return "", "", ""

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

    # return json.dumps(point, indent=2)
    return (point['customdata'][0],
            dbc.NavLink(
                point['customdata'][1],
                href=point['customdata'][4],
                external_link='True',
                target='_blank',
                active=True
            ),
            f"{point['customdata'][2]} {elevation_units}")


def main():
    app.rc = RedisClient()
    app.layout = get_layout(app)


if __name__ == "__main__":
    load_dotenv(dotenv_path="/Users/alexeylukyanov/Projects/WeatherData/.env")
    main()

    app.run_server(debug=True, use_reloader=True, port=8080)
