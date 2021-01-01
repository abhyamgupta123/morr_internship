from flask import Flask
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
import os, shutil
from flask_pymongo import PyMongo

app = Flask(__name__)
cors = CORS(app)

api = Api(app)
"""
  here these fields generally gets the values from '.env' file but here,
  since if maybe you have to test it in your own system hence i'm hardcoding the values so that you can test by your own.

  app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
  app.config['JWT_SECRET_KEY'] = os.getenv('FLASK_JWT')

"""
app.config['MONGO_URI'] = "mongodb+srv://abhyam:abhyam%40hackthebuild@cluster0.rl5eg.mongodb.net/contacts?retryWrites=true&w=majority"
app.config['JWT_SECRET_KEY'] = "mykey"
app.config['PROPAGATE_EXCEPTIONS'] = True
jwt = JWTManager(app)
mongo = PyMongo(app)
db = mongo.db
# db.contacts.insert_one({"test":True, "mission":"successfull"})

@app.route('/')
def hdfd():
    return "Running..."

from Contacts_project.Resources import contacts, user
# for user related API queries:-
"""
user related APIs are used for authenticated transactions, and only registered users are able to
use contact related all features. Here each user haves their own contact-books.

when user logins, it will be assigned a unique token to access all other apis featres which requires authentication.
the validity of user is kept as 5 min by default here.
"""
api.add_resource(user.register_user, '/registerUser')                           # to regster the particular user
api.add_resource(user.user_login, '/loginUser')                                 # to logging in the user
api.add_resource(user.user_profile, '/profileUser')                             # to get user profile of logined user
api.add_resource(user.user_profile_update, '/profileUserUpdate')                # to update the profile of particular logined user
api.add_resource(user.refresh_token, '/refreshToken')                           # for refreshing the token.

# for contact related API queries:-
api.add_resource(contacts.create_contact, '/contacts/createContact')            # to create contact
api.add_resource(contacts.get_all_contacts, '/contacts/getallContacts')         # to get list of all contacts
api.add_resource(contacts.get_specific_contact, '/contacts/getcontact/<string:query>')         # to get list of all contacts matching particular query.
api.add_resource(contacts.delete_contact, '/contacts/deleteContact')            # to delete particular contact
api.add_resource(contacts.update_contact, '/contacts/updateContact')            # to update the contact
