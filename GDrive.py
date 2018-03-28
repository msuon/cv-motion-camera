from __future__ import print_function
import httplib2
import os
import pprint
import sys


from oauth2client import client
from oauth2client import tools
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage

from apiclient import discovery

# Give the client ecret file path for requesting token
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "client_secret.json")
# Give the scope of access for the drive
SCOPES = "https://www.googleapis.com/auth/drive.file"
# Application Name
APPLICATION_NAME = "DRIVE API FOR PI SECURITY IMAGES"

class google_query:
    field = ""
    operator = ""
    value = ""
    def __init__(self, field, operator, value):
        self.field =field
        self.operator = operator
        self.value = value


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    # Todo: print error warning no required secret files or something like that
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")

    if not os.path.exists(credential_dir):
        os.mkdir(credential_dir)
    credential_path = os.path.join(credential_dir, "drive-python-generial.json")

    store = Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_drive_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build("drive", "v3", http=http)

def find_file(file_name, parents=None, before_date=None, after_date=None):
    # Todo: No Parent found error handling
    # Todo: No file found error handling
    # Todo: Handle more than one parent of the same name (maybe two folder same name)
    # Create Google Drive Thing
    drive_service = get_drive_service()
    query_list = []

    # Build query string
    query_list.append(google_query("name", "=", file_name))

    if before_date is not None:
        query_list.append(google_query("modifiedTime", "<=", before_date))

    if after_date is not None:
        query_list.append(google_query("modifiedTime", ">=", after_date))

    try:
        if parents is not None:
            # Find parent's id
            if parents == 'root':
                parent_id = 'root'
            else:
                parent_id = find_file(parents)[0]["id"]
            query_list.append(google_query("parents", "in", parent_id))
    except TypeError:
        print("No parent \"{}\" found".format(parents))
        return 0

    # Join the queries
    s = " and "
    query_str = s.join(["{} {} '{}'".format(x.field, x.operator, x.value) for x in query_list])
    print(query_str)
        # query_str.j
        # query_list += "and {} {} {}".format(each.field, each.operator, each.value)

    result = drive_service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name)",
        q=query_str
    ).execute()

    items = result.get('files', [])
    if not items:
        print('No folder/files of name {} found.'.format(file_name))
        return None
    else:
        return items

def add_folder(folder_name):

    drive_service = get_drive_service()

    folder_meta = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    f = drive_service.files().create(body=folder_meta,
                                    fields='id').execute()
    print("Created folder {} with ID {}".format(f.get('name'), f.get('id')))
    return f.get('id')

def add_file(local_path, remote_folder="root"):
    ''' This function adds file from local_path to a "remote_folder" in the Google Drive'''
    # Initialize drive_service
    drive_service = get_drive_service()
    # Create media payload
    media = MediaFileUpload(local_path, 'image/jpg', resumable=True)

    # Add metadata about parent folder to upload file to
    if remote_folder != "root":
        try:
            folder_id = find_file(remote_folder)[0]["id"]
        except TypeError:
            print("Could not find parent folder {}, creating a folder".format(remote_folder))
            folder_id = add_folder(remote_folder)

        file_meta = {
            'name': os.path.basename(local_path),
            'parents': [folder_id]
        }
    else:
        file_meta = {
            'name': os.path.basename(local_path)
        }

    print(file_meta)
    request = drive_service.files().create(media_body=media, body=file_meta)
    response = None

    while response is None:
       status, response = request.next_chunk()
       if status:
           print("Uploaded %d%%." % int(status.progress() * 100))
    print("Upload Complete!")


def remove_file(fileName, parentName=None):
    ''' This function deletes a file from the google drive. It does so by finding the folder name and use it'''

    drive_service = get_drive_service()
    file_id = find_file(fileName, parentName)[0]["id"]
    print("Removing file {} with id {}...".format(fileName, file_id))
    drive_service.files().delete(fileId=file_id).execute()

def list_file():
    drive_service = get_drive_service()
    results = drive_service.files().list().execute()
    pprint.pprint(results.get('files', []))
