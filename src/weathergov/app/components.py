from enum import Enum, unique


@unique
class Components(str, Enum):
    GraphMap = "graph-map"

    WeatherStationInfoPanelName = "ws-info-panel-name"
    WeatherStationInfoPanelStationID = "ws-info-panel-station-id"
    WeatherStationInfoPanelElevationAboveGround = "ws-info-panel-elevation-above-round"
    WeatherStationInfoPanelStationURL = "ws-info-panel-station-url"

    @staticmethod
    def get_collapse_label_id(label: str):
        lab = "-".join(label.lower().split())
        return f"collapse-button-{lab}"

    @staticmethod
    def get_collapse_id(label: str):
        lab = "-".join(label.lower().split())
        return f"collapse-pane-{lab}"

    @staticmethod
    def get_collapse_graph_id(label: str):
        lab = "-".join(label.lower().split())
        return f"collapse-graph-{lab}"
