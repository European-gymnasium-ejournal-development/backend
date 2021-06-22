from app import app, api
from flask import url_for, request, flash, redirect, send_from_directory
from flask_restful import Api, Resource, reqparse
from app.ApiHandlers import HelloHandler, Login, RefreshToken


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/main')
def main():
    return serve_index()


@app.route('/admin')
def admin():
    return serve_index()


@app.route('/export')
def export():
    return serve_index()


api.add_resource(HelloHandler.HelloHandler, '/api/hello')
api.add_resource(Login.Login, '/api/login')
api.add_resource(RefreshToken.RefreshToken, '/api/refresh_token')
