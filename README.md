***
# Spotify-2.0

## Project Description
A collection of features and improvements to Spotify using their web API. A full list of features can be found in the header of `Spotify_Features.py`.

More in-depth design and implementation methodology can be found in the headers of the source code, specifically in `Implementations.py`, `Spotify_Features.py`, and `General_Spotify_Helpers.py`. Below is a basic overview of the code structure, broken down into three "levels" to help organize functionality.

### Utilities - How Is This Happening
This is the lowest level of the repository, most notably GSH, `General_Spotify_Helpers.py`. It handles direct interactions with Spotify using the "spotipy" Python library. These utilities do not provide any inherent "features" or trigger events. Instead, they serve as abstractions that allow our features to focus on their unique aspects without worrying about 'how' to get data. Examples include creating a playlist, adding tracks to a playlist, finding a track's artists, or retrieving all of an artist's albums. This level is purely about interfacing with Spotify to perform functionality or return the requested data.

### Features - What Is Happening
Features take the functionality of 'Utilities' and turn them into fully realized features. For example, creating a playlist with every track from an artist. A feature can use the utilities to grab all tracks from an artist, create a playlist, and then add the tracks to it. Features should remain abstract. In the example above, we don't hardcode which artist we're creating the playlist for; we only handle the logic of creating a playlist given an artist. We don’t define 'When' this should happen, just 'What' happens given the parameters.

To better provide 'Implementations' access to all our capabilities, features are wrapped into `Spotify_Features.py`. This allows individual features to be self-contained in their own classes and files, while `Spotify_Features.py` manages these features.

### Implementations - When Is This Happening
Implementations define how users interact with our features and capabilities. This is where functionality like backing up the Spotify library every night at 1 AM is defined. At 1 AM, an implementation triggers a specific feature that leverages various utilities. We define 'When' specific features should be triggered. Currently, this functionality is run through `Implementations.py` and called every minute using cron.
___
# Library and Listening Management
A significant portion of the project's features and structure reflects how I listen to and organize music. Of course, this can be tailored to your personal style but below details the overall methodology behind my music organization, which drives much of the code.

## Artist Playlists
When I listen to an artist, I go through their entire discography and listen multiple times, curating a list of what I believe are their best tracks. These tracks are collected into a playlist following this naming convention:
```
__<Artist Name>
```
That's two underscores followed by the artist name as it appears on Spotify, including any prepended "The," spaces, or other characters. For example, `__The All-American Rejects`.

The only artists I follow on Spotify are those for whom I've curated a playlist after listening to their entire discography. When new tracks from that artist are released, I curate and add them to their respective playlist.

Artists that I am still working through are not followed until the process is complete, and their tracks are not added to the "Years" or "Master" collections until after the final curation.

## Years Playlists
Each calendar year gets a new playlist, simply named with the year (e.g., '2024'). This collection includes newly discovered tracks from artist investigations, as well as new releases from previously curated artists.

## Master Playlist
This is my master collection. It contains every song from every artist investigation, which in turn means every track from all "Years" playlists.

## Exceptions
I've recently started exploring various soundtracks. Normally, I go through an entire artist's discography before adding tracks to the "Years" or "Master" collections. However, for soundtracks, I use a "Soundtracks" playlist. This playlist is an exception, as we still meticulously curate what gets added, but we do not need to follow the contributing artists.

## Organization
The main playlists described above form what I call 'collections.' The `__` collection contains every artist playlist in my library, while the "Years" collection includes every year playlist (starting from 2017). Adding all the "Years" playlists together should produce the exact same track list as the "Master" playlist. The same is true for the `__` collection, except that the "Soundtracks" playlist is added, as its tracks don't have associated artists but are present in the "Years" and "Master" collections.

___
# Disclaimer
This project can and will alter your Spotify library. This includes, but is not limited to, creating new playlists, adding tracks to playlists, removing tracks from playlists, and altering playback. I strongly recommend reviewing the code before allowing it to modify your library. This is a passion project of mine, and I take zero responsibility for any changes, additions, or deletions made to your personal Spotify library. I have developed my own safeguards and secondary backups so that I can restore my library if it is altered (thankfully, this has never happened).

**You Have Been Warned**

___
# Setup

## Environment Setup
Wherever you clone this project (recommend `/home/$USER/projects`), you MUST update the `cron.jobs` `PROJ_PATH`.

```bash
cd Spotify-2.0/
python -m venv .venv 
source .venv/bin/activate
pip install -r startup/requirements.txt
```

## Tokens

### Setting up Spotify Developer Account and Project

1. Create a Spotify Developer Account:
    - https://developer.spotify.com/dashboard 
    - Note: You need a premium account.
2. Once logged in, head to your 'Dashboard' and click 'Create app'.
    - The 'App name' and 'App description' do not matter.
3. Add the following 'Redirect URIs':
    - http://localhost:9090
    - http://google.com/callback/
4. In your `spotify_token.sh`, set `SPOTIPY_REDIRECT_URI` to the localhost redirect URI.
5. Copy the 'Client ID' from your project into `SPOTIPY_CLIENT_ID`.
6. Click 'View client secret' and copy it into `SPOTIPY_CLIENT_SECRET`.

### Setting up GMail API
These steps are necessary only if you want to use the email functionality.

1. Create a new email account specifically for this project (recommended in case the credentials are compromised).
2. Enable the GMail API:
    - https://console.cloud.google.com/apis/library/gmail.googleapis.com
3. Generate an App Password:
    - Turn on 2-Step Verification
    - Follow the steps at https://myaccount.google.com/apppasswords.
4. Set `GMAIL_USERNAME` with the sending email address and `GMAIL_TOKEN` with the app password.
5. Set `GMAIL_RECIPIENT` to the email where you wish to receive notifications.

### Setting up Google Drive API
These steps are necessary only if you want to use Google Drive upload functionality.

1. Enable the Google Drive API:
    - https://console.cloud.google.com/apis/api/drive.googleapis.com
2. Generate credentials:
    - Under the 'Credentials' tab, click 'Create Credentials'.
    - Select 'OAuth client ID' and 'Desktop App'.
    - Download the JSON file, rename it to `drive_client_secrets.json`, and place it in the `tokens/` directory.
3. Add a test user:
    - Under 'Test users', click 'Add Users' and enter your project's email address.
4. Designate a Google Drive upload folder:
    - Create a new folder in Google Drive.
    - Copy the folder ID from the URL and set it in `FOLDER_ID` in `Google_Drive_Uploader.py`.
5. First run:
    - Follow the prompts and authorize access to your Google Drive by copying the URL into your browser. 
    - Paste the authorization code back into the command line.

Congrats. Now you can switch over to triggering events through Cron and `Implementations.py` Have fun and enjoy!
