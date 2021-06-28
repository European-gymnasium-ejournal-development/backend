from flask_restful import Api, Resource, reqparse
from app.Database import JWRefreshTokens
from config import Metadata
from app.ApiHandlers import JWTVerification


class RefreshToken(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('refresh_token', location='cookies', type=str)

        args = parser.parse_args()

        if not args['refresh_token']:
            return {
                'result': 'Error!',
                'error_message': 'No refresh token provided'
            }

        result = JWRefreshTokens.get_token(args['refresh_token'])

        email = JWRefreshTokens.parse_email_from_token(args['refresh_token'])

        check_result = JWTVerification.check_access_token(args['refresh_token'])

        if not check_result[0]:
            return {
                'result': 'Error!',
                'error_message': check_result[1]
            }

        if result:
            return {
                'result': 'OK'
            }, 200, {
                'Set-Cookie': 'access_token=' +
                              JWRefreshTokens.generate_token(email, Metadata.JSON_WEB_ACCESS_TOKEN_LIFETIME)
            }
        else:
            return {
                'result': 'Error!',
                'error_message': 'Wrong refresh token!'
            }
