import logging
import itertools
import os

import pandas as pd

from time import sleep, time
from datetime import datetime, timedelta

from weathergov.constants import Metrics
from weathergov.utils.redis_utils import RedisClient


"""
    This service should connect to Redis and do the following:
    - On the first day of every month it must clean up the Redis. Specifically, we are going to store
      only 1 week of data in Redis, this means that on 8th day of every month it should remove the data 
      for the previous month.
    - Also, on day 1 of each month it must save a time series to parquet files for long term storage. I do 
      not have capacity for a database at the moment. Also, I don't need the historical data at the moment 
      
    Why do I need this service? Mainly because I am working on my laptop and keep adding data to my Redis 
    server and memory consumption increasing, even though I do not need all of these data at the moment. 
    In the future I probably will use a streaming server like RabbitMQ to save the data to the right place. 
"""


logger = logging.getLogger(__name__)


def start_data_dumper():

    while True:
        # - Create a data dump
        data_dumper()

        # Remove data weekly
        data_cleaner()

        # - Remove the data that can be removed
        # Sleep for an hour
        logger.info(f"Going to sleep for 24 hours")
        sleep(3600 * 24)


def data_dumper():
    # First of all check if the dump have been done this month already. For that,
    # we are going to check specific key in Redis that has the time when each station data was
    # dumped. To be specific

    rc = RedisClient()

    station_ids = rc.get_all_station_ids()
    logger.info(f"Going to dump data for {len(station_ids)} stations")

    # A dictionary with all the keys and all the updates
    station_updates = rc.get_weather_station_last_data_dump_ts_all()

    # Current datetime in UTC
    current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_date_str = current_date.strftime("%Y%m")

    # Previous month and year
    previous_date = current_date - timedelta(days=10)

    for station_id, metric in itertools.product(station_ids, Metrics):
        # Check if we have already updated that station
        try:
            last_update = station_updates[f"{station_id}:{metric}"]
        except KeyError:
            last_update = 0

        # Convert the last update to datetime in UTC tz
        last_update_date = datetime.fromtimestamp(last_update)

        # Check if the station was updated in THIS month, if yes, then skip
        # Notice that we must check only Year and Month, but not day as we don't
        # relly care what day is today.
        last_update_date_str = last_update_date.strftime("%Y%m")

        if last_update_date_str == current_date_str:
            # This means that we have made data dump for the selected station and metric this month
            logger.info(f"Station {station_id}:{metric} for previous month has been dumped already")
            continue

        if last_update_date.day == 1:
            logger.info(f"Station {station_id}:{metric} should not be updated on the first day of a month")
            continue

        # If we reach this line, this means that we have not made a data dump for this month, therefore,
        # let's do it! First, we must get the UTC timestamps for previous month
        dt_from = datetime(previous_date.year, previous_date.month, 1, 0, 0, 0)
        dt_to = current_date

        ts_from = int(dt_from.timestamp() * 1000)
        ts_to = int(dt_to.timestamp() * 1000)

        # Get timeseries data for 1 month
        x, y = rc.get_timeseries_data(
            station_id=station_id,
            data_keyword=metric,
            ts_from=ts_from,
            ts_to=ts_to
        )

        # Save data locally, going to save to S3 in the future
        df = pd.DataFrame({"timestamp": x, "value": y})
        df.to_parquet(
            os.path.join(
                f"{os.environ.get('DUMP_DATA_DIR', '.')}",
                f"{station_id}-{metric}-{previous_date.strftime('%Y-%m')}.parquet"),
            index=False
        )
        logger.info(f"Successfully dumped {metric} data for station {station_id} to a file "
                    f"for {previous_date.strftime('%Y-%m')}")

        # Update info in Redis that the data was dumped
        rc.set_weather_station_last_data_dump_ts(
            station_id=station_id,
            metric=metric,
            ts=int(time() * 1000)
        )
        logger.info(f"Last dump ts updated in Redis for station_id={station_id} and metric={metric}")

    # Second, make sure that the data dump is made not earlier than the 2nd day of a month
    pass


def data_cleaner():
    """
        This one should do the following:
        - If day of a month is greater than 8, then we remove all
          the data from Redis up to the last day of a previous month

        - Also, we do it only if the data have been saved this month already
    """
    rc = RedisClient()

    station_ids = rc.get_all_station_ids()
    logger.info(f"Going to dump data for {len(station_ids)} stations")

    # A dictionary with all the keys and all the updates
    station_updates = rc.get_weather_station_last_data_dump_ts_all()

    # Current datetime in UTC
    current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_date_str = current_date.strftime("%Y%m")

    # Previous month and year
    # previous_date = current_date - timedelta(days=10)

    for station_id, metric in itertools.product(station_ids, Metrics):
        # Check if we have already updated that station
        try:
            last_update = station_updates[f"{station_id}:{metric}"]
        except KeyError:
            logger.info(f"Data for station={station_id} and metric={metric} have never been saved before")
            continue

        # Convert the last update to datetime in UTC tz
        last_update_date = datetime.fromtimestamp(last_update)

        # Check if the station was updated in THIS month, if yes, then skip
        # Notice that we must check only Year and Month, but not day as we don't
        # relly care what day is today.
        last_update_date_str = last_update_date.strftime("%Y%m")

        if last_update_date_str != current_date_str:
            # This means that we have made data dump for the selected station and metric this month
            # This means that the data for the previous month can be removed
            logger.info(f"Station {station_id}:{metric} for previous month has been dumped already")
            continue

        if datetime.utcnow().day < 8:
            logger.info(f"Station {station_id}:{metric} data should not be removed in the first week of a month")
            continue

        logger.info(f"We can remove data for the previous month up to {current_date - timedelta(days=1)}")

        # Convert the data_to to unix timestamp in milliseconds
        ts_to = int(current_date.timestamp() * 1000)

        # Let's truncate the timeseries
        rc.remove_timeseries_data(station_id=station_id, metric=metric, ts_from="-", ts_to=ts_to)
