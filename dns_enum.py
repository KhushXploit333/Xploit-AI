from flask import Blueprint, request, jsonify
import dns.resolver # Requires 'dnspython' library

# Create a Blueprint for DNS related routes
dns_bp = Blueprint('dns', __name__)

@dns_bp.route('/lookup', methods=['POST'])
def dns_lookup():
    """
    Performs various DNS lookups for a given domain.
    """
    domain = request.json.get('domain')
    record_type = request.json.get('type', 'A') # Default to A record

    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    # Basic domain validation (use a proper library for robust validation)
    if not all(c.isalnum() or c in ".-" for c in domain):
        return jsonify({"error": "Invalid domain format"}), 400

    try:
        # Initialize DNS resolver
        resolver = dns.resolver.Resolver()
        # resolver.nameservers = ['8.8.8.8', '8.8.4.4'] # Optional: specify nameservers

        results = []
        answers = resolver.resolve(domain, record_type)

        for rdata in answers:
            results.append(str(rdata))

        return jsonify({
            "domain": domain,
            "record_type": record_type,
            "results": results,
            "message": f"DNS lookup for {record_type} records on {domain} completed."
        })
    except dns.resolver.NoAnswer:
        return jsonify({"message": f"No {record_type} records found for {domain}."}), 200
    except dns.resolver.NXDOMAIN:
        return jsonify({"error": f"Domain '{domain}' does not exist (NXDOMAIN)."}), 404
    except dns.resolver.Timeout:
        return jsonify({"error": "DNS query timed out."}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred during DNS lookup: {str(e)}"}), 500

@dns_bp.route('/reverse-lookup', methods=['POST'])
def reverse_dns_lookup():
    """
    Performs a reverse DNS lookup for a given IP address.
    """
    ip_address = request.json.get('ip')

    if not ip_address:
        return jsonify({"error": "IP address is required"}), 400

    # Basic IP address validation (use a proper library for robust validation)
    parts = ip_address.split('.')
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return jsonify({"error": "Invalid IPv4 address format"}), 400

    try:
        addr = dns.reversename.from_address(ip_address)
        answers = dns.resolver.resolve(addr, "PTR")
        hostnames = [str(rdata) for rdata in answers]

        return jsonify({
            "ip_address": ip_address,
            "hostnames": hostnames,
            "message": f"Reverse DNS lookup for {ip_address} completed."
        })
    except dns.resolver.NXDOMAIN:
        return jsonify({"message": f"No PTR record found for {ip_address}."}), 200
    except dns.resolver.Timeout:
        return jsonify({"error": "DNS query timed out."}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred during reverse DNS lookup: {str(e)}"}), 500
