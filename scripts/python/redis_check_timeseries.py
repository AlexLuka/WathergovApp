from random import choice
from dotenv import load_dotenv
from redis import Redis
from time import time, sleep
from datetime import datetime

from weathergov.utils.redis_utils import RedisKeys, RedisInfo, RedisClient
from weathergov.constants import Metrics

load_dotenv()


redis_info = RedisInfo.load()

# rc = Redis(
#     host=redis_info.host,
#     port=redis_info.port,
#     password=redis_info.password,
#     db=0
# )
rc = RedisClient()
print(f"Successfully connected to Redis: {rc.ping()}")

#
# Get all the station IDs
station_ids = rc.get_all_station_ids()
print(f"There are {len(station_ids)} station IDs")

station_updates = rc.get_weather_station_last_data_dump_ts_all()
print(f"Data dumps: {station_updates}")

# Select one station randomly
while True:
    station_id = choice(station_ids)

    x, y = rc.get_timeseries_data(
        station_id=station_id,
        data_keyword="temperature",
        ts_from="-",
        ts_to="+"
    )
    print(f"Station {station_id}: x={len(x)}, y={len(y)}")

    if len(x) > 0:
        x1, x2 = x[0] / 1000, x[-1] / 1000
        d1 = datetime.fromtimestamp(x1)
        d2 = datetime.fromtimestamp(x2)

        ts = rc.get_weather_station_last_data_dump_ts(
            station_id=station_id,
            metric=Metrics.Temperature
        )

        print(f"Data available from {d1} to {d2} ; last dump was on {ts}")
        sleep(3)
    else:
        continue
