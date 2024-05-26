import logging
from typing import TYPE_CHECKING, Sequence

from iterpy.arr import Arr

from rescuetime_to_gcal import gcal
from rescuetime_to_gcal.config import config as cfg
from rescuetime_to_gcal.preprocessing import apply_metadata, merge_within_window

if TYPE_CHECKING:
    from rescuetime_to_gcal.preprocessing import ParsedEvent
    from rescuetime_to_gcal.sources.event_source import EventSource


def main(
    input_sources: Sequence["EventSource"],
    gcal_email: str,
    gcal_client_id: str,
    gcal_client_secret: str,
    gcal_refresh_token: str,
    dry_run: bool,
) -> Sequence["ParsedEvent"]:
    input_data = Arr(input_sources).map(lambda f: f()).flatten()

    sufficient_length_events = input_data.filter(lambda e: e.duration > cfg.min_duration)

    events_with_metadata = sufficient_length_events.map(
        lambda e: apply_metadata(
            event=e, metadata=cfg.metadata_enrichment, category2emoji=cfg.category2emoji
        )
    )

    included_events = events_with_metadata.filter(
        lambda e: not any(
            excluded_title.lower() in e.title.lower() for excluded_title in cfg.exclude_titles
        )
    )

    merged_events = (
        included_events.groupby(lambda e: e.title)
        .map(lambda g: merge_within_window(g[1], merge_gap=cfg.merge_gap))
        .flatten()
        .to_list()
    )

    logging.debug("Syncing events to calendar")
    gcal.sync(
        client=gcal.GcalClient(
            calendar_id=gcal_email,
            client_id=gcal_client_id,
            client_secret=gcal_client_secret,
            refresh_token=gcal_refresh_token,
        ),
        source_events=merged_events,
        dry_run=dry_run,
    )

    return merged_events
