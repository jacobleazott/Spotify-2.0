# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIPY PROXY SERVER                     CREATED: 2025-02-08          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# A proxy server for spotipy. This way we have a dedicated server that can handle all of our spotipy requests and most
#   importantly, handle token refreshing. This way we can have a consistant connection to the API.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import random
import spotipy
import threading
import time
from flask import Flask, request, jsonify

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates and manages a flask server as well as our spotipy instance. Handles token refreshing and allows 
                us to have a consistant connection to the API.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotifyServer():
    
    def __init__(self):
        self.logger = get_file_logger(f'logs/Proxy-Server.log', log_level=logging.INFO, mode='a')

        self.client_username = os.getenv('CLIENT_USERNAME')
        if not self.client_username:
            self.logger.error("CLIENT_USERNAME environment variable is missing.")
            return

        self.logger.info("Starting Server.")
        self.app = Flask(__name__)
        self.setup_routes()
        
        self.app.logger.handlers = self.logger.handlers
        self.app.logger.setLevel(self.logger.level)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)  # This stops it from printing every request

        self.initialize_spotipy()
        
        self.stop_event = threading.Event()
        threading.Thread(target=self.token_refresh_thread, daemon=True).start()
        self.app.run(host="127.0.0.1", port=Settings.PROXY_SERVER_PORT)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Sets up the 'routing' for our proxy server so any 'method' call goes to our spotipy instance and 
                 all non 200 codes go to the logger.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def setup_routes(self):
        self.app.add_url_rule('/spotipy/<method_name>', 'spotipy_method', self.spotipy_method, methods=['POST'])
        
        @self.app.after_request
        def log_request(response):
            if response.status_code != 200:
                self.app.logger.info(f"{request.method} {request.path} {response.status_code}")
            return response
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Initializes our spotipy instance.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def initialize_spotipy(self):
        self.logger.info("Initializing Spotipy Client...")
        try:
            self.auth_manager = spotipy.oauth2.SpotifyOAuth(
                scope=' '.join(list(Settings.MAX_SCOPE_LIST)),
                open_browser=False,
                cache_handler=spotipy.CacheFileHandler(cache_path=f"tokens/.cache_spotipy_token_{self.client_username}")
            )
            self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
            self.sp.me() # Initialize the client by making a request
            self.logger.info("Spotipy client Initialized successfully.")
        except Exception as error:
            self.logger.critical(f"Failed to Initialize Spotipy client: {error}")
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Refreshes our token with backoff and retries.
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""     
    def refresh_token(self):
        retry_attempts = 5
        for attempt in range(retry_attempts):
            try:
                token_info = self.auth_manager.get_cached_token()
                new_token_info = self.auth_manager.refresh_access_token(token_info['refresh_token'])
                self.sp._session.headers["Authorization"] = f"Bearer {new_token_info['access_token']}"
                self.logger.info("Token refreshed successfully.")
                return True
            
            except Exception as error:
                self.logger.error(f"Token refresh attempt {attempt+1}/{retry_attempts} failed: {error}")
                if attempt < retry_attempts - 1:
                    sleep_time = 2 ** attempt + random.uniform(0, 0.5)
                    self.logger.warning(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.logger.critical("Token refresh failed after maximum retries.")
                    return False

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Thread method that refreshes the token when it is about to expire. 
    INPUT: N/A
    OUTPUT: N/A
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def token_refresh_thread(self):
        while not self.stop_event.is_set():
            token_info = self.auth_manager.get_cached_token()

            if not token_info or 'expires_at' not in token_info:
                self.logger.error("No valid cached token found.")
                self.initialize_spotipy()
                time.sleep(60)
                continue
            
            expires_in = token_info['expires_at'] - time.time()

            if expires_in <= 660:
                self.logger.warning(f"Token expires in {expires_in / 60:.1f} minutes! Refreshing.")
                success = self.refresh_token()
                if not success:
                    self.initialize_spotipy()

            sleep_time = max(self.auth_manager.get_cached_token()['expires_at'] - time.time() - 600, 60)
            self.logger.info(f"Next refresh in {sleep_time / 60:.1f} minutes.")
            self.stop_event.wait(sleep_time)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: Allows us to call any method from spotipy through our server.
    INPUT: method_name - The name of the method we want to call.
    OUTPUT: JSON result of our method call or an error message.
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def spotipy_method(self, method_name):
        payload = request.get_json(force=True)
        args = payload.get('args', [])
        kwargs = payload.get('kwargs', {})

        try:
            method = getattr(self.sp, method_name)
            return jsonify({"result": method(*args, **kwargs)})

        except AttributeError as error:
            self.logger.error(f"Invalid Spotipy method '{method_name}': {error}")
            return jsonify({"error": f"Invalid method '{method_name}': {error}"}), 400

        except TypeError as error:
            self.logger.error(f"Argument error or non-callable method '{method_name}': {error}")
            return jsonify({"error": f"Incorrect arguments or non-callable method '{method_name}': {error}"}), 400

        except Exception as error:
            self.logger.error(f"Unexpected error calling {method_name}: {error}")
            return jsonify({"error": str(error)}), 500


if __name__ == '__main__':
    while True:
        try:
            server = SpotifyServer()
        except Exception as e:
            logging.error(f"Server crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════