from flask import Flask
from create.config import Config
from flask_restful import Api
from flask_cors import CORS
import os

print(os.path.abspath('.'))
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('..\\frontend\\build'))
app.config.from_object(Config)
CORS(app)
api = Api(app)

from app import routes
