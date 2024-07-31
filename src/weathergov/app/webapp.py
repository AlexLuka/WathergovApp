import logging

from dash import Dash
from dotenv import load_dotenv
from dash_bootstrap_components.themes import LUMEN

from weathergov.app.layout import get_layout


logger = logging.getLogger(__name__)


app = Dash(
    __name__,
    title="Simple Weather App",
    external_stylesheets=[LUMEN],
    add_log_handler=logger
)


def main():
    app.layout = get_layout()


if __name__ == "__main__":
    load_dotenv()
    main()

    app.run_server(debug=True, use_reloader=True, port=8080)
