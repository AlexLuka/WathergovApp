import json
import pytz
import random
import logging

from time import time
from datetime import datetime

from weathergov.utils.redis_utils import update_observation_stations, RedisClient
from weathergov.utils.stations_utils import get_all_stations, get_station_data


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


def historical_data_loader(env: str, worker_id: int):
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

        We need multiple loaders running in parallel. If run them locally, on my PC, they can run
        non-stop 100% of a time with just sleeping in between of calls. How do they communicate?
        That can be simple:
            1. Associate each instance with unique ID - integer starting from 0, like 0, 1, 2, 3
            2. Instance 0 is the main one always, it is going to start earlier a bit and generate
               a list of stations to be processed and send them to a queue
            3. Instances 1+ are going to listen to a queue and work until queue get empty
            4. Note that if we run this in AWS we are going to run this job weekly, and therefore must exit
               when finished. While if we run it locally in my PC this must live in docker env and run forever.
               The difference is going to be determined by env parameter
    :return:
    """
    t_ = time()

    # Create a connection to Redis
    rc = RedisClient()

    if worker_id == 0:
        # Check when the last time the queue was filled! If more than 6 days ago, then refill
        ts_last = rc.get_station_data_populated_last_time_ts()

        if time() - ts_last > 3600 * 24 * 6:
            # If time delta between last update time and the current update time is greater
            # than 6 days (we assume that we get 7 days of data), and also that we are going
            # to run this as a scheduled job
            rc.create_weather_stations_queue()
            logger.info(f"Last time data was updated more than 6 days ago. Update is required")
        else:
            logger.info(f"Data was collected on "
                        f"{datetime.fromtimestamp(ts_last, tz=pytz.timezone('America/Chicago'))} "
                        f"less than 6 days ago: delta={(time() - ts_last)/3600} hours ago")
            # we must make a return here in order to not update the time when the calculations were
            # done last time!
            return

    # Start consuming from weather stations queue and process each station individually
    while True:
        payload_str = rc.get_station_id_from_queue()

        if payload_str is None:
            # Reached the end of a queue
            break

        # If payload is not None, then try to unpack it
        payload = json.loads(payload_str)

        # We may use different processing functions based on
        # the source, but right now we have only one source: weather.gov
        station_id = payload['station_id']

        # Get the data from
        data = get_station_data(station_id=station_id)

        # Save data to Redis timeseries
        rc.add_timeseries_data(station_id=station_id, data=data)

    # Update the time when calculations have finished
    if worker_id == 0:
        # Technically, this is redundant check because we can update from
        # all the workers without any issues. However, lets update only once.
        rc.set_station_data_populated_last_time_ts(int(time()))

    logger.info(f"Data population took {(time() - t_) / 3600:.1f} hours")


def rt_data_loader():
    """
    This one is pretty much the same, except we are going to request data from
    different endpoint, and the last request time is going to be different as well.
    But the period is going to be the same. So, basically, we can use the same code
    and pass only endpoint url, Redis key where to get the last update info from,
    and coefficient +-1 that indicates if we want to get data point from past or from
    the future
    :return:
    """
    pass
