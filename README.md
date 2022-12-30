# Airtable OAuth Example
This is an example Flask app demonstrating how to use OAuth 2.0 to authenticate with Airtable ([OAuth reference guide](https://airtable.com/developers/web/api/oauth-reference)) and access a user's data. This app uses the Authorization Code Grant flow to authenticate the user and request an access token.

## Prerequisites
* Airtable (developer) account
* Airtable OAuth integration created in the [Airtable Management page](https://airtable.com/create/oauth)
  * Client ID and Client secret
* Python 3.6+

## Setup
1. Clone this repository and cd into it
2. Create a virtual environment: python -m venv env
3. Activate the environment: source env/bin/activate
4. Install the dependencies: pip install -r requirements.txt
5. Set the CLIENT_ID and CLIENT_SECRET environment variables with the values from your Airtable OAuth integration
6. Run the app: flask run

## Usage
*Visit http://localhost:4000 in your web browser Click the "Testify!" link to initiate the OAuth flow.
*You will be redirected to Airtable to authenticate and authorize the app.
*If successful, you will be redirected back to http://localhost:4000/airtable-oauth with a code query parameter appended to the URL
The app will exchange the authorization code for an access token (eg. use it to make a request to the Airtable API to retrieve a list of tables in your base. The app will display the names of the tables in the base)

## Notes
*The redirect_uri in this example is set to http://localhost:4000/airtable-oauth. Make sure this matches the redirect_uri registered in your Airtable OAuth integration.
*The scope in this example is set to data.records:read data.records:write. This allows the app to read and write data in the user's base. You can specify different scopes depending on the permissions you want to request.
*The state parameter is used to prevent cross-site request forgery (CSRF). It is important to validate this value when handling the redirect back to the app.
*The code_verifier and code_challenge parameters are used in the [Proof Key for Code Exchange (PKCE)] flow to secure the authorization code exchange.
*The authorization code and access token are short-lived and should be exchanged for a refresh token, which can be used to obtain new access tokens without requiring the user to re-authenticate. This example does not implement the refresh token flow.
*This example does not implement the time out of the cache.
