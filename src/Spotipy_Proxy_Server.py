# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIPY PROXY SERVER                     CREATED: 2025-02-08          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# 
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import sys
import requests
import spotipy
import threading
import time
from flask import Flask, request, jsonify

from src.helpers.Settings import Settings
from src.helpers.decorators import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Creates and manages a flask server as well as our spotipy instance. Handles token refreshing and allows 
                us to have a consistant connection to the API.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotifyServer():
    
    def __init__(self):
        client_username = os.getenv('CLIENT_USERNAME')
        if not client_username:
            self.logger.error("CLIENT_USERNAME environment variable is missing.")
            return

        self.logger = get_file_logger(f'logs/0_server.log', log_level=logging.INFO, mode='a')
        self.logger.info("Starting Server.")
        
        self.app = Flask(__name__)
        self.setup_routes()
        self.app.logger.handlers = self.logger.handlers
        self.app.logger.setLevel(self.logger.level)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)  # This stops it from printing every request

        self.auth_manager = spotipy.oauth2.SpotifyOAuth(
            scope=' '.join(list(Settings.MAX_SCOPE_LIST)),
            open_browser=False,
            cache_handler=spotipy.CacheFileHandler(cache_path=f"tokens/.cache_spotipy_token_{client_username}")
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        # self.sp.me() # Force API handshake once to avoid delay later
        
        self.logger.info("Server Started With Spotify Connection.")
        
        self.stop_event = threading.Event()
        threading.Thread(target=self.token_refresh_thread, daemon=True).start()
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def setup_routes(self):
        self.app.add_url_rule('/spotipy/<method_name>', 'spotipy_method', self.spotipy_method, methods=['POST'])
        
        @self.app.after_request
        def log_request(response):
            if response.status_code != 200:
                self.app.logger.info(f"{request.method} {request.path} {response.status_code}")
            return response
            
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def refresh_token(self):
        try:
            token_info = self.auth_manager.get_cached_token()
            new_token_info = self.auth_manager.refresh_access_token(token_info['refresh_token'])

            if token_info['access_token'] == new_token_info['access_token']:
                self.logger.warning("Token refresh returned the same token.")
            else:
                self.logger.info("Token refreshed successfully.")

            self.sp._session.headers["Authorization"] = f"Bearer {new_token_info['access_token']}"

        except Exception as error:
            self.logger.error(f"Error refreshing token: {error}")

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def token_refresh_thread(self):
        while not self.stop_event.is_set():
            # Get the latest token info
            token_info = self.auth_manager.get_cached_token()

            if not token_info or 'expires_at' not in token_info:
                self.logger.error("No valid cached token found.")
                return
            
            expires_in = token_info['expires_at'] - time.time()

            if expires_in <= 660:
                self.logger.warning(f"Token expires in {expires_in / 60:.1f} minutes! Refreshing.")
                self.refresh_token()
                token_info = self.auth_manager.get_cached_token()  # Get updated token info
                expires_in = token_info['expires_at'] - time.time()

            # Calculate next sleep time (wake up 10 mins before expiration)
            sleep_time = max(expires_in - 600, 60)  # Ensure at least 1 min sleep

            self.logger.info(f"Next refresh in {sleep_time / 60:.1f} minutes.")
            self.stop_event.wait(sleep_time)
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def spotipy_method(self, method_name):
        payload = request.get_json(force=True)
        args = payload.get('args', [])
        kwargs = payload.get('kwargs', {})

        try:
            method = getattr(self.sp, method_name)
            return jsonify({"result": method(*args, **kwargs)})

        except AttributeError as error:
            self.app.logger.error(f"Invalid Spotipy method '{method_name}': {error}")
            return jsonify({"error": f"Invalid method '{method_name}': {error}"}), 400

        except TypeError as error:
            self.app.logger.error(f"Argument error or non-callable method '{method_name}': {error}")
            return jsonify({"error": f"Incorrect arguments or non-callable method '{method_name}': {error}"}), 400

        except Exception as error:
            self.app.logger.error(f"Unexpected error calling {method_name}: {error}")
            return jsonify({"error": str(error)}), 500


    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def run(self):
        self.app.run(host="0.0.0.0", port=5000)


if __name__ == '__main__':
    
    while True:
        try:
            server = SpotifyServer()
            server.run()
        except Exception as e:
            # Log the exception, wait briefly, then restart.
            logging.error(f"Server crashed: {e}. Restarting in 5 seconds...")
            time.sleep(5)
        else:
            # If server.run() ever exits without exception, exit the loop.
            break


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Abstracted proxy for spotipy. This way all methods from spotipy can be called like we actually own the 
                instance, when in reality it is all passed through our proxy to our flask server that owns the object.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotipyProxy:
    
    def __init__(self, base_url="http://127.0.0.1:5000", max_retries=3, backoff_factor=1.0, overall_timeout=20):
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.overall_timeout = overall_timeout
    
    def __getattr__(self, method_name):
        def method(*args, **kwargs):
            url = f"{self.base_url}/spotipy/{method_name}"
            payload = {"args": args, "kwargs": kwargs}
            attempt = 0
            start_time = time.perf_counter()  # Track the start time of the method execution

            while attempt < self.max_retries:
                try:
                    # Check if the total time elapsed exceeds the overall timeout
                    elapsed_time = time.perf_counter() - start_time
                    if elapsed_time > self.overall_timeout:
                        raise Exception(f"Operation timed out after {self.overall_timeout} seconds")
                    
                    # Make the request with a short timeout for each individual request
                    response = requests.post(url, json=payload, timeout=5)
                    if response.status_code == 500:
                        raise Exception("Server error 500 - Retrying...")

                    data = response.json()
                    if "error" in data:
                        raise Exception(data["error"])

                    # If no error, return the result
                    return data["result"]

                except (requests.exceptions.RequestException, Exception) as error:
                    # Check if the total time exceeded the overall timeout before retrying
                    elapsed_time = time.perf_counter() - start_time
                    if elapsed_time > self.overall_timeout:
                        raise Exception(f"Operation timed out after {self.overall_timeout} seconds")

                    # If it's not the last retry, backoff and retry
                    if attempt >= self.max_retries - 1:
                        print(f"Request failed after {self.max_retries} attempts.")
                        raise error  # Raise the exception if we've reached the max retries
                    else:
                        # If the exception is temporary (e.g., 500 error), retry after backoff
                        delay = self.backoff_factor * (2 ** attempt)  # Exponential backoff
                        print(f"Retrying... (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(delay)
                        attempt += 1

        return method


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════