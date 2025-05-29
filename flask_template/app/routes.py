from flask import Blueprint, jsonify, request, render_template
import os
import json
from app.nlp import classify_question, extract_entities
from app.spoilers import find_movie, get_spoiler_answer

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/ask', methods=['POST'])
def ask_spoiler():
    data = request.json
    if not data or 'movie' not in data or 'question' not in data:
        return jsonify({"error": "Missing movie or question"}), 400
    
    movie_title = data.get('movie', '').strip()
    question = data.get('question', '').strip()
    show_warning = data.get('showWarning', True)
    
    movie_data = find_movie(movie_title)
    if not movie_data:
        return jsonify({
            "error": "Movie not found",
            "message": f"Sorry, I don't have information about '{movie_title}'."
        }), 404
    
    # Process the question to understand what is being asked
    intent = classify_question(question)
    entities = extract_entities(question, movie_data)
    
    # Get the answer based on the intent and entities
    answer = get_spoiler_answer(movie_data, intent, entities, question)
    
    response = {
        "movie": movie_data["title"],
        "answer": answer,
        "showWarning": show_warning,
    }
    
    return jsonify(response)

@main_bp.route('/api/movies', methods=['GET'])
def get_movies():
    # Return a list of available movies in the database
    from app.spoilers import get_all_movies
    movies = get_all_movies()
    return jsonify({"movies": movies})

@main_bp.route('/health')
def health():
    return jsonify({"status": "healthy"})