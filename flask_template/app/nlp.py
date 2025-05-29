import re
import string

# Question types/intents we can recognize
QUESTION_TYPES = [
    "character_fate",   # Questions about what happens to characters
    "key_scene",        # Questions about specific scenes
    "ending",           # Questions about the ending
    "general_question"  # Fallback for other questions
]

# Keywords that help identify the intent of the question
INTENT_KEYWORDS = {
    "character_fate": ["die", "dies", "death", "fate", "happen", "happens", "alive", "survive", "kill"],
    "key_scene": ["scene", "part", "moment", "sequence", "event", "happen"],
    "ending": ["end", "ending", "final", "finale", "conclude"]
}

def classify_question(question):
    """
    Determine the type of question being asked based on keywords
    """
    question_lower = question.lower()
    
    # Check for ending questions first (they're most specific)
    if any(kw in question_lower for kw in INTENT_KEYWORDS["ending"]):
        if any(phrase in question_lower for phrase in ["how does it end", "what happens at the end", "how does the movie end", "how does the show end"]):
            return "ending"
    
    # Check for character fate questions
    if any(kw in question_lower for kw in INTENT_KEYWORDS["character_fate"]):
        # Look for patterns like "does X die" or "what happens to X"
        if re.search(r"(does|did|do)\s+\w+\s+(die|survive|live|get killed)", question_lower) or \
           re.search(r"what\s+happens\s+to\s+\w+", question_lower) or \
           re.search(r"(fate|death)\s+of\s+\w+", question_lower):
            return "character_fate"
    
    # Check for key scene questions
    if any(kw in question_lower for kw in INTENT_KEYWORDS["key_scene"]):
        # Look for patterns like "what happens in X scene" or "the X scene"
        if re.search(r"(what\s+happens|tell me about)\s+(in|during|at)\s+\w+", question_lower) or \
           re.search(r"the\s+\w+\s+(scene|part|moment|sequence)", question_lower):
            return "key_scene"
    
    # Default to general question
    return "general_question"

def extract_entities(question, movie_data):
    """
    Extract relevant entities from the question (character names, scene references, etc.)
    """
    question_lower = question.lower()
    entities = {}
    
    # Extract character references
    if "characters" in movie_data:
        for character_name in movie_data["characters"]:
            char_lower = character_name.lower()
            # Check if character name appears in question
            if char_lower in question_lower:
                entities["character"] = character_name
                break
            
            # Check for first names
            first_name = char_lower.split()[0]
            if len(first_name) > 2 and first_name in question_lower.split():
                entities["character"] = character_name
                break
    
    # Extract scene references
    if "key_scenes" in movie_data:
        for scene_key in movie_data["key_scenes"]:
            scene_name = scene_key.replace("_", " ")
            if scene_name in question_lower:
                entities["scene"] = scene_name
                break
            
            # Look for keywords in scene descriptions that might match question
            scene_desc = movie_data["key_scenes"][scene_key].lower()
            # Extract significant nouns from the description
            scene_keywords = [word for word in re.findall(r'\b[a-zA-Z]{4,}\b', scene_desc) 
                             if word not in set(string.punctuation) and word not in 
                             {"what", "when", "where", "which", "this", "that", "there", "these", "those", "with", "from"}]
            
            # Check if these keywords appear in the question
            for keyword in scene_keywords:
                if keyword in question_lower and len(keyword) > 3:
                    entities["scene"] = keyword
                    break
    
    # Try to extract any character name for "does X die" questions
    if "character" not in entities:
        does_die_match = re.search(r"does\s+([^?]+)\s+die", question_lower)
        if does_die_match:
            potential_character = does_die_match.group(1).strip()
            # See if this matches or partially matches any character
            for character_name in movie_data["characters"]:
                char_lower = character_name.lower()
                if potential_character in char_lower or char_lower in potential_character:
                    entities["character"] = character_name
                    break
    
    return entities