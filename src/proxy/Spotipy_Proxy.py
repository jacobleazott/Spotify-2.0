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
import time
import requests

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