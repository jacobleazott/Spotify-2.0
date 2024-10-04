# Spotify-2.0

## Project Description
A collection of features and improvements to Spotify through their web API.

# Disclaimer
This project can and will alter your Spotify library. This includes but is not limited to creating new playlists, 
adding tracks to playlists, removing tracks from playlists, and altering your playback. I highly encourage you to review the 
code yourself before trusting it to alter your library. This is a passion project of mine and I claim 0 responsibility for
any alterations/ addition/ or destruction to your personal Spotify library. I have developed my own safeguards and 
have secondary backups so that in case I ever break my library I can write up a script to restore it (thankfully this has 
never happened).

**You Have Been Warned**

# How To
## Environment Setup
Wherever you clone this project (recommend /home/$USER/projects) you MUST update the cron.jobs 'PROJ_PATH'
```bash
cd Spotify-2.0/
python -m venv .venv 
source .venv/bin/activate
pip install -r startup/requirements.txt
```

## Tokens
### Setting up Spotify Developer Account and Project
https://developer.spotify.com/dashboard Note: You need a premium account.

1. Once you have logged in head to your 'Dashboard' and click 'Create app'.
   - 'App name' and 'App description' do not matter.
2. 'Redirect URIs' should include both a localhost, and a generic callback.
   - For Example:
   - http://localhost:9090
   - http://google.com/callback/
3. In your spotify_token.sh your localhost redirect uri will be what you put in 'SPOTIPY_REDIRECT_URI'
4. Then you'll need to go into your new project, go into 'Settings' copy your 'Client ID' into 'SPOTIPY_CLIENT_ID'
5. Click 'View client secret' and copy this into 'SPOTIPY_CLIENT_SECRET'

### Setting up GMail API 
These steps are only necessary if you wish to setup the email functionality.
1. Recommend setting up a brand new email for this in case your creds are ever compromised.
2. Enable The GMail API
    - https://console.cloud.google.com/apis/library/gmail.googleapis.com
3. This will require setting up a Google Cloud project.
4. You will need to generate an App Password
    - Turn on 2-Step Verification
    - Follow steps on https://myaccount.google.com/apppasswords
    - App name doesn't matter, copy the password into your 'GMAIL_TOKEN'
5. Make sure to set both 'GMAIL_USERNAME' with your email with the app password that will be sending the emails.
6. Fill 'GMAIL_RECIPIENT' with the email you wish to receive these emails.

### Setting up Google Drive API
These steps are only necessary if you wish to setup google drive upload functionality.
1. Enable The Google Drive API
    - https://console.cloud.google.com/apis/api/drive.googleapis.com
2. Scroll Down and Select 'Create Credentials' under the 'Credentials' Tab
    - Select 'OAuth client ID'
    - Select 'Desktop App'
    - Name doesn't matter, click 'Download JSON'
    - Rename json file to 'drive_client_secrets.json' and place in the 'tokens/' directory.
3. Add A Test User 
    - https://console.cloud.google.com/apis/credentials/consent?authuser
    - Select your project
    - Scroll down and under 'Test users' click 'Add Users'
    - Enter your new email/ the email you are using for this project.
4. Go to your google drive for this account.
    - Create a new folder
    - Go into that folder and copy the folder-id from the url.
    - ex. https://drive.google.com/drive/u/3/folders/THIS_IS_YOUR_FOLDER_ID
    - Copy that folder id into 'FOLDER_ID' in 'Google_Drive_Uploader.py' 
4. On your first use of the drive API it will present you with a url, open it up and just follow the on screen prompts.
5. Copy the code it gives you back into the command line window.

## Setup
1. If you haven't already make sure to populate 'CLIENT_USERNAME' in the spotify_token.sh
   - This can be found under your "Account" and "Edit Profile" since it may not be your display name.
2. Uncomment your second callback uri, the one that is a non localhost. We need to login and authorize access.
3. Run 'startup/test_proj.sh' 
   - You should be greeted with a url in your console, copy that to a browser.
   - After following the on screen directions copy the url from the address bar and copy it back into the command line.
4. Now feel free to experiment through the different functions in 'Initial_Startup.py'. They give a small overview of code flow and the base functionality of the project. Each function takes subsequently more and more permissions and you will have to continue to authorize each function manually. 
5. Once you have verified it is working properly you can comment that second redirect uri. From now on spotipy will automatically use the localhost one to refresh your token and you shouldn't need to reauthenticate.

Congrats. Now you can switch over to triggering events through Cron and 'Implementations.py' Have fun and enjoy!