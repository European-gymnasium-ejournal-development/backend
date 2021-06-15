from flask_restful import Api, Resource, reqparse
from app.Database import JWRefreshTokens
from config import Metadata


class RefreshToken(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('refresh_token', type=str)

        args = parser.parse_args()

        if not args['refresh_token']:
            return {
                'result': 'Error!',
                'error_message': 'No refresh token provided'
            }

        result = JWRefreshTokens.get_token(args['refresh_token'])

        email = JWRefreshTokens.parse_email_from_token(args['refresh_token'])

        if result:
            return {
                'result': 'OK',
                'access_token': JWRefreshTokens.generate_token(email, Metadata.JSON_WEB_ACCESS_TOKEN_LIFETIME)
            }
        else:
            return {
                'result': 'Error!',
                'error_message': 'Wrong refresh token!'
            }
