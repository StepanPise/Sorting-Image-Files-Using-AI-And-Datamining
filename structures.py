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

    include_unassigned: bool = False

    match_all: bool = False

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    location_query: Optional[str] = None
