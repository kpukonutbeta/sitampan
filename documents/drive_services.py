import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Builds and returns the Google Drive API service using OAuth 2.0."""
    creds = None
    token_path = os.path.join(settings.BASE_DIR, settings.GOOGLE_DRIVE_TOKEN_FILE)
    creds_path = os.path.join(settings.BASE_DIR, settings.GOOGLE_DRIVE_CREDENTIALS_FILE)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"Credentials file not found at {creds_path}. Please download it from Google Cloud Console.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            # This will open a browser window for authorization
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service

def get_or_create_drive_folder(category):
    """
    Ensures a folder exists for the category.
    Returns the drive_folder_id.
    """
    if category.drive_folder_id:
        return category.drive_folder_id

    service = get_drive_service()
    if not service:
        # Cannot connect to drive, just return None
        return None

    # Determine parent folder ID
    parent_id = settings.GOOGLE_DRIVE_ROOT_FOLDER_ID
    if category.parent:
        if not category.parent.drive_folder_id:
            # Recursively create parent folder
            get_or_create_drive_folder(category.parent)
        parent_id = category.parent.drive_folder_id
        # Reload parent to get the ID if it was just saved
        category.parent.refresh_from_db()
        parent_id = category.parent.drive_folder_id

    if not parent_id:
        return None

    # Check if a folder with this name already exists in the parent
    query = f"name='{category.name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query, 
        spaces='drive', 
        fields='nextPageToken, files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    items = results.get('files', [])

    if items:
        # Folder already exists, just use the first match
        folder_id = items[0]['id']
    else:
        # Create a new folder
        file_metadata = {
            'name': category.name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = service.files().create(
            body=file_metadata, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        folder_id = folder.get('id')

    # Save the new ID to the category model directly to avoid triggering signals infinitely
    category.drive_folder_id = folder_id
    category.save(update_fields=['drive_folder_id'])
    return folder_id

def upload_document_to_drive(document):
    """
    Uploads the document to its category's Google Drive folder.
    Updates the document with the drive_file_id.
    """
    service = get_drive_service()
    if not service or not document.file or not document.category:
        return None

    folder_id = document.category.drive_folder_id
    if not folder_id: # Might need to ensure the folder exists first
        folder_id = get_or_create_drive_folder(document.category)
    
    if not folder_id:
        return None

    file_metadata = {
        'name': document.title,
        'parents': [folder_id]
    }
    
    file_path = document.file.path
    media = MediaFileUpload(file_path, resumable=True)
    
    file = service.files().create(
        body=file_metadata, 
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()
    
    file_id = file.get('id')
    document.drive_file_id = file_id
    document.save(update_fields=['drive_file_id'])
    return file_id

def delete_drive_folder(folder_id):
    """
    Moves a folder to the trash in Google Drive.
    """
    if not folder_id:
        return False
        
    service = get_drive_service()
    if not service:
        return False
        
    try:
        # Move to trash rather than permanent deletion
        service.files().update(
            fileId=folder_id,
            body={'trashed': True},
            supportsAllDrives=True
        ).execute()
        return True
    except Exception as e:
        print(f"Error trashing Drive folder {folder_id}: {e}")
        return False

def rename_drive_file(file_id, new_name):
    """
    Renames a file in Google Drive.
    """
    if not file_id or not new_name:
        return False
        
    service = get_drive_service()
    if not service:
        return False
        
    try:
        file_metadata = {'name': new_name}
        service.files().update(
            fileId=file_id,
            body=file_metadata,
            supportsAllDrives=True
        ).execute()
        return True
    except Exception as e:
        print(f"Error renaming Drive file {file_id}: {e}")
        return False
