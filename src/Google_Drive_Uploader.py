
# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    GOOGLE DRIVE UPLOADER                    CREATED: 2024-09-28          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# This is just an abstraction for authorization and codeflow for getting a handler setup for the Google Drive API. It 
#   does require both a client_secrets.json and a token.txt file. It then also requires a folder_id to be given. This
#   is just grabbed from the url of the folder itself, but just another hardcoded value.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import os
import logging

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Abstracted google drive api handler to upload single 'simple' (< 5MB) files. 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class DriveUploader(LogAllMethods):
    CLIENT_SECRET_JSON = "tokens/drive_client_secrets.json"
    TOKEN_FILE = "tokens/google_drive_creds.txt"
    FOLDER_ID = "16MR2FUanB13hnAGzbCx-ZZ3Pv04vqAAB" # Spotify Databases Folder
    
    drive = None

    def __init__(self, logger: logging.Logger=None) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        self.authorize()
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Goes through authorization flow for our creds. We need to manually login and give access if the creds
                 ever go missing or it's our first run through. It handles any token refresh and just sets up our 
                 'GoogleDrive' object for later use.
    INPUT: NA
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def authorize(self) -> None:
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(client_config_file=self.CLIENT_SECRET_JSON)
        gauth.LoadCredentialsFile(self.TOKEN_FILE)

        if gauth.credentials is None:
            gauth.CommandLineAuth()
            gauth.SaveCredentialsFile(self.TOKEN_FILE)
        elif gauth.access_token_expired:
            gauth.Refresh()
            gauth.SaveCredentialsFile(self.TOKEN_FILE)
        else:
            gauth.Authorize()

        self.drive = GoogleDrive(gauth)
        
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Takes a given file and uploads it to Google Drive.
    INPUT: file - The full filepath of the file we wish to upload to our Google Drive.
    OUTPUT: NA
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def upload_file(self, file: str) -> None:
        gfile = self.drive.CreateFile({'title': os.path.basename(file), 'parents': [{'id': self.FOLDER_ID}]})
        gfile.SetContentFile(file)
        gfile.Upload()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════