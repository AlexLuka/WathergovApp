import random
import logging

from weathergov.utils.stations_utils import get_all_stations


logger = logging.getLogger(__name__)


def observation_station_loader():
    # TODO Get the information from Redis when the station information was updated last time.
    #   In other words, when this script was running last time.
    #   Do not run this script more frequently than once a week!
    #   If the script was running last time a week ago and must run every week (scheduled),
    #   then we must take into account how long does it take to run this script to make sure
    #   that we do not miss the next run.
    #   Alternative option would be to run it as a scheduled job/lambda on AWS
    #

    # Get all stations from the Weather.gov API
    # There should be about 45000 stations, not too many.
    stations = get_all_stations()
    logger.info(f"Random example of station info: {random.choice(stations)}")

    # TODO Load all the stations to Redis
    logger.warning(f"Loading to Redis have not been implemented yet")

    # TODO Update the timestamp when the station info was updated


def historical_data_loader():
    pass


def rt_data_loader():
    pass
