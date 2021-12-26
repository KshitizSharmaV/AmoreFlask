##### WARNING ##### 
### Be very careful with this file. This file will revoke all the refresh tokens and user will be asked to sign in
### This is to be ran in case of hacking and it looks like the refresh tokens were lost


'''
# Also storing the metadata for the user 
# Meta data will store the revokeTime of the ID token
# This Will allow for efficient checks within the database
user = auth.get_user(uid)
# Convert to seconds as the auth_time in the token claims is in seconds.
revocation_second = user.tokens_valid_after_timestamp / 1000
metadata_ref = db.collection("metadata").document(uid)
metadata_ref.set({'revokeTime': revocation_second})
'''

'''
Access the database
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://amore-f8cd6.firebaseio.com/'})

## This function is not in use
## It takes in the idToken and returns the uid.. 
## You don't want to do that because you already have uid, so why to risk sending the uid over network
## Make use of session cookies instead i.e. session_login method
@app.route('/adminLogin', methods=['POST'])
def verify_token_uid():
    try:
        authRequestData = json.loads(request.data)
        # [START verify_token_uid]
        # id_token comes from the client app (shown above)
        decoded_token = auth.verify_id_token(authRequestData['idToken'])
        uid = decoded_token['uid']
        # [END verify_token_uid]

        logger.info("User was successfully authenticated %s" %(uid))
        return jsonify([{'message':"Successfully authenticated user", "statusCode":200}])
    
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        logger.exception("Token revoked, inform the user to reauthenticate or signOut().")
        return jsonify([{"message":"Token revoked, Please reauthenticate or signOut()","statusCode":400}])
        pass

    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        logger.exception("Token belongs to a disabled user record")
        logger.exception(traceback.format_exc())
        return jsonify([{"message":"Your accout is disabled. Please contact support","statusCode":400}])
        pass

    except auth.InvalidIdTokenError:
        # Token is invalid
        logger.exception("Token is invalid")
        logger.exception(traceback.format_exc())
        return jsonify([{"message":"Invalid token, please SignOut and try again","statusCode":400}])
        pass

    except Exception as e:
        logger.info("Wasn't able to authenticate User")
        logger.exception(traceback.format_exc())
        print(traceback.format_exc())
        return jsonify([{"message":"Failed to authenticate","statusCode":400}])
'''
