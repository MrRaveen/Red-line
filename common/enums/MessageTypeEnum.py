from enum import Enum
class MessageType(str, Enum):
    """Lifecycle / event types emitted during an attack workflow."""
    START              = "start"
    NODE_ENTER         = "node_enter"
    NODE_EXIT          = "node_exit"
    ATTACK_ATTEMPT     = "attack_attempt"
    OBSERVATION        = "observation"
    FINAL_OBSERVATION  = "final_observation"
    ERROR              = "error"
