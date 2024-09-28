#######################################################################################################################
##  WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING  ##
##                                   READ AND UNDERSTAND BEFORE MAKING ANY CHANGES                                   ##
##  This File serves SOLELY AS AN EXAMPLE. Do NOT put your secret, or token in here. Under current implementation    ##
##      this file should be copied and named 'spotify_token.sh' AND SHOULD NOT BE COMMITED, this file is an          ##
##      exception in the .gitignore.                                                                                 ##
##                                                                                                                   ##
##  You have been warned.                                                                                            ##
##                                                                                                                   ##
##       STOP AND READ, STOP AND READ STOP AND READ, STOP AND READ STOP AND READ, STOP AND READ STOP AND READ        ##
#######################################################################################################################
# Below are all of the 'required' environment variables the project requires.

export SPOTIPY_CLIENT_ID='public client id'                 # Client ID From Spotify Dev Project
export SPOTIPY_CLIENT_SECRET='super secret client id'       # Client Secret From Spotify Dev Project
export SPOTIPY_REDIRECT_URI='http://someAddress:someport'   # Redirect URI, must match one from the 'Redirect URIs'
                                                            #   section from the dev project. Can be localhost to 
                                                            #   allow spotipy to automatically refresh token without
                                                            #   user intervention.
export CLIENT_USERNAME="username1234"                       # Spotify Username
export EMAIL_TOKEN='tokeny token token'                     # SMTP Password For Gmail
