import requests
from authlib.jose import JsonWebKey, jwt

# Google OIDC JWKS endpoint (public keys for signature verification)
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

# Replace this with your actual ID token (keep it secret in real apps!)
ID_TOKEN = """eyJhbGciOiJSUzI1NiIsImtpZCI6ImI1MDljNTEzODc2OGY3Y2YyZTgyN2UwNGIyN2U3ZTRjYmM3YmI5MTkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTIyNjA3MzE0NzQ1Mzc4MzkxNTMiLCJlbWFpbCI6Imd3aW50aGVwcm9AZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJndzZjejE2ZXpkVkJENmZERnpqUWxnIiwibmFtZSI6Ikd3aW4gUHJvIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lZbkctRjlBTWxFUEtEY0JTOE8xT1RsNWpWOEdSa3JzNnRCbDRGeWVaazgwNXVGazNTPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6Ikd3aW4iLCJmYW1pbHlfbmFtZSI6IlBybyIsImlhdCI6MTc1MzU3OTEwOSwiZXhwIjoxNzUzNTgyNzA5fQ.J6yo0RSS00VH0Li7oNKXLzCojU3jQBFonIS5QwtS7cSFYw0SRhX-o5Rd1NZLs2uClyJcgq7AsM3RIdOOmsh8W6iZV76_oPZd5p38d1Dau6GTirfGrMY7klSLGXR8OP43uJ4XDikicMX7yQNpxnyB6pSXP_1a92e48eMfwMtgVkw4Gh5trdPEhs4MwOSaAbGyRiMmBAwBu2CZBZNf-QSouI0NEcSFwoQt0KJ0EjOfb-m74mSY7EXDXBYg8use7aAn8p7ORvDiCVcMJc4ZtYH7Ed8bSnnp1qxvCLxekiVZV8j0iqXf2pCY6qpXNwctdOIgcE1uuOjK98Oipfso1d_-zg"""

def get_jwks():
    response = requests.get(JWKS_URL)
    response.raise_for_status()
    return response.json()

def validate_token(id_token):
    jwks = get_jwks()
    keys = JsonWebKey.import_key_set(jwks)
    try:
        claims = jwt.decode(id_token, keys)
        claims.validate()  # validates expiration, etc.
        return claims
    except Exception as e:
        print(f"Token validation failed: {e}")
        return None

def main():
    claims = validate_token(ID_TOKEN)
    if claims:
        print("✅ Token is valid!")
        print("🔐 Extracted user info from claims:")
        print(f"- Email: {claims.get('email')}")
        print(f"- Name: {claims.get('name')}")
        print(f"- Subject ID: {claims.get('sub')}")
        print(f"- Issuer: {claims.get('iss')}")
        print(f"- Audience: {claims.get('aud')}")
        print(f"- Expiration: {claims.get('exp')}")
    else:
        print("❌ Invalid token.")

if __name__ == "__main__":
    main()
