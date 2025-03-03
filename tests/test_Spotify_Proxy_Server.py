# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SPOTIFY PROXY SERVER        CREATED: 2025-03-02          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Spotify_Proxy_Server.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import os
import logging
import unittest
from unittest import mock
from flask import Flask, request, jsonify

from src.helpers.Settings           import Settings
from src.proxy.Spotify_Proxy_Server import SpotifyServer
from tests.helpers.mocked_Settings  import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Spotify Proxy Server functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.proxy.Spotipy_Proxy.Settings', Test_Settings)
class TestSpotifyProxyServer(unittest.TestCase):
    
    @mock.patch('src.proxy.Spotify_Proxy_Server.get_file_logger')
    @mock.patch('src.proxy.Spotify_Proxy_Server.Flask')
    @mock.patch('src.proxy.Spotify_Proxy_Server.spotipy')
    def setUp(self, mock_spotipy, mock_flask, mock_get_file_logger):
        self.mock_app = mock_flask.return_value
        self.mock_logger = mock.MagicMock()
        mock_get_file_logger.return_value = self.mock_logger
        os.environ['CLIENT_USERNAME'] = "TEST"
        self.proxy_server = SpotifyServer()
        self.mock_app.reset_mock()
        self.mock_logger.reset_mock()

    # Since we need to create new instances, need to reapply all mocks
    @mock.patch('src.proxy.Spotify_Proxy_Server.get_file_logger')
    @mock.patch('src.proxy.Spotify_Proxy_Server.Flask')
    @mock.patch('src.proxy.Spotify_Proxy_Server.spotipy')
    @mock.patch('src.proxy.Spotify_Proxy_Server.threading')
    def test_init(self, mocked_threading, mocked_spotipy, mocked_flask, mocked_get_logger):
        # Test Default
        os.environ['CLIENT_USERNAME'] = "TEST"
        proxy = SpotifyServer()
        mocked_get_logger.assert_called_once()
        mocked_flask.assert_called_once()
        mocked_spotipy.Spotify.assert_called_once()
        mocked_threading.Thread.assert_called_once_with(target=proxy._token_refresh_thread, daemon=True)
        mocked_threading.Thread.return_value.start.assert_called_once()
        mocked_flask.return_value.run.assert_called_once_with(host="127.0.0.1", port=Settings.PROXY_SERVER_PORT)
        mocked_flask.reset_mock()
        
        # Test No CLIENT_USERNAME
        os.environ['CLIENT_USERNAME'] = ""
        mock_logger = mock.MagicMock()
        mocked_get_logger.return_value = mock_logger
        SpotifyServer()
        mock_logger.error.assert_called_once_with("CLIENT_USERNAME environment variable is missing.")
        mocked_flask.assert_not_called()
        
        
    def test_setup_routes(self):
        app = Flask(__name__)
        self.proxy_server.app = app
        self.proxy_server._setup_routes()
        
        # Simulate request context with method and path
        with app.test_request_context('/spotipy/some_method', method='POST'):
            # Access the after_request function (Flask's internal decorator storage)
            log_request = app.after_request_funcs.get(None)[0]
            log_request(mock.MagicMock(status_code=500))
            self.mock_logger.info.assert_called_once_with("POST /spotipy/some_method 500")
            self.mock_logger.reset_mock()
            log_request(mock.MagicMock(status_code=200))
            self.mock_logger.info.assert_not_called()

    @mock.patch('src.proxy.Spotify_Proxy_Server.spotipy')
    def test_initialize_spotipy(self, mock_spotipy):
        self.proxy_server._initialize_spotipy()
        mock_spotipy.Spotify.assert_called_once()
        self.mock_logger.info.assert_any_call("Spotipy client Initialized successfully.")
        
        mock_spotipy.Spotify.side_effect = Exception("Test Exception")
        self.proxy_server._initialize_spotipy()
        self.mock_logger.critical.assert_called_once()
    
    @mock.patch('src.proxy.Spotify_Proxy_Server.time.sleep')
    def test_refresh_token(self, mock_sleep):
        self.assertTrue(self.proxy_server._refresh_token())
        self.mock_logger.info.assert_called_once_with("Token refreshed successfully.")
        
        self.proxy_server.auth_manager.get_cached_token.side_effect = Exception("Test Exception")
        
        self.assertFalse(self.proxy_server._refresh_token())
        self.assertEqual(mock_sleep.call_count, 4)
        self.assertEqual(self.mock_logger.error.call_count, 5)
    
    def test_token_refresh_thread(self):
        pass
    
    def test_spotipy_method(self):
        pass
    


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════