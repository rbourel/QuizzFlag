from flask import Flask, render_template, jsonify, request, session
import random
import requests
from bs4 import BeautifulSoup
import os
import unicodedata

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_quiz_flag_session'  # Change this in production

# Load flags
FLAGS_FILE = 'flags.txt'
flags_dict = {}
capital_dict = {}

def load_flags():
    global flags_dict, capital_dict
    if not os.path.exists(FLAGS_FILE):
        return
    with open(FLAGS_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                country, path, capital = parts[0], parts[1], parts[2]
                flags_dict[country] = path
                capital_dict[country] = capital

load_flags()

def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().strip()

def get_country_info_data(country_name):
    country_name_fmt = country_name.replace(' ', '_')
    url = f"https://en.wikipedia.org/wiki/{country_name_fmt}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        infobox = soup.find('table', class_='infobox')
        info_data = {}
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    key = header.text.strip()
                    val = value.text.strip()
                    # Clean up long values or references
                    val = val.split('[')[0] 
                    if len(info_data) < 8: # Limit to top 8 facts for brevity
                         info_data[key] = val
            return info_data
        return None
    except Exception as e:
        print(f"Error scraping info: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-question')
def new_question():
    if not flags_dict:
        return jsonify({"error": "No flags loaded"}), 500

    # Get parameters from request
    req_type = request.args.get('type', 'mixed')
    difficulty = request.args.get('difficulty', '4') # '4', '8', 'input'

    if req_type not in ['flag', 'capital']:
        question_type = random.choice(['flag', 'capital'])
    else:
        question_type = req_type

    correct_country = random.choice(list(flags_dict.keys()))
    
    # Store in session for verification
    session['correct_country'] = correct_country
    session['question_type'] = question_type
    session['difficulty'] = difficulty
    
    response_data = {
        "type": question_type,
        "choices": [],
        "image": None,
        "question_text": "",
        "input_mode": (difficulty == 'input')
    }

    if difficulty != 'input':
        try:
            num_choices = int(difficulty)
        except:
            num_choices = 4
        
        # Generate choices
        other_countries = list(flags_dict.keys())
        if correct_country in other_countries:
            other_countries.remove(correct_country)
        
        # Ensure we don't ask for more choices than available
        num_choices = min(num_choices, len(other_countries) + 1)
        
        choices_countries = random.sample(other_countries, num_choices - 1) + [correct_country]
        random.shuffle(choices_countries)
        session['choices_countries'] = choices_countries # Store for index verification
    else:
        choices_countries = []
        session['choices_countries'] = []

    if question_type == 'flag':
        response_data["question_text"] = f"Which country does this flag belong to?"
        response_data["image"] = flags_dict[correct_country]
        if difficulty != 'input':
            response_data["choices"] = choices_countries
    else:
        response_data["question_text"] = f"What is the capital of {correct_country}?"
        if difficulty != 'input':
            response_data["choices"] = [capital_dict[c] for c in choices_countries]
    
    return jsonify(response_data)

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    selected_index = data.get('index')
    user_text = data.get('text')
    
    correct_country = session.get('correct_country')
    question_type = session.get('question_type')
    difficulty = session.get('difficulty')
    
    if not correct_country:
         return jsonify({"correct": False, "error": "Session expired"}), 400

    is_correct = False
    
    if difficulty == 'input':
        if not user_text:
             return jsonify({"correct": False, "error": "No input provided"}), 400
        
        normalized_user = normalize_text(user_text)
        
        if question_type == 'flag':
            # User must guess Country name
            correct_val = correct_country
        else:
            # User must guess Capital name
            correct_val = capital_dict.get(correct_country, "")
            
        normalized_correct = normalize_text(correct_val)
        
        # Check direct match
        if normalized_user == normalized_correct:
            is_correct = True
    else:
        # Multiple Choice
        choices_countries = session.get('choices_countries')
        if selected_index is None or not choices_countries:
             return jsonify({"correct": False, "error": "Invalid selection"}), 400
        
        try:
            selected_country = choices_countries[int(selected_index)]
            is_correct = (selected_country == correct_country)
        except IndexError:
            is_correct = False
    
    correct_capital = capital_dict.get(correct_country, "Unknown")
    
    return jsonify({
        "correct": is_correct,
        "correct_country": correct_country,
        "correct_capital": correct_capital
    })

@app.route('/api/country-info')
def country_info():
    country = session.get('correct_country')
    if not country:
        return jsonify({"error": "No country in context"}), 400
    
    data = get_country_info_data(country)
    return jsonify({"country": country, "info": data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)