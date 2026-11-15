"""
TERRA-X Credential Validator
Tests live connectivity and authenticates credentials in .env against:
1. Copernicus Data Space Ecosystem (CDSE) / Sentinel Hub (OAuth2 client credentials flow)
2. NASA Earthdata Login / CMR (Bearer Token & Basic Auth)
"""

import os
import sys
import json
import requests
from pathlib import Path

# Ensure .env is loaded
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from connectors.config import load_env_file

load_env_file()


def validate_cdse_credentials():
    print("\n" + "=" * 60)
    print("1. VALIDATING COPERNICUS (CDSE / SENTINEL HUB) CREDENTIALS")
    print("=" * 60)

    client_id = os.environ.get("CDSE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("CDSE_CLIENT_SECRET", "").strip()
    username = os.environ.get("CDSE_USERNAME", "").strip()
    password = os.environ.get("CDSE_PASSWORD", "").strip()

    print(f"CDSE_CLIENT_ID     : {client_id[:8]}...{client_id[-4:] if len(client_id) > 12 else ''} (Length: {len(client_id)})")
    print(f"CDSE_CLIENT_SECRET : {client_secret[:4]}...{client_secret[-4:] if len(client_secret) > 8 else ''} (Length: {len(client_secret)})")
    if username:
        print(f"CDSE_USERNAME      : {username}")
    else:
        print("CDSE_USERNAME      : (Not provided - using OAuth2 Client Credentials grant)")

    if not client_id or not client_secret:
        print("[FAIL] Missing CDSE_CLIENT_ID or CDSE_CLIENT_SECRET in .env.")
        return False

    # Endpoints to test
    # If client_id starts with 'sh-', it is a Sentinel Hub / Copernicus OAuth client
    endpoints = []
    if client_id.startswith("sh-"):
        endpoints.append(("Sentinel Hub / CDSE Services", "https://services.sentinel-hub.com/oauth/token"))
    endpoints.append(("CDSE Keycloak Realm", "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"))

    success = False
    for name, token_url in endpoints:
        print(f"\nAttempting OAuth2 Client Credentials token exchange on {name}...")
        print(f"URL: {token_url}")
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            resp = requests.post(token_url, data=payload, headers=headers, timeout=10)
            print(f"HTTP Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                access_token = data.get("access_token", "")
                expires_in = data.get("expires_in", "unknown")
                token_type = data.get("token_type", "Bearer")
                print("[SUCCESS] Successfully authenticated with CDSE / Sentinel Hub!")
                print(f"Token Type : {token_type}")
                print(f"Expires In : {expires_in} seconds (~{int(expires_in)//60 if isinstance(expires_in, int) else '?'} mins)")
                print(f"Access Token: {access_token[:15]}...{access_token[-10:]}")
                success = True
                break
            else:
                print(f"[ERROR] Response body: {resp.text}")
        except Exception as e:
            print(f"[CONNECT ERROR] {e}")

    return success


def validate_nasa_credentials():
    print("\n" + "=" * 60)
    print("2. VALIDATING NASA EARTHDATA & CMR CREDENTIALS")
    print("=" * 60)

    username = os.environ.get("EARTHDATA_USERNAME", "").strip()
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()

    print(f"EARTHDATA_USERNAME : {username}")
    print(f"EARTHDATA_TOKEN    : {token[:15]}...{token[-10:] if len(token) > 25 else ''} (Length: {len(token)})")

    if not token:
        print("[FAIL] Missing EARTHDATA_TOKEN in .env.")
        return False

    # Validate against CMR
    cmr_url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": "TERRA-X-SpaceApps-2026",
    }
    params = {"keyword": "ECOSTRESS", "page_size": 1}

    print(f"\nQuerying NASA CMR endpoint: {cmr_url} with Bearer Token...")
    try:
        resp = requests.get(cmr_url, headers=headers, params=params, timeout=10)
        print(f"HTTP Status: {resp.status_code}")
        
        if resp.status_code == 200:
            hits = resp.headers.get("CMR-Hits", "unknown")
            print("[SUCCESS] Successfully authenticated with NASA Earthdata & CMR!")
            print(f"CMR Total Hits for query: {hits}")
            return True
        else:
            print(f"[ERROR] Response body: {resp.text}")
            return False
    except Exception as e:
        print(f"[CONNECT ERROR] {e}")
        return False


if __name__ == "__main__":
    cdse_ok = validate_cdse_credentials()
    nasa_ok = validate_nasa_credentials()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"CDSE Authentication : {'[PASSED]' if cdse_ok else '[FAILED / REQUIRES NETWORK]'}")
    print(f"NASA Authentication : {'[PASSED]' if nasa_ok else '[FAILED / REQUIRES NETWORK]'}")

