# File: main.py
# This is the primary entry point for running the Xploit AI Flask application.
# It initializes the Flask app from app.py and runs it.

import os
from app import create_app

# ASCII art for the Xploit AI launch screen
# You can customize this skull design!
SKULL_ART = r"""
██╗  ██╗██╗  ██╗██╗   ██╗██╗  ██╗███████╗██╗   ██╗██╗     ██╗██████╗ ██╗
██║  ██║██║  ██║██║   ██║██║  ██║██╔════╝██║   ██║██║     ██║██╔══██╗██║
███████║███████║██║   ██║███████║█████╗  ██║   ██║██║     ██║██████╔╝██║
██╔══██║██╔══██║██║   ██║██╔══██║██╔══╝  ██║   ██║██║     ██║██╔══██╗╚═╝
██║  ██║██║  ██║╚██████╔╝██║  ██║███████╗╚██████╔╝███████╗██║██║  ██║██╗
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚═╝

    💀 Xploit AI: AI-Powered Web Pentest Assistant 💀
"""

def main():
    """
    Main function to initialize and run the Flask application.
    Prints a launch screen and starts the development server.
    """
    print(SKULL_ART)
    print("\nStarting Xploit AI server...")

    # Create the Flask application instance
    app = create_app()

    # Run the Flask development server
    # In a production environment, you would use a WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
