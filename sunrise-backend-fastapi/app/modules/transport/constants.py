"""Fixed values of the transport operations module. They match the CHECK constraints in Database/Tables/T960-T985."""
from enum import Enum


class RateBasis(str, Enum):
    PER_STOP = "PER_STOP"
    DISTANCE_SLAB = "DISTANCE_SLAB"
    FLAT = "FLAT"


# An assignment takes the first rate that matches, in this order
RATE_ORDER = (RateBasis.PER_STOP, RateBasis.DISTANCE_SLAB, RateBasis.FLAT)

# fee_audit_log entity types written by this module
ENTITY_ASSIGNMENT = "transport_assignment"
ENTITY_PAUSE = "transport_pause"

DEFAULT_CUTOFF_DAY = 15
DEFAULT_DUE_DAY = 10

DEFAULT_TYPES = [
    # name, description, capacity, sort_order
    ("E-Rickshaw", "E-Rickshaw service", 6, 10),
    ("Van", "Van service", 12, 20),
    ("Bus", "Bus service", 40, 30),
]
