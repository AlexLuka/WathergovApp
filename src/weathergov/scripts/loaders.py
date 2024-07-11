import random
import logging

from weathergov.utils.redis_utils import update_observation_stations
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

    # Load all the stations to Redis
    update_observation_stations(stations)

    # TODO Update the timestamp when the station info was updated


def historical_data_loader():
    """
        The goal of this loader is to load historical data. If we try to get
        observations from a station we will get only 1 week of data. But there is
        an option to specify date and time. So, the logic for this one is going to
        be the following:
        - Pick a station: not randomly but based on when it was updated last time. If it
            was updated recently then it is going to have lower priority
        - If station has no data, then try to get the last week of data
        - If station has some data, then get the oldest data point timestamp and timestamp
            when the last data was requested. These are not the same because we may request
            data for a specific timestamp and get none. Therefore, we cannot rely on actual
            data, but on the time for which we requested the data. For every new request the
            time should be reduced by the time period.
        - Send a request to get the data and update the request time in Redis.
    :return:
    """
    pass


def rt_data_loader():
    pass
