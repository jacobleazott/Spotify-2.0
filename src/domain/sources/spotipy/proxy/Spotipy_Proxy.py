# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SPOTIPY PROXY                            CREATED: 2025-02-08          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Offers a proxy for spotipy. This way all methods from spotipy can be called like we actually own the instance, 
#   when in reality it is all passed through our proxy to our flask server that owns the object.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import sys
import time
import requests

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Abstracted proxy for spotipy. This way all methods from spotipy can be called like we actually own the 
                instance, when in reality it is all passed through our proxy to our flask server that owns the object.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SpotipyProxy(LogAllMethods):
    
    def __init__(self, logger: logging.Logger=None, max_retries: int=3
                 , backoff_factor: float=1.0, overall_timeout: int=20) -> None:
        self.logger = logger if logger is not None else logging.getLogger()
        self.base_url=f"http://127.0.0.1:{Settings.PROXY_SERVER_PORT}"
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.overall_timeout = overall_timeout
    
    def __getattr__(self, method_name):
        def method(*args, **kwargs):
            url = f"{self.base_url}/spotipy/{method_name}"
            payload = {"args": args, "kwargs": kwargs}
            start_time = time.perf_counter()  # Track the start time of the method execution
            
            for attempt in range(self.max_retries):
                try:
                    # Check if the total time elapsed exceeds the overall timeout
                    elapsed_time = time.perf_counter() - start_time
                    if elapsed_time > self.overall_timeout:
                        raise TimeoutError(f"Operation timed out after {self.overall_timeout} seconds")
                    
                    # Make the request with a short timeout for each individual request
                    response = requests.post(url, json=payload, timeout=5)
                    if response.status_code == 500:
                        raise Exception("Server error 500 - Retrying...")
                    
                    data = response.json()
                    if "error" in data:
                        raise Exception(data["error"])

                    return data["result"]

                except Exception as error:
                    # Check if the total time exceeded the overall timeout before retrying
                    elapsed_time = time.perf_counter() - start_time
                    if elapsed_time > self.overall_timeout:
                        raise TimeoutError(f"Operation timed out after {self.overall_timeout} seconds")
                    
                    # Backoff and retry
                    delay = self.backoff_factor * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Retrying... (attempt {attempt + 1}/{self.max_retries}), error: {error}")
                    time.sleep(delay)
                    
            self.logger.error(f"Request failed after {self.max_retries} attempts.")
            sys.exit(0)

        return method


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════