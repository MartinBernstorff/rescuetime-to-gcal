import logging
from abc import ABC
from dataclasses import dataclass
from typing import Sequence

import devtools

from rescuetime_to_gcal.delta._deduper import deduper
from rescuetime_to_gcal.generic_event import GenericEvent


@dataclass(frozen=True)
class NewEvent:
    event: GenericEvent


@dataclass(frozen=True)
class UpdateEvent:
    event: GenericEvent


EventChange = NewEvent | UpdateEvent


def changeset(
    source_events: Sequence[GenericEvent], destination_events: Sequence[GenericEvent]
) -> Sequence[EventChange]:
    """Identify which changes are needed on destination for it to mirror source. Assumes all events are in the same timezone."""
    timezones = set(e.timezone for e in [*source_events, *destination_events])
    if len(timezones) != 1:
        raise ValueError(f"All events must be in the same timezone. Found {timezones}")

    deduped_events = deduper(destination_events=destination_events, source_events=source_events)

    changeset: list[EventChange] = []
    for new_event in deduped_events:
        ancestor = [
            event
            for event in destination_events
            if event.title == new_event.title and event.start == new_event.start
        ]

        if len(ancestor) > 1:
            raise ValueError(
                f"Found multiple events with the same title and start time: {ancestor}"
            )

        event_is_update = len(ancestor) != 0
        if event_is_update:
            existing_event = ancestor[0]
            existing_event.end = new_event.end
            changeset.append(UpdateEvent(event=existing_event))
        else:
            changeset.append(NewEvent(event=new_event))

    logging.info(f"Changeset: {devtools.debug.format(changeset)}")
    return changeset
