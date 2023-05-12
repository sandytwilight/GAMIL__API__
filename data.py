import os
import mysql.connector
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Define database connection parameters
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'admin'
}

# Define the OAuth scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Authenticate with GMail API using OAuth
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# Fetch emails from Inbox
if creds:
    service = build('gmail', 'v1', credentials=creds)

    result = service.users().messages().list(userId='me', q='is:inbox').execute()
    messages = result.get('messages')

    # Connect to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id VARCHAR(255) PRIMARY KEY,
            thread_id VARCHAR(255),
            sender VARCHAR(255),
            recipient VARCHAR(255),
            subject TEXT,
            body TEXT,
            timestamp DATETIME
        )
    """)

    # Loop through each email and store it in the database
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = msg['payload']['headers']
        email_data = {
            'id': msg['id'],
            'thread_id': msg['threadId']
        }
        for header in headers:
            if header['name'] == 'From':
                email_data['sender'] = header['value']
            elif header['name'] == 'To':
                email_data['recipient'] = header['value']
            elif header['name'] == 'Subject':
                email_data['subject'] = header['value']
            elif header['name'] == 'Date':
                print('Timestamp string:', header['value'])
                email_timestamp_format = '%a, %d %b %Y %H:%M:%S %z'
                print('Timestamp format:', email_timestamp_format)
                try:
                    email_timestamp = datetime.strptime(header['value'], email_timestamp_format)
                    email_data['timestamp'] = email_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    print('Error parsing timestamp:', header['value'])

        if 'parts' in msg['payload']:
            email_parts = msg['payload']['parts']
            for part in email_parts:
                if part['mimeType'] == 'text/plain':
                    email_data['body'] = part['body']['data']
        else:
            email_data['body'] = msg['payload']['body']['data']

        # Insert email data into the MySQL database
        query = """
            INSERT INTO emails (id, thread_id, sender, recipient, subject, body, timestamp)
            VALUES (%(id)s, %(thread_id)s, %(sender)s, %(recipient)s, %(subject)s, %(body)s,%(timestamp)s)"""