from flask import request
from flask_restful import Resource
from google.cloud.firestore import DocumentReference

import gravitate.api_server.utils as service_utils
import gravitate.domain.event.actions as event_actions
import gravitate.domain.event.builders_new as event_builders
import gravitate.domain.event.models as event_models
from gravitate.context import Context
from gravitate.domain.event.actions import create_fb_event
from gravitate.domain.user import UserDao
from gravitate.domain.event.dao import EventDao
from . import parsers as event_parsers

db = Context.db


class UserEventService(Resource):
    """
    Handles user facebook event upload
    """

    @service_utils.authenticate
    def post(self, uid):
        """
        Creates a new event with Facebook event JSON (that is obtained from Facebook Graph API).

        ---
        tags:
          - me/events
        parameters:
          - in: body
            name: body
            schema:
              id: UserEventJSON
              type: object
              required:
                - description
                - end_time
                - start_time
                - place
                - id
              properties:
                description:
                  type: string
                  example: "Advance Sale begins Friday, 6/1 at 11AM PDT\nwww.coachella.com"
                end_time:
                  type: string
                  example: "2019-04-14T23:59:00-0700"
                start_time:
                  type: string
                  example: "2019-04-12T12:00:00-0700"
                place:
                    type: object
                    properties:
                      name:
                        type: string
                        example: "Coachella"
                      location:
                        type: object
                        properties:
                          latitude:
                            type: number
                            example: 33.679974
                          longitude:
                            type: number
                            example: -116.237221
                      id:
                        example: "20281766647"
                id:
                  type: string
                  example: "137943263736990"
        responses:
          200:
            description: user created
          400:
            description: form fields error

        :param uid:
        :return:
        """
        json_data = request.get_json()
        b = event_builders.FbEventBuilder()
        b.build_with_fb_dict(json_data)
        e: event_models.SocialEvent = b.export_as_class(event_models.SocialEvent)

        # Note that e.firestore_ref will not be set by create()
        ref: DocumentReference = EventDao().create_fb_event(e)
        e.set_firestore_ref(ref)
        dict_view = e.to_dict_view()
        dict_view["eventId"] = ref.id

        # TODO: add error handling
        UserDao().add_user_event_dict(uid, dict_view["fbEventId"], dict_view)

        return {
            "id": e.get_firestore_ref().id
        }

    @service_utils.authenticate
    def put(self, uid):
        """
        Creates many new events with a list of Facebook event JSON's (that are obtained from Facebook Graph API).
        ---
        tags:
          - me/events
        parameters:
          - in: body
            name: body
            schema:
              properties:
                data:
                  type: array
                  items:
                    $ref: "#/definitions/UserEventJSON"

        :param uid:
        :return:
        """
        json_data = request.get_json()
        event_dicts = json_data["data"]
        ids = list()

        for event_dict in event_dicts:
            event_id = create_fb_event(event_dict, uid)
            ids.append(event_id)

        return {
            "ids": ids
        }


class EventCreation(Resource):
    @service_utils.authenticate
    def post(self, uid):
        """
                TODO: implement

                This method allows the user to post an event.
                    Expect a JSON form in request.json
                For now, handle only local time in "America/Los_Angeles"

                Form fields required:
                    "eventCategory": "campus" | "social"
                    "eventLocation" (A user-defined text description such as "LAX")
                    "locationRef" (Should have been generated by earlier steps in workflow)
                    "startLocalTime"
                    "endLocalTime"
                    "pricing": 100

                Validation:
                    Reject if:
                        eventCategory is "airport", or is not one of "campus", "social"
                        locationRef is the same as any airport locationRef
                        ...
                    Allow pricing to be empty, and fill in default value



                :param uid:
                :return:
                """
        raise NotImplementedError
        # Verify Firebase auth.
        user_id = uid

        event_dict = None

        eventCategory = args["eventCategory"]

        if eventCategory == "social":
            args = event_parsers.social_event_parser.parse_args()
            event_dict = args.values()
        else:
            raise Exception("Unsupported eventCategory: {}".format(eventCategory))

        print(args)

        # Create RideRequest Object
        event = event_actions.create(args, user_id, event_category=eventCategory)

        # rideRequest Response
        response_dict = {
            "id": event.get_firestore_ref().id
        }

        return response_dict, 200


class EventAutofillService(Resource):
    """
    Handles default value for front end create event ride request view
    """

    @service_utils.authenticate
    def get(self, eventId, uid):
        """
        (NOT IMPLEMENTED) Returns default value for ride request creation form.
        ---
        tags:
         - 'events'
        parameters:
          - name: id
            in: path
            description: ID of the event to generate default values from
            required: true
            schema:
              type: string
        responses:
          '200':
            description: event form default values response
          default:
            description: unexpected error
        """
        pass


class EventService(Resource):

    def get(self, eventId):
        """
        Returns a JSON representation of an event based on a single ID.

        ---
        tags:
          - events
        # operationId: find event by id
        parameters:
          - name: id
            in: path
            description: ID of the event to fetch
            required: true
            schema:
              type: string
        responses:
          '200':
            description: event response
          default:
            description: unexpected error
        """
        event = EventDao().get_by_id(event_id=eventId)
        event_dict = event.to_dict_view()
        return event_dict
