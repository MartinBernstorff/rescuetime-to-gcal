import pandas as pd

from input_services.rescuetime import Rescuetime
from output_services.gcal.converter import df_to_gcsa_events
from output_services.gcal.syncer import CalendarSyncer
from utils.log import log

API_KEY = "B6300jX6LJHN6RU0uhZCQfOJEMrn2RfLIY0bkT_z"

if __name__ == "__main__":
    log.info("Starting script")

    rescuetime = Rescuetime(api_key=API_KEY)
    rescuetime_df = rescuetime.pull(
        perspective="interval",
        resolution_time="minute",
        anchor_date=pd.Timestamp.today(),
        lookbehind_distance=pd.Timedelta(days=1),
        titles_to_keep={
            "calendar": "Coordinating",
            "citrix": "Programming",
            "dr.dk": "Browsing",
            "facebook": "Browsing",
            "github": "Programming",
            "hey": "Browsing",
            "linkedin": "Browsing",
            "logseq": "Programming",
            "mail": "Coordinating",
            "macrumors": "Browsing",
            "reddit": "Browsing",
            "slack": "Coordinating",
            "star realms": "Gaming",
            "stackoverflow": "Programming",
            "twitter": "Browsing",
            "Visual": "Programming",
            "wandb.ai": "Programming",
            "word": "Writing",
            "youtube": "Browsing",
        },
        allowed_gap=pd.Timedelta("5 minutes") - pd.Timedelta("2 seconds"),
        min_duration="5 seconds",
    )

    events = df_to_gcsa_events(rescuetime_df)

    calendar = CalendarSyncer().sync_events_to_calendar(events)
