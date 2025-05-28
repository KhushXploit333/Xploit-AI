from flask import Blueprint, request, jsonify
import subprocess # To run external commands like nmap

# Create a Blueprint for Nmap related routes
nmap_bp = Blueprint('nmap', __name__)

@nmap_bp.route('/scan', methods=['POST'])
def run_nmap_scan():
    """
    Executes an Nmap scan against a target host or IP address.
    """
    target = request.json.get('target')
    scan_type = request.json.get('scan_type', '-sV') # Default to service version detection

    if not target:
        return jsonify({"error": "Target IP/hostname is required"}), 400

    # Basic input validation to prevent command injection
    # For a production tool, this needs to be much more robust.
    if not all(c.isalnum() or c in ".-_" for c in target):
        return jsonify({"error": "Invalid target format"}), 400

    # Construct the Nmap command
    # WARNING: Directly executing user-provided input in subprocess can be dangerous.
    # Ensure thorough sanitization and validation in a real application.
    command = ['nmap', scan_type, target]

    try:
        # Execute Nmap command
        # capture_output=True captures stdout and stderr
        # text=True decodes output as text
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
        scan_output = result.stdout
        error_output = result.stderr

        if error_output:
            print(f"Nmap stderr: {error_output}") # Log errors

        # Here, you would parse the Nmap output to extract relevant information
        # and potentially feed it to an AI model for analysis.
        parsed_results = parse_nmap_output(scan_output)

        return jsonify({
            "target": target,
            "scan_type": scan_type,
            "raw_output": scan_output,
            "parsed_results": parsed_results,
            "message": "Nmap scan completed successfully."
        })
    except subprocess.CalledProcessError as e:
        # Nmap exited with a non-zero status (e.g., host down, syntax error)
        return jsonify({
            "error": "Nmap scan failed",
            "details": e.stderr,
            "command": ' '.join(command)
        }), 500
    except FileNotFoundError:
        return jsonify({"error": "Nmap command not found. Is Nmap installed and in your PATH?"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Nmap scan timed out."}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def parse_nmap_output(output):
    """
    Parses the raw Nmap output into a more structured format.
    This is a simplified example. A robust parser would use regex or a dedicated library.
    """
    parsed = {"open_ports": [], "host_status": "unknown"}
    lines = output.splitlines()

    for line in lines:
        if "Host is up" in line:
            parsed["host_status"] = "up"
        elif "/tcp" in line and "open" in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                port_info = {
                    "port": parts[0].split('/')[0],
                    "protocol": parts[0].split('/')[1],
                    "state": parts[1],
                    "service": parts[2]
                }
                parsed["open_ports"].append(port_info)
    return parsed
