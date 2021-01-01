from flask_restful import Resource, reqparse, request
from flask import Response, render_template
from Contacts_project import db
from flask_jwt_extended import (create_access_token, decode_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, jwt_optional)
import os, shutil
import base64, uuid, time
from hashlib import sha256

class register_user(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help = 'This field cannot be blank', required = True)
        parser.add_argument('name', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        username = data['username'].lower()
        email = data['email'].lower()
        password = data['password']
        name = data['name']
        if(db.users.find_one({'email': email}) or db.users.find_one({'username' : username})):
            return {'message': 'User already exists'}
        user = {
            'username' : username,
            'name' : name,
            'email' : email,
            'password' : password
        }
        try:
            db.users.insert(user)
        except:
            return {'message' : "Some Error occured while registering"}
        else:
            return {
            'message': 'User {} is created'.format(data['username']),
            'username' : f"{data['username']}"
            }

class user_login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help = 'This field cannot be blank', required = True)
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        if('@' in data['id']):
            user = db.users.find_one({'email': data['id'].lower() })
        else:
            user = db.users.find_one({'username': data['id'].lower() })
        if(user):
            if(user['password'] == data['password']):
                access_token = create_access_token(identity = user['username'])
                refresh_token = create_refresh_token(identity = user['username'])
                return {
                'message': 'Logging in User {}'.format(user['username']),
                'name': user['name'],
                'username':user['username'],
                'access_token': access_token,
                'refresh_token': refresh_token
                }
                # print(user['name'] + user['username'])
                print("looed in user" + user['username'])
            else:
                return {'message': 'Invalid Credentials'}
        else:
            return {'message': 'User does not exists'}

class user_profile(Resource):
    def get(self, username):
        user = db.users.find_one({'username': username.lower()})
        if (user != None):
            del user['_id']
            del user['password']
            return user
        else:
            return {'message': 'User does not exists'}


class user_profile_update(Resource):
    @jwt_required
    def post(self):
        _user = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('name', help = 'This field can be blank', required = True)
        parser.add_argument('email', help = 'This field can be blank', required = True)
        parser.add_argument('password', help = 'This field can be blank', required = True)
        data = parser.parse_args()
        _name = data['name']
        _email = data['email']
        _password = data['password']
        query = { "username": _user }
        values = {}
        if (db.users.find_one(query)):
            values['name'] = _name
            values['email'] = _email
            values['password'] = _password
            query_update = { "$set": values }
            try:
                db.users.update_one(query, query_update)
                return {"message" : "Information updated successfully"}
            except Exception as e:
                print("could not able to update the info")
                print("Exception", e)
                return Response("{'message': 'Sorry due to some reason the information is not updated..!!'}", status=500, mimetype='application/json')
        else:
            return Response("{'message': 'User not exist'}", status=404, mimetype='application/json')

class refresh_token(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
