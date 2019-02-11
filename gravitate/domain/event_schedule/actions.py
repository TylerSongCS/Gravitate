from typing import Type

from . import CTX
from gravitate.domain.event_schedule.builders import EventScheduleBuilder
from gravitate.models import RideRequest, Location, AirportRideRequest, AirportLocation, SocialEventRideRequest, \
    SocialEventLocation, Orbit

def create_event_schedule(ride_request: Type[RideRequest], location: Type[Location]):

    # Validate that type of location and type of ride request match
    if isinstance(ride_request, AirportRideRequest):
        assert isinstance(location, AirportLocation)
    elif isinstance(ride_request, SocialEventRideRequest):
        assert isinstance(location, SocialEventLocation)
    else:
        raise NotImplementedError("Unsupported ride request type: {}".format(type(ride_request)))

    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    event_schedule_builder.build_orbit(pending=True)
    return event_schedule_builder.export()


def create_event_schedule_orbit(ride_request: Type[RideRequest], location: Type[Location], orbit: Orbit):
    event_schedule_builder = EventScheduleBuilder()
    event_schedule_builder.build_ride_request(ride_request)
    event_schedule_builder.build_location(location)  # Note that location=None defaults to LAX as destName
    event_schedule_builder.build_orbit(pending=False, orbit=orbit)
    return event_schedule_builder.export()