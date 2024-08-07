import json

from dotenv import load_dotenv
from redis import Redis

from weathergov.utils.redis_utils import RedisKeys, RedisInfo


load_dotenv()


redis_info = RedisInfo.load()

rc = Redis(
    host=redis_info.host,
    port=redis_info.port,
    password=redis_info.password,
    db=0,
    decode_responses=True
)
print(f"Successfully connected to Redis: {rc.ping()}")

station_id = "C1627"

info = rc.hgetall(RedisKeys.get_station_info_hash_key(station_id=station_id))

print(json.dumps(info, indent=2))
