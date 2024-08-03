from enum import Enum, unique


@unique
class Components(str, Enum):
    GraphMap = "graph-map"
