import argparse

from weathergov.scripts.loaders import (observation_station_loader,
                                        historical_data_loader,
                                        rt_data_loader)
from weathergov.utils.logging_utils import init_logger


"""
    Depending on type of a selected script we are going to run the corresponding 
    functionality:
    - ObservationStationsLoader
    - HistoricalDataLoader
    - RTDataLoader 
"""


def main(script_name: str):
    if script_name == "ObservationStationsLoader":
        logger.info(f"ObservationStationsLoader is running")
        observation_station_loader()
    elif script_name == "HistoricalDataLoader":
        logger.info(f"HistoricalDataLoader is running")
        historical_data_loader()
    elif script_name == "RTDataLoader":
        logger.info(f"RTDataLoader is running")
        rt_data_loader()
    else:
        logger.info(f"Unknown script {script_name}. Exiting...")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Weather Puller',
        description='It periodically pulls the data from Weather API',
        epilog='How can I help you?')

    parser.add_argument("-s", "--script", default="NotSelected")
    args = parser.parse_args()

    # Init the logger
    logger = init_logger(__name__)

    main(args.script)
