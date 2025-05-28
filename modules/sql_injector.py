from flask import Blueprint, request, jsonify
import subprocess # To run external commands like sqlmap
import os # For accessing environment variables

# Create a Blueprint for SQLi related routes
sqli_bp = Blueprint('sqli', __name__)

@sqli_bp.route('/scan', methods=['POST'])
def run_sqli_scan():
    """
    Executes a sqlmap scan against a target URL.
    """
    target_url = request.json.get('url')
    # You might also get other sqlmap options from the user, e.g., data, headers, level, risk
    # For simplicity, we'll use a basic scan.
    data = request.json.get('data', '') # POST data, if any
    method = request.json.get('method', 'GET').upper()

    if not target_url:
        return jsonify({"error": "Target URL is required"}), 400

    # Basic URL validation (very basic, use a proper URL validation library in production)
    if not target_url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL format. Must start with http:// or https://"}), 400

    # Construct the sqlmap command
    # WARNING: Directly executing user-provided input in subprocess can be extremely dangerous.
    # sqlmap is designed for exploitation. Ensure explicit user consent and legal authorization.
    # In a real tool, you would have strict controls and sanitization.
    command = ['sqlmap', '-u', target_url, '--batch', '--random-agent']
    if method == 'POST' and data:
        command.extend(['--data', data])

    # Add a dummy API key for the LLM call, as per instructions.
    # In a real app, this would be passed securely or fetched from env.
    api_key = os.getenv("GEMINI_API_KEY", "")

    try:
        # Execute sqlmap command
        # capture_output=True captures stdout and stderr
        # text=True decodes output as text
        # check=True raises CalledProcessError for non-zero exit codes
        # timeout=300 sets a timeout for the scan
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=300)
        scan_output = result.stdout
        error_output = result.stderr

        if error_output:
            print(f"sqlmap stderr: {error_output}") # Log errors

        # Here, you would parse the sqlmap output to identify vulnerabilities.
        # AI could then interpret these findings and suggest remediation.
        vulnerabilities_found = parse_sqlmap_output(scan_output)

        # Example of how AI could be used to summarize sqlmap findings (conceptual)
        # This would involve sending scan_output to an LLM.
        # For this example, we'll just return the raw output.
        ai_summary = "SQLmap scan completed. Analyzing findings with AI..."
        # Example LLM call (conceptual, needs actual implementation)
        # prompt = f"Summarize the following sqlmap output for SQL injection vulnerabilities and suggest remediation:\n{scan_output}"
        # ai_summary = call_gemini_api(prompt, api_key) # This function needs to be defined elsewhere

        return jsonify({
            "target_url": target_url,
            "raw_output": scan_output,
            "vulnerabilities": vulnerabilities_found,
            "ai_summary": ai_summary,
            "message": "sqlmap scan initiated. Check raw_output for details."
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "sqlmap scan failed",
            "details": e.stderr,
            "command": ' '.join(command)
        }), 500
    except FileNotFoundError:
        return jsonify({"error": "sqlmap command not found. Is sqlmap installed and in your PATH?"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "sqlmap scan timed out."}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def parse_sqlmap_output(output):
    """
    Parses the raw sqlmap output to extract detected vulnerabilities.
    This is a simplified example. A robust parser would use regex or look for specific keywords.
    """
    vulnerabilities = []
    if "SQL injection vulnerability found" in output:
        vulnerabilities.append("SQL Injection")
    if "Parameter" in output and "is vulnerable" in output:
        # Extract vulnerable parameters (simplified)
        for line in output.splitlines():
            if "Parameter" in line and "is vulnerable" in line:
                param_start = line.find("Parameter '") + len("Parameter '")
                param_end = line.find("' is vulnerable")
                if param_start != -1 and param_end != -1 and param_end > param_start:
                    vulnerable_param = line[param_start:param_end]
                    vulnerabilities.append(f"SQL Injection (Parameter: {vulnerable_param})")
                    break # Only add first found for simplicity

    # AI could be used here to further analyze and categorize the findings.
    return list(set(vulnerabilities)) # Remove duplicates

# Placeholder for a generic LLM API call function (could be in a utils.py)
# This function would need to be properly implemented with an HTTP client.
async def call_gemini_api(prompt, api_key):
    """
    Placeholder function to call the Gemini API.
    In a real Flask app, you'd use 'requests' library and handle async if needed.
    """
    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": prompt}]})
    payload = { "contents": chat_history }
    api_url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=){api_key}"

    # This part would typically be a synchronous requests.post call in Flask.
    # For demonstration, we'll just return a mock response.
    # try:
    #     response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload)
    #     response.raise_for_status() # Raise an exception for HTTP errors
    #     result = response.json()
    #     if result.get('candidates') and result['candidates'][0].get('content') and \
    #        result['candidates'][0]['content'].get('parts'):
    #         return result['candidates'][0]['content']['parts'][0]['text']
    #     else:
    #         print("Gemini API response structure unexpected:", result)
    #         return "AI analysis failed: Unexpected response."
    # except requests.exceptions.RequestException as e:
    #     print(f"Error calling Gemini API: {e}")
    #     return "AI analysis failed: Could not connect to API."
    return "AI analysis of sqlmap output: This is a placeholder summary. Actual AI would interpret the raw output to provide insights and remediation advice."
