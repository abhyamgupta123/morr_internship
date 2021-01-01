from flask_restful import Resource, reqparse, request
from flask import Response, render_template
from Contacts_project import db
from flask_jwt_extended import (create_access_token, decode_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, jwt_optional)
import os, shutil
import uuid


class create_contact(Resource):

    """
    This is the create method, used for creating contacts for particular logined user.
    Only logined users can able to access this feature, provided by their specific unique access token, which
    they will get after logging in.

    """

    @jwt_required
    def post(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('name', help = 'This field cannot be blank', required = True)
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        parser.add_argument('number', help = 'This field can be blank', required = False)
        data = parser.parse_args()
        contactId = str(uuid.uuid4())
        email = data['email'].lower()
        name = data['name']

        try:
            number = data['number']
        except :
            number = None

        if(db.contacts.find_one({'email': email, 'owner' : username})):
            return {'message': 'Contact already exists'}

        # handling else
        contact = {
            '_id': contactId,
            'name' : name,
            'email' : email,
            'number' : number,
            'owner' : username
        }
        try:
            db.contacts.insert(contact)
        except:
            return {'message' : "Some Error occured while adding contacts"}
        else:
            return {
            'message': 'Contact < {} > is created'.format(contact),
            'username' : f"{username}"
            }


class get_all_contacts(Resource):

    """
    This method returns all the contacts for partcular logged user in
    it's contact-book.

    """

    @jwt_required
    def get(self):
        username = get_jwt_identity()
        all_contacts = []
        try:
            contacts = db.contacts.find({'owner' : username})
            for i in contacts:
                all_contacts.append(i)
            # print('contacts is', all_contacts)
            return all_contacts
        except Exception as e:
            print(e)
            return Response("{'message': 'some internal server error occured'}", status=500, mimetype='application/json')


class get_specific_contact(Resource):

    """
    This method returns all the contacts matched to particular query string.
    Max limit of the contacts is 10, but you can specify as per your requirement.

    the string of the query matches with the 'email' and 'name' fileds in the NoSQL database, and
    returns the list of all the contacts matching with the query string.

    for searching particularly email, the query string must have the '@' symbol in
    it's string, it then matches with only the 'email' field of the datafields in database,
    otherwise matches with the 'name' field.

    """

    @jwt_required
    def get(self, query):
        username = get_jwt_identity()
        all_contacts = []
        try:
            new_query = ".*{}.*".format(query)                                                                                           # using regular expression to find the matching charachters in query
            print(new_query)
            if('@' in query):
                contacts = db.contacts.find({'owner' : username, 'email': { "$regex": new_query }}).limit(10)                           # limiting values upto 10 max contacts in one API request
            else:
                print('query is ',query )
                contacts = db.contacts.find({'owner' : username, 'name': { "$regex": new_query }}).limit(10)                            # limiting values upto 10 max contacts in one API request
            for i in contacts:
                all_contacts.append(i)
            return all_contacts

        except Exception as e:
            print(e)
            return Response("{'message': 'some internal server error occured'}", status=500, mimetype='application/json')


class update_contact(Resource):

    """
    This is the update method, used for updating exsisting contacts for particular logined user.
    Only logined users can able to update their exsistig contacts.

    """

    @jwt_required
    def put(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('old_contact_email', help = 'This field cannot be blank', required = True)
        parser.add_argument('new_contact_email', help = 'This field can be blank', required = False)
        parser.add_argument('name', help = 'This field can be blank', required = False)
        parser.add_argument('number', help = 'This field can be blank', required = False)
        data = parser.parse_args()
        query = {'email': data['old_contact_email'], 'owner': username}

        # checks if the contacts with particular uinqe email id exist or not:-
        contact = db.contacts.find_one(query)
        if contact == None:
            msg = "{'message': 'contact with email {" + str(data['old_contact_email']) + "} doesn\'t exist'}"
            return Response(msg, status=404, mimetype='application/json')

        # to check if the new email aready exsists in the contact-book of user:-
        new_emailcontact = db.contacts.find_one({'email': data['new_contact_email'], 'owner': username})
        if new_emailcontact != None:
            msg = "{'message': 'contact with email {} already exist'}".format(data['new_contact_email'])
            return Response(msg, status=404, mimetype='application/json')
        # handling else condition
        updated_values = {}
        if(data['name']):
            updated_values['name'] = data['name']
        if(data['number']):
            updated_values['number'] = data['number']
        if(data['new_contact_email']):
            updated_values['email'] = data['new_contact_email']

        query_update = { "$set": updated_values }

        # handling else condition
        try:
            db.contacts.update_one(query, query_update)
            return Response("{'message': 'contact updated successfully'}", status=200, mimetype='application/json')
        except Exception as e:
            print('error is', e)
            print("contact not updated due to some server error")
            return Response("{'message': 'some internal server error occured while updating'}", status=500, mimetype='application/json')


class delete_contact(Resource):

    """
    This method can be used to delete a particular contacts in contact-book for paticular user which is currently logined,
    here the logined user is verified by it's unique specific token given at time of logging in after registration.

    """

    @jwt_required
    def delete(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('email', help = 'This field cannot be blank', required = True)
        data = parser.parse_args()
        query = {'email': data['email'], 'owner': username}

        # checks if the contacts with particular uinqe email id exist or not:-
        contact = db.contacts.find_one(query)
        if contact == None:
            return Response("{'message': 'contact doesn\'t exist'}", status=404, mimetype='application/json')

        # handling else condition
        try:
            db.contacts.delete_one(query)
            return Response("{'message': 'contact deleted successfully'}", status=200, mimetype='application/json')
        except Exception as e:
            print('error is', e)
            print("contact not delted due to some server error")
            return Response("{'message': 'some internal server error occured while deleting'}", status=500, mimetype='application/json')
