from flask import Blueprint, request, jsonify
import dns.resolver
import requests # For checking if subdomains are active
import concurrent.futures # For parallel processing

# Create a Blueprint for subdomain related routes
subdomain_bp = Blueprint('subdomain', __name__)

# A small list of common subdomains for brute-forcing (for demonstration)
# In a real tool, you'd use a much larger wordlist.
COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "blog", "dev", "test", "admin", "api", "webmail",
    "portal", "cpanel", "autodiscover", "vpn", "docs", "app", "cdn", "shop"
]

@subdomain_bp.route('/find', methods=['POST'])
def find_subdomains():
    """
    Attempts to find subdomains for a given domain using brute-force and DNS lookups.
    """
    domain = request.json.get('domain')
    check_active = request.json.get('check_active', False) # Whether to check if subdomains are live

    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    # Basic domain validation
    if not all(c.isalnum() or c in ".-" for c in domain):
        return jsonify({"error": "Invalid domain format"}), 400

    found_subdomains = []
    resolver = dns.resolver.Resolver()
    # resolver.nameservers = ['8.8.8.8', '8.8.4.4'] # Optional: specify nameservers

    # Brute-force approach
    for sub in COMMON_SUBDOMAINS:
        full_domain = f"{sub}.{domain}"
        try:
            answers = resolver.resolve(full_domain, 'A')
            for rdata in answers:
                found_subdomains.append({
                    "subdomain": full_domain,
                    "ip_address": str(rdata),
                    "status": "DNS Resolved"
                })
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            # Subdomain not found or timed out
            pass
        except Exception as e:
            print(f"Error resolving {full_domain}: {e}")

    # Optionally check if resolved subdomains are active (HTTP/HTTPS)
    if check_active and found_subdomains:
        active_subdomains = []
        # Use ThreadPoolExecutor for concurrent HTTP requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_sub = {executor.submit(check_subdomain_active, sub['subdomain']): sub for sub in found_subdomains}
            for future in concurrent.futures.as_completed(future_to_sub):
                sub = future_to_sub[future]
                try:
                    is_active = future.result()
                    if is_active:
                        sub["status"] = "Active (HTTP/S)"
                    else:
                        sub["status"] = "DNS Resolved (HTTP/S Check Failed)"
                    active_subdomains.append(sub)
                except Exception as exc:
                    print(f'{sub["subdomain"]} generated an exception: {exc}')
                    sub["status"] = f"DNS Resolved (Error checking HTTP/S: {exc})"
                    active_subdomains.append(sub)
        found_subdomains = active_subdomains

    return jsonify({
        "domain": domain,
        "found_subdomains": found_subdomains,
        "message": f"Subdomain enumeration for {domain} completed."
    })

def check_subdomain_active(subdomain):
    """
    Checks if a subdomain is active by attempting to connect via HTTP/HTTPS.
    """
    try:
        # Try HTTPS first
        requests.head(f"https://{subdomain}", timeout=5, allow_redirects=True, verify=False) # verify=False for self-signed certs in pentesting
        return True
    except requests.exceptions.RequestException:
        try:
            # Then try HTTP
            requests.head(f"http://{subdomain}", timeout=5, allow_redirects=True)
            return True
        except requests.exceptions.RequestException:
            return False
