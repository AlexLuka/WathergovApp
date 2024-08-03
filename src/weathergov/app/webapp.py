import json
import logging

from dash import Dash, Input, Output, callback
from dotenv import load_dotenv
from dash_bootstrap_components.themes import LUMEN

from weathergov.app.layout import get_layout
from weathergov.app.components import Components
from weathergov.utils.redis_utils import RedisClient


logger = logging.getLogger(__name__)


app = Dash(
    __name__,
    title="Simple Weather App",
    external_stylesheets=[LUMEN],
    add_log_handler=logger
)


@callback(
    Output('click-data', 'children'),
    Input(Components.GraphMap, 'clickData'))
def display_click_data(click_data):
    return json.dumps(click_data, indent=2)


def main():
    app.rc = RedisClient()
    app.layout = get_layout(app)


if __name__ == "__main__":
    load_dotenv(dotenv_path="/Users/alexeylukyanov/Projects/WeatherData/.env")
    main()

    app.run_server(debug=True, use_reloader=True, port=8080)
