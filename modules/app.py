# File: app.py
# This file handles the creation and configuration of the Flask application.
# It registers blueprints for different modules and sets up basic configurations.

from flask import Flask, render_template

# Import blueprints from different modules
from index import index_bp
from modules.cvss import cvss_bp
from modules.nmap_scanner import nmap_bp
from modules.sql_injector import sqli_bp
from modules.dns_enum import dns_bp
from modules.subdomain_finder import subdomain_bp
from modules.owasp_analyzer import owasp_bp

def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)

    # --- Configuration ---
    # You can add more configurations here, e.g., secret keys, database URIs.
    app.config['SECRET_KEY'] = 'your_super_secret_key_here' # IMPORTANT: Change this in production!
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Example for a database

    # --- Register Blueprints ---
    # Blueprints help organize your application into smaller, reusable components.
    app.register_blueprint(index_bp)
    app.register_blueprint(cvss_bp, url_prefix='/cvss')
    app.register_blueprint(nmap_bp, url_prefix='/nmap')
    app.register_blueprint(sqli_bp, url_prefix='/sqli')
    app.register_blueprint(dns_bp, url_prefix='/dns')
    app.register_blueprint(subdomain_bp, url_prefix='/subdomain')
    app.register_blueprint(owasp_bp, url_prefix='/owasp')

    # --- Error Handlers (Optional) ---
    @app.errorhandler(404)
    def page_not_found(e):
        """Custom 404 error page."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """Custom 500 error page."""
        return render_template('500.html'), 500

    return app

# File: index.py
# This file defines the main routes for the Xploit AI web interface,
# including the homepage and the chat interface.

from flask import Blueprint, render_template, request, jsonify
import json # For parsing API responses
import os # For accessing environment variables

# Create a Blueprint for the index/main routes
index_bp = Blueprint('index', __name__)

# Placeholder for chat history
chat_history = []

@index_bp.route('/')
def home():
    """
    Renders the main homepage of the Xploit AI application.
    This will serve as the entry point to the chat interface.
    """
    return render_template('index.html')

@index_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat interactions with the AI assistant.
    Receives user messages, calls the AI model, and returns AI responses.
    """
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Add user message to chat history
    global chat_history
    chat_history.append({"role": "user", "parts": [{"text": user_message}]})

    # --- AI Model Integration (Placeholder) ---
    # This is where you would integrate with OpenAI, Gemini, or your custom AI/ML models.
    # For demonstration, we'll use a placeholder for Gemini-2.0-Flash API call.
    ai_response_text = "I'm still learning! How can I assist you with web pentesting today?"
    try:
        # Prepare the payload for the Gemini API call
        payload = {
            "contents": chat_history,
            "generationConfig": {
                "responseMimeType": "text/plain" # Or "application/json" if structured output is desired
            }
        }
        # Get the API key from environment variable
        # Note: In a real deployment, you'd use a more secure way to handle API keys.
        # For Canvas environment, __app_id is automatically provided.
        api_key = os.getenv("GEMINI_API_KEY", "") # Use environment variable or empty string for Canvas auto-injection

        # Construct the API URL
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        # Simulate a fetch call (this would be done via a client-side JS in real app,
        # or a server-side HTTP request library like 'requests' in Flask)
        # For this Python backend, we'll simulate the response structure.
        # In a real Flask app, you'd use:
        # import requests
        # response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
        # result = response.json()

        # Placeholder for actual API call and response parsing
        # This part needs to be implemented with a proper HTTP client in a real Flask app.
        # For now, we simulate a direct response.
        # Example of what a successful Gemini API response might look like:
        # result = {
        #     "candidates": [
        #         {
        #             "content": {
        #                 "parts": [
        #                     {"text": "Hello! I am your AI pentest assistant. How can I help?"}
        #                 ]
        #             }
        #         }
        #     ]
        # }
        # if result.get('candidates') and result['candidates'][0].get('content') and \
        #    result['candidates'][0]['content'].get('parts'):
        #     ai_response_text = result['candidates'][0]['content']['parts'][0]['text']
        # else:
        #     print("Gemini API response structure unexpected:", result)
        #     ai_response_text = "Sorry, I couldn't process that. Please try again."

        # For now, a simple mock response:
        if "hello" in user_message.lower():
            ai_response_text = "Hello! I am Xploit AI, your AI-powered web pentest assistant. What website would you like to analyze today?"
        elif "xss" in user_message.lower():
            ai_response_text = "To detect XSS, I can analyze input fields for improper sanitization and output encoding. Would you like to initiate an XSS scan?"
        elif "sqli" in user_message.lower():
            ai_response_text = "For SQL Injection, I can attempt to identify vulnerable parameters. I can also integrate with sqlmap for deeper analysis. What's your target?"
        elif "report" in user_message.lower():
            ai_response_text = "I can generate a comprehensive report of the vulnerabilities found. What kind of details would you like included?"
        else:
            ai_response_text = "I'm still learning! How can I assist you with web pentesting today?"

    except Exception as e:
        print(f"Error calling AI model: {e}")
        ai_response_text = "I'm having trouble connecting to the AI assistant right now. Please try again later."

    # Add AI response to chat history
    chat_history.append({"role": "model", "parts": [{"text": ai_response_text}]})

    return jsonify({"response": ai_response_text})

