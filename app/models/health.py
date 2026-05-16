from dataclasses import dataclass, field
from typing import List


@dataclass
class Dependency:
    name: str
    status: str


@dataclass
class Health:
    datetime: str
    response_time: str
    dependencies: List[Dependency] = field(default_factory=list)
