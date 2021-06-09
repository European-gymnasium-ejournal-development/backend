from flask import Flask
from config import Config
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS


app = Flask(__name__, static_url_path='', static_folder='..\\..\\frontend\\build')
app.config.from_object(Config)
CORS(app)
api = Api(app)

from app import routes
