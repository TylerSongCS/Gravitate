# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO adapt with https://flask-restful.readthedocs.io/en/latest/quickstart.html#a-minimal-api

# [START gae_flex_quickstart]
import logging

# APScheduler for automatic grouping per interval
# Reference: https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask/38501429
# Deprecated
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from flask_restful import reqparse, Api, Resource
from flasgger import APISpec, Swagger
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from google.auth.transport import requests

from gravitate.api_server import errors as service_errors
from gravitate.api_server.event.services import EventService, EventCreation, UserEventService, EventAutofillService
from gravitate.api_server.group_task.services import GroupCronTasksService
from gravitate.api_server.grouping_service import OrbitForceMatchService, DeleteMatchServiceNew
from gravitate.api_server.ride_request.services import LuggageService, RideRequestPost, AccommodationService
from gravitate.api_server.ride_request.services import RideRequestService, RideRequestCreation
from gravitate.api_server.user_service import UserService, UserNotificationService
from gravitate.api_server.group_task import GroupTasksService
from gravitate.api_server.orbit_service import OrbitCommandService, OrbitService, RideRequestOrbitService
from gravitate.api_server.utils import authenticate
from gravitate.context import Context
from gravitate import schemas

# Firebase Admin SDK
# Deprecated: Moved to be invoked by app engine cron on '/groupAll'
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(refreshGroupAll, 'interval', minutes=1)
# sched.start()

# Flasgger docs
# Create an APISpec
spec = APISpec(
    title='Gravitate REST API',
    version='0.0.1',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)


# Initialize Flask
firebase_request_adapter = requests.Request()
app = Flask(__name__)

db = Context.db
parser = reqparse.RequestParser()


class EndpointTestService(Resource):
    method_decorators = [authenticate]

    def post(self, uid):
        """
        * This method handles a POST/PUT call to './authTest' to test that front end Auth
            is set up correctly. 
        If the id_token included in 'Authorization' is verified, the user id (uid)
            corresponding to the id_token will be returned along with other information. 
        Otherwise, an exception is thrown

        """

        # Verify Firebase auth.
        data = request.get_json()
        responseDict = {'uid': uid, 'request_data': data}
        return responseDict, 200


api = Api(app, errors=service_errors.errors)

# User Related Endpoints
api.add_resource(UserService, '/users/<string:uid>')
api.add_resource(UserNotificationService, '/users/<string:uid>/messagingTokens')
api.add_resource(UserEventService, '/me/events')

# Ride Request Related Endpoints
api.add_resource(RideRequestPost, '/rideRequests')
api.add_resource(RideRequestService, '/rideRequests/<string:rideRequestId>')
api.add_resource(DeleteMatchServiceNew, '/rideRequests/<string:rideRequestId>/unmatch')
api.add_resource(LuggageService, '/rideRequests/<string:rideRequestId>/luggage')
api.add_resource(AccommodationService, '/rideRequests/<string:rideRequestId>/accommodation')
api.add_resource(RideRequestOrbitService, '/rideRequests/<string:rideRequestId>/orbit')

# Event Related Endpoints
api.add_resource(EventCreation, '/events')
api.add_resource(EventService, '/events/<string:eventId>')
api.add_resource(EventAutofillService, '/events/<string:eventId>/defaultRide')

# Grouping Related Endpoints
api.add_resource(GroupTasksService, '/groupTasks')
api.add_resource(GroupCronTasksService, '/groupAll')
api.add_resource(OrbitForceMatchService, '/devForceMatch')

# Orbit Related Endpoints
api.add_resource(OrbitCommandService, '/orbits/<string:orbitId>/command')
api.add_resource(OrbitService, '/orbits/<string:orbitId>')

# Endpoint for Testing Purposes
api.add_resource(EndpointTestService, '/endpointTest')

# No longer used
api.add_resource(RideRequestCreation, '/requestRide/<string:rideCategory>')
# api.add_resource(AirportRideRequestCreationService, '/airportRideRequests')
# api.add_resource(DeleteMatchService, '/deleteMatch')


@app.route('/contextTest', methods=['POST', 'PUT'])
def add_noauth_test_data():
    """ Description
        This endpoint receives a REST API "post_json" call and stores the 
            json in database collection contextText. If set up correctly, 
            the client receives the id of the json inserted. 
        Note that this call does not test Auth token. 

    :raises:

    :rtype:
    """

    current_ride_request_json = request.get_json()
    print(current_ride_request_json)

    ride_requests_ref = db.collection(u'contextText')
    current_ride_request_ref = ride_requests_ref.document()
    current_ride_request_id = current_ride_request_ref.id
    current_ride_request_ref.set(current_ride_request_json)
    return current_ride_request_id, 200


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # flasgger for hosting REST API docs
    template = spec.to_flasgger(
        app,
        definitions=[schemas.LuggageCollectionSchema, schemas.LuggageItemSchema],
        # paths=[random_pet]
    )
    swagger = Swagger(app, template=template)
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
