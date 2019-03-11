import unittest
from gravitate.domain.event.models import Event, SocialEvent, AirportEvent
from test import context
from test.store import getEventDict

db = context.Context.db


class EventModelTest(unittest.TestCase):

    maxDiff = None

    def testEventFactory(self):
        eventDict = {
            "eventCategory": "airport",
            "airportCode": "LAX",
            "isClosed": False,
            "targets": [
                {
                    'eventCategory': 'airport',
                    'toEvent': True,
                    'arriveAtEventTime': {'earliest': 1545033600, 'latest': 1545119999}
                },
                {
                    'eventCategory': 'airport',
                    'toEvent': False,
                    'leaveEventTime': {'earliest': 1545033600, 'latest': 1545119999}
                }
            ],
            "localDateString": "2018-12-17",
            "pricing": 123456789,
            "parkingInfo": {
                "parkingAvailable": False,
                "parkingPrice": 0,
                "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            "locationRef": "/locations/testlocationid1",
            "participants": []
        }
        event = AirportEvent.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)


class SocialEventModelTest(unittest.TestCase):

    def testEventFactory(self):
        d = {
            "eventCategory": "social",
            "participants": [
            ],
            "eventLocation": "Las Vegas Convention Center",
            "startTimestamp": 1545033600,
            "endTimestamp": 1545119999,
            "pricing": 100,
            "isClosed": False,
            "parkingInfo": {
                "parkingAvailable": False, "parkingPrice": 0, "parkingLocation": "none"
            },
            "description": "what the event is",
            "name": "name of the event",
            "locationRef": "/locations/testlocationid1"
        }
        eventDict = d
        event = SocialEvent.from_dict(eventDict)
        # Assert that event converts to the same dict that generated the event
        self.assertDictEqual(event.to_dict(), eventDict)