import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://canltn:7wxrtYXlU2vG@ep-black-art-863315.us-east-2.aws.neon.tech/fyyur?sslmode=require&options=project%3Dtiny-rain-632318'
