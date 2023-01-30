import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
DATABASE_URI = 'postgres://mgrhdzaaxfrqvk:9fe43ec6f2cd2e3222ca3afa875059e4008916205b9e71e002b8fc558572d2fd@ec2-3-229-252-6.compute-1.amazonaws.com:5432/dc5jm3ce22aapv'
SQLALCHEMY_TRACK_MODIFICATIONS = False
