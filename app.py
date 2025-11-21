from flask import Flask, jsonify, render_template, request
import sqlite3
import os
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
import string



# Load environment variables from .env file
load_dotenv()

# Flask app initialization

app = Flask(__name__)


# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# SQLite connection function
def get_db_connection():
    conn = sqlite3.connect('personal_info.db')
    conn.row_factory = sqlite3.Row
    return conn

  

# API Functions
def get_weather(location):
    if not location:
        return "Please provide a valid location."
    
    print(f"Fetching weather for: {location}")  # Debugging line
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temp = data["main"].get("temp", "N/A")
        weather_desc = data["weather"][0].get("description", "N/A")
        return f"The weather in {location} is {weather_desc} with a temperature of {temp}°C."
    elif response.status_code == 429:
        return "API rate limit exceeded. Please try again later."
    elif response.status_code == 404:
        return "Location not found. Please check the location name."
    else:
        return "Sorry, I couldn't fetch the weather information."


def get_news():
    url = f"https://api.currentsapi.services/v1/latest-news?apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("news", [])[:5]  # Fetch top 5 articles
        news_list = [f"- {article['title']}" for article in articles]
        return "Here are the top news headlines:\n" + "\n".join(news_list)
    return "Sorry, I couldn't fetch the news."

def search_with_serpapi(query):
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "organic_results" in results:
        top_results = results["organic_results"][:3]  # Get the top 3 results
        result_str = "Here are the top search results:\n"
        for idx, result in enumerate(top_results, start=1):
            result_str += f"{idx}. {result['title']} - {result['link']}\n"
        return result_str
    return "Sorry, I couldn't find any relevant search results."



# Route to fetch personal information from the database
@app.route('/personal_info')
def personal_info():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personal_info")
    info = cursor.fetchall()
    conn.close()

    info_dict = {row['key']: row['value'] for row in info}
    return jsonify(info_dict)



# Route to update personal information (learning new data)
@app.route('/update_personal_info', methods=['POST'])
def update_personal_info():
    data = request.json
    key = data['key']
    value = data['value']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO personal_info (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Personal information updated successfully!"})

# Route for SerpAPI search
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        search_results = search_with_serpapi(query)
        return jsonify({"search_results": search_results})
    return jsonify({"error": "No query provided!"})

# Store user state (whether location is needed)
user_states = {}

# Route for the chatbot to ask if it should learn new data
# Route for the chatbot to ask if it should learn new data
# Route for the chatbot to ask if it should learn new data
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input', '').strip().lower()

    if not user_input:
        return jsonify({"response": "I couldn't understand your message."})

    user_id = request.json.get('user_id', 'default')  # Identify the user session

    # Check if the user state exists, if not, initialize it
    if user_id not in user_states:
        user_states[user_id] = {"awaiting_location": False}

    # If we are awaiting location input for weather, process that
    if user_states[user_id]["awaiting_location"]:
        # Only process location input if it's for weather
        user_states[user_id]["awaiting_location"] = False  # Reset the state after receiving location
        return jsonify({"response": get_weather(user_input)})

    # Remove punctuation to make input cleaner for comparison
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))

    # Check if the question relates to personal info or external API requests
    if is_personal_question(user_input):
        return jsonify({"response": handle_personal_questions(user_input)})

    # Handle weather request
    elif 'weather' in user_input:
        # Ask for location if not provided
        user_states[user_id]["awaiting_location"] = True
        return jsonify({"response": "Please provide a location for the weather."})


   

    # Handle news request
    elif 'news' in user_input:
        # Don't ask for location, just fetch the news
        return jsonify({"response": get_news()})

    # Handle search request
    elif 'search' in user_input:
        query = user_input.split("search")[-1].strip()  # Extract search query from user input
        return jsonify({"response": search_with_serpapi(query)})
    
 

    # If the query doesn't match, ask the user if the system should learn it
    return jsonify({"response": "I don't know the answer to that. Should I learn this? Please respond with 'yes' or 'no'."})




# Helper function to identify personal questions
def is_personal_question(user_input):
    personal_triggers = ['name', 'age', 'who', 'what', 'your', 'about']
    return any(trigger in user_input for trigger in personal_triggers)

# Handle personal information queries
def handle_personal_questions(user_input):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM personal_info")
    results = cursor.fetchall()
    conn.close()

    # Check if the input matches any stored key
    for row in results:
        if row["key"].lower() in user_input:
            return f"Your {row['key']} is {row['value']}."
    
    # If no match found, prompt to learn new data
    return "I don't know the answer to that. Should I learn this? Please respond with 'yes' or 'no'."


# Route to handle learning new data (update personal info)
# Route to handle learning new data (update personal info)
@app.route('/learn', methods=['POST'])
def learn():
    user_input = request.json.get('user_input', '').strip()

    if ":" not in user_input:
        return jsonify({"error": "Please provide input in 'key: value' format."})

    key, value = map(str.strip, user_input.split(":", 1))

    # Remove any unwanted characters like quotes or extra spaces
    key = key.strip().lower()
    value = value.strip()

    # Insert or replace the value in the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT OR REPLACE INTO personal_info (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        return jsonify({"message": f"I have learned: {key} = {value}"})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})
    finally:
        conn.close()



# Frontend Route (render template)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
