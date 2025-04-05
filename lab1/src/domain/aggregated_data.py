from dataclasses import dataclass
from datetime import datetime

from lab1.src.domain.accelerometer import Accelerometer
from lab1.src.domain.gps import Gps


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    time: datetime