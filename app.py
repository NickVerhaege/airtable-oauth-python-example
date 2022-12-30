import base64
import os
import hashlib
import urllib.parse
import json
import requests
from flask import Flask, redirect, request

app = Flask(__name__)

# set up environment variables
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]

# if you edit the port you will need to edit the redirect_uri
# if you edit the path of this URL will you will need to edit the /airtable-oauth route to match your changes
redirect_uri = 'http://localhost:4000/airtable-oauth'
scope = "data.records:read data.records:write"
airtable_url = "https://airtable.com"

encoded_credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
authorization_header = f"Basic {encoded_credentials}"

@app.route('/')
def index():
    return '<a href="redirect-testing">Testify!</a>'

authorization_cache = {}
@app.route('/redirect-testing')
def redirect_testing():
    # prevents others from impersonating Airtable
    state = base64.urlsafe_b64encode(os.urandom(100)).decode()

    # prevents others from impersonating you
    code_verifier = base64.urlsafe_b64encode(os.urandom(96)).decode()
    code_challenge_method = 'S256'
    code_challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode().rstrip('=') #remove =
    code_challenge = code_challenge.replace('+', '-').replace('/', '_') #replace + and - with / and _ respectively

    # ideally, entries in this cache expires after ~10-15 minutes
    authorization_cache[state] = {
        # we'll use this in the redirect url route
        "code_verifier": code_verifier,
        # any other data you want to store, like the user's ID
    }

    # build the authorization URL
    authorization_url = f"{airtable_url}/oauth2/v1/authorize"
    params = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "state": state,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        # your OAuth integration register with these scopes in the management page
        "scope": scope,
    }
    authorization_url += '?' + urllib.parse.urlencode(params)

    # redirect the user and request authorization
    return redirect(authorization_url)

# route that user is redirected to after successful or failed authorization
# Note that one exemption is that if your client_id is invalid or the provided
# redirect_uri does exactly match what Airtable has stored, the user will not
# be redirected to this route, even with an error.
@app.route('/airtable-oauth')
def airtable_oauth():
    state = request.args.get('state')
    cached = authorization_cache.get(state)
    # validate request, you can include other custom checks here as well
    if cached is None:
        return 'This request was not from Airtable!'

    # clear the cache
    authorization_cache.pop(state, None)

    # Check if the redirect includes an error code.
    # Note that if your client_id and redirect_uri do not match the user will never be re-directed
    # Note also that if you did not include "state" in the request, then this redirect would also not include "state"
    error = request.args.get('error')
    if error:
        # handle error
        return f'Authorization failed with error: {error}'

    # Extract the authorization code from the query parameters
    authorization_code = request.args.get('code')

    # send a POST request to the token URL to exchange the authorization code for an access token
    token_url = f"{airtable_url}/oauth2/v1/token"
    headers = {
        #Content-Type is always required
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if client_secret:
        headers["Authorization"] = authorization_header

    data = {
        "client_id": client_id,
        "code_verifier": cached["code_verifier"],
        "redirect_uri": redirect_uri,
        "code": authorization_code,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code != 201:
        return f'Error exchanging authorization code for access token: {response.text}'

    # extract the access token and refresh token
    token_response = response.json()
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']

    # store the access token and refresh token for later use
    # ...

    return 'Authorization successful!'

if __name__ == "__main__":
    app.run(port="4000")