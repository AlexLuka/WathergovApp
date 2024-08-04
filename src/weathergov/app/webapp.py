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
    Output('click-data', 'children'),
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
        return ""

    point = click_data['points'][0]

    # Additional data is included into customdata

    # point_index = point['pointIndex']

    # point['station_id'] = app.df.loc[point_index, 'station_id']
    # point['station_name'] = app.df.loc[point_index, 'station_name']
    # point['station_timezone'] = app.df.loc[point_index, 'station_timezone']
    # point['elevation'] = app.df.loc[point_index, 'elevation']
    # point['station_url'] = app.df.loc[point_index, 'url']

    return json.dumps(point, indent=2)


def main():
    app.rc = RedisClient()
    app.layout = get_layout(app)


if __name__ == "__main__":
    load_dotenv(dotenv_path="/Users/alexeylukyanov/Projects/WeatherData/.env")
    main()

    app.run_server(debug=True, use_reloader=True, port=8080)
