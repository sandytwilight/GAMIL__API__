import base64
import os
import pickle
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask, jsonify, request

# Replace with the path to your client secret file
CLIENT_SECRET_FILE = '/path/to/client_secret.json'

# Replace with the path to your credentials file (or where you want to save it)
CREDENTIALS_FILE = '/path/to/credentials.pickle'

# Replace with your desired scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.compose']

# Initialize Flask app
app = Flask(__name__)

def authenticate():
    # Check if the user's credentials exist in a pickle file
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
    else:
        # If the user's credentials don't exist, initiate the OAuth2 flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        print('Please go to this URL: {}\n'.format(authorization_url))
        authorization_code = input('Enter the authorization code: ')
        flow.fetch_token(authorization_response=authorization_code)

        # Save the user's credentials in a pickle file
        credentials = flow.credentials
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)

    # Build the Gmail API client with the user's credentials
    try:
        service = build('gmail', 'v1', credentials=credentials)
        return service
    except HttpError as error:
        print('An error occurred: %s' % error)
        return None

# Define API endpoints
@app.route('/api/custom-label/', methods=['POST'])
def get_labels():
    service = authenticate()
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return jsonify(labels)

@app.route('/rules.json/', methods=['POST'])
def get_messages():
    service = authenticate()
    query = request.args.get('q')
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return jsonify(messages)

@app.route('/rules.json/', methods=['POST'])
def get_message(message_id):
    service = authenticate()
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return jsonify(message)

@app.route('/assignment.py/', methods=['POST'])
def update_message(message_id):
    service = authenticate()
    message = service.users().messages().get(userId='me', id=message_id).execute()
    label_ids = request.json.get('labelIds', [])
    if label_ids:
        body = {'removeLabelIds': [], 'addLabelIds': label_ids}
        service.users().messages().modify(userId='me', id=message_id, body=body).execute()
    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)
