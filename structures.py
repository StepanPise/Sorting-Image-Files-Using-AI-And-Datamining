from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class FilterCriteria:
    """
    Dataclass that holds filter criteria for Gallery.
    Pass it from Sidebar (UI) to Repository (DB).
    """

    person_ids: List[int] = field(default_factory=list)
    match_all: bool = False

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    country: Optional[List[str]] = None
    city: Optional[List[str]] = None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name != "__dict__":
            self._log_state()

    def _log_state(self):
        print(
            f"[FilterCriteria changed] "
            f"person_ids={self.person_ids}, "
            f"country={self.country}, "
            f"city={self.city}"
        )
