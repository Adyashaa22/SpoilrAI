from flask import Flask
from config import Config
import os
import json

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    # Set the database path relative to this file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'movie_spoilers_db.json'))
    app.config['MOVIE_DB_PATH'] = DB_PATH
    
    # Create necessary directories if they don't exist
    os.makedirs(os.path.join(app.static_folder, 'css'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'js'), exist_ok=True)
    
    return app 
