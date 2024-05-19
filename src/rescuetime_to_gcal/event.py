import datetime  # noqa: TCH003
from typing import Optional

import pydantic

from rescuetime_to_gcal.config import RecordCategory  # noqa: TCH001


class Event(pydantic.BaseModel):
    title: str
    start: datetime.datetime
    end: datetime.datetime
    category: Optional[RecordCategory] = None
    timezone: str = "UTC"
    gcal_event_id: Optional[str] = None

    @property
    def duration(self) -> "datetime.timedelta":
        return self.end - self.start

    def __repr__(self) -> str:
        return f"Event(title={self.title}, {self.start} to {self.end}, {self.timezone})"
