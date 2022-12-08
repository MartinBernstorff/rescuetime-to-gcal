from datetime import datetime
from re import S

import pandas as pd
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from pydantic import BaseModel

from log import log


class MinimalEvent(BaseModel):
    title: str
    start: datetime
    end: datetime
    timezone: str = "Europe/Copenhagen"

    def __init__(self, **data) -> None:
        super().__init__(**data)

        # Convert all datetime.datetime objects to Timestamps without tzoffset
        if self.start.tzinfo is not None:
            self.start = pd.Timestamp(self.start).tz_convert(self.timezone)
        else:
            self.start = pd.Timestamp(self.start).tz_localize(self.timezone)

        if self.end.tzinfo is not None:
            self.end = pd.Timestamp(self.end).tz_convert(self.timezone)
        else:
            self.end = pd.Timestamp(self.end).tz_localize(self.timezone)

    def to_gcsa_event(self) -> Event:
        return Event(
            title=self.title, start=self.start, end=self.end, summary=self.title
        )


class CalendarManager:
    def __init__(self):
        self.calendar = GoogleCalendar("martinbernstorff@gmail.com")
        self.timezone = self.calendar.get_settings().timezone

    def sync_df_to_calendar(
        self,
        df: pd.DataFrame,
        title_col_name: str = "title",
        start_time_col_name: str = "start_time",
        end_time_col_name: str = "end_time",
    ) -> None:
        events_in_calendar = list(
            self.calendar.get_events(
                df[start_time_col_name].min(),
                datetime.today(),
                order_by="updated",
                single_events=True,
            )
        )

        calendar_events = [
            MinimalEvent(
                title=event.summary,
                start=event.start,
                end=event.end,
                timezone=self.timezone,
            )
            for event in events_in_calendar
        ]

        for _, row in df.iterrows():
            # Set timezone to current timezone
            rescuetime_event = MinimalEvent(
                title=row[title_col_name],
                start=row[start_time_col_name],
                end=row[end_time_col_name],
            )

            if rescuetime_event not in calendar_events:
                self.calendar.add_event(rescuetime_event.to_gcsa_event())
                log.good(f"Added {rescuetime_event.title} to calendar")
            else:
                # Log with today
                log.info(
                    f"{rescuetime_event.title} at {rescuetime_event.start.strftime('%Y-%m-%d')} already exists in calendar. Skipping..."
                )
