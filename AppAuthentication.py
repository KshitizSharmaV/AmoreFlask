import flask
from flask import Blueprint, current_app,  Flask, jsonify, request
from firebase_admin import auth, exceptions
import traceback
import datetime

session_cookie_expires_in = datetime.timedelta(days=7)
auth_app = Blueprint('Authentication', __name__)

# Sesssion Cookies for all api authentication
# Once the user has logged in on the app from the firebase : Client side authentication
# We call session_login for server side authentication
# The function accepts idToken which is generated on client side & create a session cookie for it
# The sesssion cookie is sent back and then used further by client side for communicating with APIs
# Session cookie is validated before every api call
# The session cookie is valid for 7 days, if expired do another call from client side to sessionLogin
@current_app.route('/sessionLogin', methods=['POST'])
def session_login():
    # Get the ID token sent by the client
    id_token = request.json['idToken']
    # Set session expiration to 5 days.
    try:
        # Create the session cookie. This will also verify the ID token in the process.
        # The session cookie will have the same claims as the ID token.
        session_cookie = auth.create_session_cookie(id_token, expires_in=session_cookie_expires_in)
        response = jsonify({'message': 'Successfully authenticated user', 'statusCode': 200})
        # Set cookie policy for session cookie.
        expires = datetime.datetime.now() + session_cookie_expires_in
        response.set_cookie('session', session_cookie, expires=expires)
        current_app.logger.info("User was successfully authenticated & cookies were generated")
        return response
    except exceptions.FirebaseError:
        return flask.abort(401, 'Failed to create a session cookie')
        pass
    except Exception as e:
        current_app.logger.exception("Wasn't able to authenticate user and failed to create a session cookie")
        current_app.logger.exception(traceback.format_exc())
        return flask.abort(400, 'Failed to create a session cookie')