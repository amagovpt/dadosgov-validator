from enum import Enum

class TaskStatus(Enum):
    QUEUED = "queued"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"

    def __repr__(self):
        return super().__repr__()