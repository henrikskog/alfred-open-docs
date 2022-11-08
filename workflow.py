from __future__ import print_function
import json

import os.path
import sys
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

# TODO(developer) make this an environment variable set from Alfred workflow
DEFAULT_NUMBER_RESULTS = 5

def alfred_build_option(uid: Any, title: Any, arg: Any):
    """
    Build object representing a resulting option in the launcher, with format expected by Alfred
    """
    return {"uid": uid, "title": title, "arg": arg}

def google_results_transfrom(results):
    res = [alfred_build_option(result['id'], result['name'], result['id']) for result in results]
    return json.dumps({"items": res})

def get_recent_docs(creds, number_of_docs):
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(pageSize=int(number_of_docs), fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        return []

    return items

def fetch_latest_docs():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    number_of_recent = DEFAULT_NUMBER_RESULTS
    if len(sys.argv) > 1:
        number_of_recent = sys.argv[1]

    return get_recent_docs(creds, number_of_recent)


def main():

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    try:
        res = fetch_latest_docs()
        print(google_results_transfrom(res))
    except:
        print(alfred_build_option(0, "Could not connect with the Google API", ""))

if __name__ == '__main__':
    main()