import os
from dotenv import load_dotenv
load_dotenv()
from Contacts_project import app
from waitress import serve
serve(app, host="0.0.0.0", port=8080)
""" uncomment this below line, and comment out the above line to use this project in debug/development mode """
# app.run(debug=True, host="0.0.0.0")
