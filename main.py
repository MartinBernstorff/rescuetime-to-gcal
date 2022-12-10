import pandas as pd

from df_to_gcal import CalendarManager
from log import log
from rescuetime_to_df import (
    combine_overlapping_rows,
    compute_end_time,
    get_events_containing_str,
    get_from_rescuetime,
)

if __name__ == "__main__":
    log.info("Starting script")

    # Get today as YYYY-MM-DD
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    data = get_from_rescuetime(
        perspective="interval",
        resolution_time="minute",
        restrict_begin=today,
        restrict_end=today,
    )

    events_of_interest = get_events_containing_str(
        data=data,
        strs_to_match=[
            "dr.dk",
            "facebook",
            "hey",
            "linkedin",
            "macrumors",
            "reddit",
            "star realms",
            "twitter",
            "Visual",
            "youtube",
        ],
    )
    events_of_interest = compute_end_time(data=events_of_interest)[
        ["start_time", "end_time", "title", "duration"]
    ]

    # Drop rows with duration less than 2 seconds
    events_of_interest = events_of_interest[
        events_of_interest["duration"] > pd.Timedelta("2 seconds")
    ]

    events_of_interest = combine_overlapping_rows(
        df=events_of_interest,
        start_col_name="start_time",
        end_col_name="end_time",
        duration_col_name="duration",
        group_by_col="title",
        allowed_gap=pd.Timedelta("4 minutes 55 seconds"),
    )

    # Sort events of interest by start time
    events_of_interest = events_of_interest.sort_values(by="start_time")

    calendar = CalendarManager(color_code=True)

    calendar.sync_df_to_calendar(
        df=events_of_interest,
        title_col_name="title",
        start_time_col_name="start_time",
        end_time_col_name="end_time",
    )
