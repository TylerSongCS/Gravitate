"""
Reference: flask-restful docs
"""

from functools import wraps, partial

from firebase_admin import auth
from flask import request
from flask_restful import abort

from gravitate.config import Context
import warnings

# Flag for whether main app is in TESTING mode
TESTING_MODE = False
if TESTING_MODE is True:
    warnings.warn("Testing mode is True. Set to False before release. ")


# For Testing Purposes. If not in TESTING mode, the function verfifies the token with FirebaseApp.
# Otherwise, a fixed uid will be returned in the format {"uid":"testuid1"}
auth_verify_id_token = None
if TESTING_MODE:
    def mock_auth_verify_id_token(*args, **kwargs):
        return {
            "uid": "testuid1"
        }
    auth_verify_id_token = mock_auth_verify_id_token
else:
    auth_verify_id_token = auth.verify_id_token


def default_gravitate_authentication(id_token) -> (str, int):
    try:
        # Verify the ID token while checking if the token is revoked by
        # passing check_revoked=True.
        decoded_token = auth_verify_id_token(id_token, check_revoked=True, app=Context.firebaseApp)
        # Token is valid and not revoked.
        uid = decoded_token['uid']
        return uid, 200
    except auth.AuthError as exc:
        if exc.code == 'ID_TOKEN_REVOKED':
            # Token revoked, inform the user to reauthenticate or signOut().
            return None, 401
        else:
            # Token is invalid
            return None, 402


def authenticate(func):
    """
        Wraps a resource to provide authentication.
        Note that the resource need to take uid in kwargs
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        id_token = request.headers['Authorization'].split(' ').pop()
        uid, status_code = default_gravitate_authentication(id_token)  # custom account lookup function

        if status_code == 401:
            abort(401, 'Unauthorized. Token revoked, inform the user to reauthenticate or signOut(). ')
        elif status_code == 402:
            abort(402, 'Invalid token')

        if uid:
            func_acct = partial(func, uid=uid)
            return func_acct(*args, **kwargs)

        abort(401)

    return wrapper
