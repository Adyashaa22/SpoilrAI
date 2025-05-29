import os
import json
import re

from flask import current_app

# We'll get the DB_PATH from the app config

# Load the spoiler database
def load_spoilers_db():
    try:
        db_path = current_app.config['MOVIE_DB_PATH']
        with open(db_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading spoiler database: {e}")
        return []

# Find a movie by title (case insensitive)
def find_movie(title):
    db = load_spoilers_db()
    title_lower = title.lower()
    
    for movie in db:
        if movie['title'].lower() == title_lower:
            return movie
    
    # Try partial matching if exact match fails
    for movie in db:
        if title_lower in movie['title'].lower():
            return movie
    
    return None

# Get a list of all available movies
def get_all_movies():
    db = load_spoilers_db()
    return [{"title": movie['title'], "year": movie.get('year', 'Unknown')} for movie in db]

# Get spoiler answer based on intent and entities
def get_spoiler_answer(movie, intent, entities, original_question):
    if intent == "character_fate":
        if "character" in entities:
            character_name = entities["character"]
            # Try to find exact or close match for the character
            for char_name, char_data in movie["characters"].items():
                if character_name.lower() in char_name.lower():
                    return char_data["fate"]
            return f"I don't have information about the character '{character_name}' in {movie['title']}."
        
    elif intent == "key_scene":
        if "scene" in entities:
            scene_key = entities["scene"]
            # Try to match the scene description with available key scenes
            for scene_name, scene_desc in movie["key_scenes"].items():
                if scene_key.lower() in scene_name.lower():
                    return scene_desc
                # Check if the scene key is mentioned in the scene description
                if scene_key.lower() in scene_desc.lower():
                    return scene_desc
            return f"I don't have specific information about that scene in {movie['title']}."
        
    elif intent == "ending":
        return movie["ending"]
    
    elif intent == "general_question":
        # For general questions, try to match with character names, scenes, or just return the ending
        if "character" in entities:
            character = entities["character"]
            for char_name, char_data in movie["characters"].items():
                if character.lower() in char_name.lower():
                    # Check if question indicates interest in fate
                    if any(word in original_question.lower() for word in ["die", "dies", "death", "fate", "happen", "happens", "end"]):
                        return char_data["fate"]
                    # Otherwise return a more complete character info
                    key_moments = ", ".join(char_data["key_moments"][:3]) + "..."
                    return f"{char_name}: {char_data['fate']} Key moments include: {key_moments}"
                    
        if "does" in original_question.lower() and "die" in original_question.lower():
            # Try to extract character name from between "does" and "die"
            match = re.search(r"does\s+([^?]+)\s+die", original_question.lower())
            if match:
                character = match.group(1).strip()
                for char_name, char_data in movie["characters"].items():
                    if character in char_name.lower():
                        if "die" in char_data["fate"].lower():
                            return f"Yes, {char_name} dies. {char_data['fate']}"
                        else:
                            return f"No, {char_name} doesn't die. {char_data['fate']}"
        
    # Default response if we can't classify the question properly
    return f"I'm not sure about that specific detail in {movie['title']}. You might want to ask about a character's fate, a key scene, or the ending."