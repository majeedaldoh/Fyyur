import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://doadmin:AVNS_eUobwkwcx5EWK1Fk1In@fyyur-do-user-13431804-0.b.db.ondigitalocean.com:25060/defaultdb'
SQLALCHEMY_TRACK_MODIFICATIONS = False
