import argparse

from dotenv import load_dotenv

from weathergov.constants import Environment
from weathergov.scripts.loaders import (observation_station_loader,
                                        historical_data_loader,
                                        rt_data_loader)
from weathergov.utils.logging_utils import init_logger
from weathergov.scripts.data_dumper import start_data_dumper


"""
    Depending on type of a selected script we are going to run the corresponding 
    functionality:
    - ObservationStationsLoader
    - HistoricalDataLoader
    - RTDataLoader 
"""


def main(script_name: str, worker_id: int, env: Environment):
    if script_name == "ObservationStationsLoader":
        logger.info(f"ObservationStationsLoader is running")
        observation_station_loader()
    elif script_name == "HistoricalDataLoader":
        logger.info(f"HistoricalDataLoader is running")
        historical_data_loader(env=env, worker_id=worker_id)
    elif script_name == "RTDataLoader":
        logger.info(f"RTDataLoader is running")
        rt_data_loader()
    elif script_name == "DataDumper":
        logger.info(f"Starting data dumper service")
        start_data_dumper()
    else:
        logger.info(f"Unknown script {script_name}. Exiting...")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Weather Puller',
        description='It periodically pulls the data from Weather API',
        epilog='How can I help you?')

    parser.add_argument("-s", "--script", default="NotSelected")
    #
    # This can be either Local or AWS. If run in AWS, then we are going to do certain
    # things differently.
    parser.add_argument("-e", "--environment", default="Local")
    #
    # Worker ID is going to be used by a data loader that runs once a week.
    # We plan to run multiple workers to process data in parallel, and therefore
    # need different worker IDs to differentiate the workers.
    parser.add_argument("-w", "--worker-id", default=0, type=int)

    args = parser.parse_args()

    # Init the logger
    logger = init_logger("weathergov")

    # Load the environment variables if running in local environment
    # In cloud deployment all the env variables are going to be setup
    # separately, and therefore no need to load them from .env file - there
    # will be no such.

    env_ = Environment(args.environment)
    logger.info(f"Running script in {env_} environment")

    if env_ is Environment.LOCAL:
        load_dotenv()

    main(script_name=args.script,
         worker_id=args.worker_id,
         env=env_)
