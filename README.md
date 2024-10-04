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
pip install -r requirements.txt
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
2. https://www.sitepoint.com/quick-tip-sending-email-via-gmail-with-python/
3. Once you have your 'app password' go ahead and put that into 'EMAIL_TOKEN' in your 'spotify_token.sh'

### Setting up Google Drive API
These steps are only necessary if you wish to setup google drive upload functionality.
1. https://www.projectpro.io/recipes/upload-files-to-google-drive-using-python
   - Specifically follow step 2. However, it may be a good idea to test that this works independently.
2. Your client credentials json file you get should be renamed 'drive_client_secrets.json' and palced in 'tokens/'

## Setup
1. If you haven't already make sure to populate 'CLIENT_USERNAME' in the spotify_token.sh
   - This can be found under your "Account" and "Edit Profile" since it may not be your display name.
2. Uncomment your second callback uri, the one that is a non localhost. We need to login and authorize access.
3. Run 'Proj.sh' 
   - You should be greeted with a url in your console, copy that to a browser.
   - After following the on screen directions copy the url from the address bar and copy it back into the command line.
4. Once you have verified it is working properly you can comment that second redirect uri. From now on spotipy will automatically use the localhost one to refresh your token and you shouldn't need to reauthenticate.