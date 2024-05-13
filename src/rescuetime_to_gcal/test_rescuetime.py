import copy
import datetime
import os
import random
from random import shuffle

from rescuetime_to_gcal.rescuetime import Event, Rescuetime


class FakeEvent(Event):
    title: str = "fake title"
    start: datetime.datetime = datetime.datetime(2023, 1, 1, 0, 0)
    end: datetime.datetime = datetime.datetime(2023, 1, 1, 0, 0)


def test_get_data():
    result = Rescuetime(api_key=os.environ["RESCUETIME_API_KEY"])._get_data(
        api_key=os.environ["RESCUETIME_API_KEY"],
        url="https://www.rescuetime.com/anapi/data",
        perspective="interval",
        resolution_time="minute",
        restrict_begin=None,
        restrict_end=None,
    )
    assert isinstance(result[0], Event)


def test_filter_by_title():
    events = [
        FakeEvent(
            title="tes",
        ),
        FakeEvent(
            title="test2",
        ),
        FakeEvent(
            title="test3",
        ),
    ]
    filtered_events = Rescuetime._filter_by_title(data=events, strs_to_match=["test"])
    assert len(filtered_events) == 1
    assert filtered_events[0].title == "tes"


def test_merge_events_within_window():
    events = [
        FakeEvent(  # Event 1 start
            title="test1",
            start=datetime.datetime(2023, 1, 1, 0, 0),
            end=datetime.datetime(2023, 1, 1, 0, 0),
        ),
        FakeEvent(  # Merge with previous event
            title="test1",
            start=datetime.datetime(2023, 2, 1, 0, 0),
            end=datetime.datetime(2024, 1, 1, 0, 0),
        ),
        FakeEvent(  # Merge with previous event
            title="test1",
            start=datetime.datetime(2024, 3, 1, 0, 0, 0),
            end=datetime.datetime(2025, 1, 1, 0, 0, 0),
        ),
        FakeEvent(  # Do not merge
            title="test1",
            start=datetime.datetime(2030, 1, 1, 0, 0, 1),
            end=datetime.datetime(2035, 1, 1, 0, 0, 2),
        ),
        FakeEvent(  # Different title, but within window, do not merge
            title="test2",
            start=datetime.datetime(2023, 1, 1, 0, 0, 3),
            end=datetime.datetime(2023, 1, 1, 0, 0, 4),
        ),
        FakeEvent(  # Starts within end of merged window, merge
            title="test1",
            start=datetime.datetime(2024, 12, 31, 23, 59, 59),
            end=datetime.datetime(2026, 1, 1, 0, 0, 0),
        ),
    ]

    for i in range(10):
        random.seed(i)
        shuffled_events = copy.deepcopy(events)
        shuffle(shuffled_events)
        # Shuffle events to ensure the test is order-independent

        combined = Rescuetime._merge_events_within_window(
            events=shuffled_events,
            group_by=lambda e: e.title,
            merge_gap=datetime.timedelta(days=365 * 1.5),
        )

        assert sorted(combined, key=lambda e: e.start) == [
            FakeEvent(
                title="test1",
                start=datetime.datetime(2023, 1, 1, 0, 0),
                end=datetime.datetime(2026, 1, 1, 0, 0, 0),
            ),
            FakeEvent(
                title="test2",
                start=datetime.datetime(2023, 1, 1, 0, 0, 3),
                end=datetime.datetime(2023, 1, 1, 0, 0, 4),
            ),
            FakeEvent(
                title="test1",
                start=datetime.datetime(2030, 1, 1, 0, 0, 1),
                end=datetime.datetime(2035, 1, 1, 0, 0, 2),
            ),
        ]
