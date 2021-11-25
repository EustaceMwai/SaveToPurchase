from flask import request, jsonify
import jwt
from . import models, db
from functools import wraps
from config import SECRET_KEY, logger


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

            # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, SECRET_KEY)
            current_user = db.session.query(models.Entity_Users) \
                .filter_by(id=data['id']) \
                .first()

        except Exception as e:
            print(str(e))
            logger.error("Error {} occured as user tried to get the access token".format(e))
            return jsonify({
                'message': 'Token is invalid !!'
            }), 401

        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated