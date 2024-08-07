import os
import json

import numpy as np
import redis
import pandas as pd
import typing
import logging

from time import time
from datetime import datetime

from weathergov.constants import Metrics


logger = logging.getLogger(__name__)


class RedisInfo:
    _password = None
    _host = None
    _port = None

    # Add other Redis connection parameters there
    _db = 0

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        if value is None:
            self.logger.warning(f"Redis Password is not set")
        self._password = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value: str):
        if value is None:
            self.logger.warning(f"Redis Host is not set")
        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value: int):
        if value is None:
            self.logger.warning(f"Redis port is not set")
        self._port = value

    @staticmethod
    def load():
        ri = RedisInfo()
        ri.password = os.environ.get("REDIS_PASS", None)
        ri.host = os.environ.get("REDIS_HOST", None)
        ri.port = os.environ.get("REDIS_PORT", None)
        return ri


class RedisKeys:
    STATION_RT_TABLE = "weather_station:weather.gov:last_rt_update"

    # This is RT metric where we are going to keep the number of RT
    # stations overtime.
    TOTAL_STATIONS_NUM = "weather_station:weather.gov:total_number_of_stations"

    # This is a sorted set of stations that were checked at some point of time and
    # had data missed. If data is missed, we do not call an API, but instead add a
    # station to that blacklist for a certain amount of time - 24 hours for example.
    WEATHER_STATIONS_NO_DATA_BLACKLIST = "weather_station:weather.gov:no_data_stations_blacklist"

    # Set of all weather station IDs
    WEATHER_STATIONS_IDS = "weather_station:weather.gov:station_ids"

    @staticmethod
    def get_rt_data_key(station_id, data_keyword):
        return f"weather_station:weather.gov:{station_id}:data:{data_keyword}"

    @staticmethod
    def get_station_info_hash_key(station_id):
        return f"weather_station:weather.gov:{station_id}"


class RedisClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        redis_info = RedisInfo.load()

        self.rc = redis.Redis(
            host=redis_info.host,
            port=redis_info.port,
            password=redis_info.password,
            db=0,
            decode_responses=True,
            socket_keepalive=True,
            socket_timeout=60
        )

        self.script1 = self.rc.register_script(f"""
        -- Get the station ID with the latest update time
        local res = redis.call("ZPOPMIN", "{RedisKeys.STATION_RT_TABLE}")
        local time = redis.call("TIME")

        -- Set the key to the current timestamp
        redis.call("ZADD", "{RedisKeys.STATION_RT_TABLE}", time[1] * 1000 + time[2] / 1000, res[1])

        -- Return the last time when it calculations were done
        return res
        """)

    def create_weather_stations_queue(self):
        # Get all station IDs. There should be about 46000 of them
        station_ids = list(self.rc.smembers("weather_station:weather.gov:station_ids"))

        # Check if the queue is empty, if not, then no need to create anything again
        n = self.rc.llen("weather_station_process_queue")

        if n > 0:
            self.logger.info(f"Queue is not empty. Need to complete the previous computations first!")
            return

        # Put all of them into a list
        # If at some point we are going to deal with different data sources, then include data
        # source to a payload: include station ID and
        pipeline = self.rc.pipeline()

        for station_id in station_ids:
            payload = json.dumps({
                "station_id": station_id,
                "data_source": "weather.gov"
            })
            pipeline.lpush("weather_station_process_queue", payload)

        pipeline.execute()

    def get_station_id_from_queue(self) -> str:
        return self.rc.lpop("weather_station_process_queue")

    def get_station_data_populated_last_time_ts(self):
        ts_str = self.rc.get("weather_station:weather.gov:last_data_update_ts")

        if ts_str is None:
            # If we get None, then it have never been fetched before
            return 0

        # convert to integer
        return int(str(ts_str))

    def set_station_data_populated_last_time_ts(self, ts: int):
        self.rc.set("weather_station:weather.gov:last_data_update_ts", str(ts))

    def add_timeseries_data(self, station_id: str, data: dict):
        if 'timestamp' not in data.keys():
            self.logger.warning(f"Keyword 'timestamp' not found in the data")
            return
        ts = data['timestamp']

        # Get the timeseries connector
        # rc_ts = self.rc.ts()
        # rc_ts_pipe = rc_ts.pipeline()
        pipe = self.rc.pipeline()

        # TODO Create a timeseries for each parameter to avoid
        #   TSDB: the key does not exist error

        # TODO Add the last value of temperature to the station info hash

        #
        # At this point we should have timestamp, let's go over all the possible
        # data metrics and add all of them as timeseries data to Redis
        for keyword in [Metrics.Temperature,
                        "dew_point",
                        "wind_direction",
                        "wind_speed",
                        "wind_gust",
                        "barometric_pressure",
                        "sea_level_pressure",
                        "visibility",
                        "precipitation_last_3h",
                        "relative_humidity",
                        "wind_chill",
                        "heat_index"]:
            try:
                kw_data = data[keyword]
            except KeyError:
                logger.warning(f"Failed to find keyword '{keyword}' in data for station {station_id}")
                continue

            # Check if they have the same size
            if len(ts) != len(kw_data):
                logger.warning(f"Data length do not match for keyword {keyword}: "
                               f"len(kw_data)={len(kw_data)} != {len(ts)} = len(ts)")
                continue

            # These are the most recent value and corresponding timestamp in milliseconds
            val_max_ts, max_ts = 0, 0

            # Here we have the same length of ts and data and can insert it to Redis
            # First we need to convert the timestamp to unix time
            for tsi, value in zip(ts, kw_data):
                # Convert time to unix epoch timestamp in milliseconds
                tsi_unix = int(datetime.strptime(tsi, "%Y-%m-%dT%H:%M:%S%z").timestamp() * 1000)

                key = RedisKeys.get_rt_data_key(station_id, keyword)

                if tsi_unix > max_ts:
                    max_ts = tsi_unix
                    val_max_ts = value

                # Add to timeseries
                # rc_ts_pipe.add(f"weather_station:weather.gov:{station_id}:data:{keyword}",
                #                tsi_unix, value,
                #                duplicate_policy="FIRST")
                pipe.ts().add(key,
                              tsi_unix,
                              value,
                              duplicate_policy="FIRST")

            # Add the most recent value to station hash
            pipe.hset(RedisKeys.get_station_info_hash_key(station_id=station_id), f"{keyword}_ts", str(max_ts))
            pipe.hset(RedisKeys.get_station_info_hash_key(station_id=station_id), f"{keyword}_val", val_max_ts)

            # Execute transaction
            pipe.execute()
            logger.info(f"{len(ts)} new data points added to {keyword} data for station {station_id}")

        self.logger.info(f"Data for station {station_id} have been added to Redis")

    def get_rt_update_station(self):
        """
        :return: A station that needs to be updated basd on the value
            of last_update_ts
        """
        try:
            station_id, last_update_ts = self.script1()
        except ValueError:
            # This is possible if script returns an empty list
            station_id = None
            last_update_ts = 0
            logger.warning(f"Failed to execute the script")
        except redis.exceptions.ResponseError:
            station_id = None
            last_update_ts = 0
            logger.warning(f"Failed to execute the script")

        last_update_ts = int(float(last_update_ts))
        return station_id, last_update_ts

    def update_observation_stations(self, stations: list):
        """
            Save observation stations to Redis HASH
            under "weather_station:weather.gov:ABCD23"
            where the latter is the station ID.

            In addition, create a set of all the station IDs:
                "weather_station:weather.gov:station_ids"

        :param stations:
        :return:
        """

        logger.info(f"Successfully connected to Redis")

        pipeline = self.rc.pipeline()

        for station in stations:
            station_id = station["station_id"]

            #
            pipeline.hset(RedisKeys.get_station_info_hash_key(station_id=station_id), mapping=station)

            #
            pipeline.sadd(RedisKeys.WEATHER_STATIONS_IDS, station_id)

            # Add a station to a sorted set with default value -1 - timestamp when it was updated.
            # First timestamp is going to be -1. When update in real-time we are going to have a
            # loader that will get the timestamp and update it to another one - actual integer/float
            # timestamp when the RT data was loaded
            pipeline.zadd(RedisKeys.STATION_RT_TABLE, {station_id: -1})

        pipeline.execute()
        logger.info(f"Stations info was updated in Redis")

        # Update the station tracker: how many stations there were on a specific date.
        # This is going to be a timeseries. On July 10, 2024, there were 46483 stations
        rc_ts = self.rc.ts()
        rc_ts.add(RedisKeys.TOTAL_STATIONS_NUM, int(time()), len(stations), duplicate_policy="FIRST")

    def is_station_in_blacklist(self, station_id: str) -> (bool, float):
        score = self.rc.zscore(RedisKeys.WEATHER_STATIONS_NO_DATA_BLACKLIST, station_id)

        if score is None:
            return False, score
        return True, score

    def get_observation_stations_info(self):
        station_ids = list(self.rc.smembers("weather_station:weather.gov:station_ids"))

        pipeline = self.rc.pipeline()

        for station_id in station_ids:
            pipeline.hgetall(f"weather_station:weather.gov:{station_id}")
        data = pipeline.execute()

        # Add the most recent data to the plot?
        for station_id in station_ids:
            pipeline.ts().get(RedisKeys.get_rt_data_key(station_id, "temperature"))
        ts_data = pipeline.execute(raise_on_error=False)

        ts_data_updated = list()

        for value, station_id in zip(ts_data, station_ids):
            if isinstance(value, tuple):
                ts_data_updated.append(
                    {
                        'station_id': station_id,
                        'ts': value[0],
                        'temperature': value[1] if value[1] > -99911990 else np.nan
                    }
                )
            elif isinstance(value, redis.exceptions.ResponseError):
                ts_data_updated.append(
                    {
                        'station_id': station_id,
                        'ts': int(time() * 1000),
                        'temperature': np.nan
                    }
                )
            else:
                ts_data_updated.append(
                    {
                        'station_id': station_id,
                        'ts': int(time() * 1000),
                        'temperature': np.nan
                    }
                )

        df_ts = pd.DataFrame(ts_data_updated)
        df = pd.DataFrame(data)

        # return pd.DataFrame(data)
        return pd.merge(df, df_ts, on='station_id')

    def get_timeseries_data(self,
                            station_id: str,
                            data_keyword: str,
                            ts_from: int,
                            ts_to: int) -> (list, list):
        data: list
        try:
            data = self.rc.ts().range(
                RedisKeys.get_rt_data_key(station_id, data_keyword),
                ts_from,
                ts_to)
        except redis.ResponseError:
            return [], []

        n = 0
        while n < len(data):
            if data[n][1] < -99911990:
                data.pop(n)
                continue
            n += 1

        try:
            x, y = zip(*data)
        except ValueError:
            return [], []
        return x, y

    def get_timeseries_data_multi(self,
                                  station_id: str,
                                  data_keywords: typing.List[str],
                                  ts_from: int,
                                  ts_to: int) -> typing.Dict[str, typing.Tuple[list, list]]:
        """
            Note that this is better to rewrite with Redis pipeline logic. The only thing is that
            it may cause the error if some station and keyword do not exist. Therefore, update
            the logic of time series data creation before updating this method.
        :param station_id:
        :param data_keywords:
        :param ts_from:
        :param ts_to:
        :return:
        """
        data = dict()
        for data_keyword in data_keywords:
            data[data_keyword] = self.get_timeseries_data(station_id=station_id,
                                                          data_keyword=data_keyword,
                                                          ts_from=ts_from,
                                                          ts_to=ts_to)
        return data
