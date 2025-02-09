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
        self.app = Flask(__name__)
        self.setup_routes()
        
        self.logger = get_file_logger(f'logs/0_server.log', log_level=logging.INFO, mode='a')
        self.app.logger.handlers = self.logger.handlers
        self.app.logger.setLevel(self.logger.level)
        # log = logging.getLogger('werkzeug')
        # log.setLevel(logging.ERROR)  # This stops it from printing every request

        self.auth_manager = spotipy.oauth2.SpotifyOAuth(
            scope=' '.join(list(Settings.MAX_SCOPE_LIST)),
            open_browser=False,
            cache_handler=spotipy.CacheFileHandler(
                cache_path=f"tokens/.cache_spotipy_token_{os.environ['CLIENT_USERNAME']}"
            )
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)
        threading.Thread(target=self.token_refresh_thread, daemon=True).start()
    
    
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # def setup_routes(self):
    #     self.app.add_url_rule('/spotipy/<method_name>', 'spotipy_method', self.spotipy_method, methods=['POST'])

    def setup_routes(self):
        @self.app.route('/spotipy/<method_name>', methods=['POST'])
        def spotipy_method(method_name):
            payload = request.get_json(force=True)
            args = payload.get('args', [])
            kwargs = payload.get('kwargs', {})
            try:
                method = getattr(self.sp, method_name)
                result = method(*args, **kwargs)
                return jsonify({"result": result})
            except Exception as error:
                self.app.logger.error(f"Error calling {method_name}: {str(error)}")
                return {"error": str(error)}, 500
        
        @self.app.after_request
        def log_request(response):
            self.app.logger.info(f"{request.method} {request.path} {response.status_code}")
            return response
            
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # Function to refresh the token and update the Spotipy session headers
    def refresh_token(self):
        token_info = self.auth_manager.get_cached_token()
        self.sp._session.headers["Authorization"] = f"Bearer {token_info['access_token']}"
        self.sp.me()
        self.logger.info("Refreshing Token")
        self.auth_manager.refresh_access_token(token_info['refresh_token'])
        token_info2 = self.auth_manager.get_cached_token()
        if token_info['access_token'] == token_info2['access_token']:
            self.logger.info("WHAT THE FUCK ------------------------------------------------")
        else:
            self.logger.info("Refreshed No Issue")
        self.sp._session.headers["Authorization"] = f"Bearer {token_info2['access_token']}"

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    # Background thread to refresh the token periodically
    def token_refresh_thread(self):
        while True:
            self.refresh_token()
            time.sleep(60 * 5)  # refresh every 50 minutes
    
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
            # Get the method from the Spotipy instance
            method = getattr(self.sp, method_name)
            # Call the method with the provided arguments
            result = method(*args, **kwargs)
            return jsonify({"result": result})
        except Exception as e:
            self.logger.error(f"Error during {method_name}: {e}")  # Add additional logging here
            return jsonify({"error": str(e)}), 500

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    DESCRIPTION: 
    INPUT: 
    OUTPUT: 
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''"""
    def run(self):
        self.app.run(host="0.0.0.0", port=5000)


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


if __name__ == '__main__':
    SpotifyServer().run()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════