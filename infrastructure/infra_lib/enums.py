from enum import StrEnum


class Environment(StrEnum):
    prod = "prod"
    stage = "stage"
    local = "local"
