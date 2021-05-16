from enum import Enum

class State(Enum):
    READY = "ready",
    IN_PROGRESS = "in_progress",
    COMPLETE = "complete",