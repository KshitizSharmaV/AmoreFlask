from flask import Flask
from flask import jsonify, json
from flask import Response
from flask import request

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import exceptions
from firebase_admin import tenant_mgt
from firebase_admin import firestore

import traceback
import logging
from logging.handlers import TimedRotatingFileHandler

# format the log entries
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

handler = TimedRotatingFileHandler('authentication.log', when='midnight',backupCount=10)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


app = Flask(__name__)
cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/testapi', methods=['GET','POST'])
def test_api():
    return jsonify([{'message':"1234", "statusCode":200}])

## Verify the user id
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

    except Exception as e:
        logger.error("Wasn't able to Authenticate User  %s" %(uid))
        logger.error(traceback.format_exc())
        return jsonify([{"message":"Failed to authenticate","statusCode":400}])
        

if __name__ == '__main__':
    app.run(debug=True)
