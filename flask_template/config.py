import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spoilrai-secret-key'
    # Set path to the movie spoilers database
    MOVIE_DB_PATH = os.environ.get('MOVIE_DB_PATH') or '/data/chats/iq2oe/workspace/movie_spoilers_db.json' 