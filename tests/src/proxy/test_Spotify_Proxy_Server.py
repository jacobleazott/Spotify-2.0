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
import time
import unittest

from unittest import mock
from flask import Flask

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
    @mock.patch('src.proxy.Spotify_Proxy_Server.threading')
    def setUp(self, mock_threading, mock_spotipy, mock_flask, mock_get_file_logger):
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
    
    @mock.patch('src.proxy.Spotify_Proxy_Server.SpotifyServer._initialize_spotipy')
    @mock.patch('src.proxy.Spotify_Proxy_Server.SpotifyServer._refresh_token')
    @mock.patch('src.proxy.Spotify_Proxy_Server.time.sleep')
    def test_token_refresh_thread(self, mock_sleep, mock_refresh_token, mock_initialize_spotipy):
        mock_stop_event = mock.MagicMock()
        self.proxy_server.stop_event = mock_stop_event
        mock_auth_manager = mock.MagicMock()
        self.proxy_server.auth_manager = mock_auth_manager
        
        def reset_mocks():
            mock_sleep.reset_mock()
            mock_refresh_token.reset_mock()
            mock_initialize_spotipy.reset_mock()
            mock_stop_event.reset_mock()
            mock_auth_manager.reset_mock()
            mock_stop_event.is_set.reset_mock()
        
        # Test Non Expired Token
        expires_in = 700
        mock_stop_event.is_set.side_effect = [False, True]
        mock_auth_manager.get_cached_token.side_effect = [
            {'expires_at': time.time() + expires_in}
            , {'expires_at': time.time() + expires_in}
        ]
        self.proxy_server._token_refresh_thread()
        
        mock_initialize_spotipy.assert_not_called()
        mock_refresh_token.assert_not_called()
        self.assertAlmostEqual(mock_stop_event.wait.call_args[0][0], expires_in - 600, places=2)
        mock_stop_event.wait.assert_called_once()
        reset_mocks()
        
        # Test Expired Token - Successful Refresh
        expires_in = 3600
        mock_refresh_token.return_value = True
        mock_stop_event.is_set.side_effect = [False, True]
        mock_auth_manager.get_cached_token.side_effect = [
            {'expires_at': time.time() + 500}
            , {'expires_at': time.time() + expires_in}
        ]
        self.proxy_server._token_refresh_thread()
        
        mock_refresh_token.assert_called_once()
        mock_initialize_spotipy.assert_not_called()
        self.assertAlmostEqual(mock_stop_event.wait.call_args[0][0], expires_in - 600, places=2)
        mock_stop_event.wait.assert_called_once()
        reset_mocks()
        
        # Test Expired Token - Failed Refresh
        expires_in = 100
        mock_refresh_token.return_value = False
        mock_stop_event.is_set.side_effect = [False, True]
        mock_auth_manager.get_cached_token.side_effect = [
            {'expires_at': time.time() + expires_in}
            , {'expires_at': time.time() + expires_in}
        ]
        self.proxy_server._token_refresh_thread()
        
        mock_refresh_token.assert_called_once()
        mock_initialize_spotipy.assert_called_once()
        self.assertAlmostEqual(mock_stop_event.wait.call_args[0][0], 60, places=2)
        mock_stop_event.wait.assert_called_once()
        reset_mocks()
        
        # Test None Token
        mock_stop_event.is_set.side_effect = [False, True]
        expires_in = 3600
        mock_auth_manager.get_cached_token.side_effect = [
            None
        ]
        self.proxy_server._token_refresh_thread()
        
        mock_initialize_spotipy.assert_called_once()
        mock_refresh_token.assert_not_called()
        mock_stop_event.wait.assert_not_called()
        reset_mocks()
        
        # Test Missing 'expires_at' Key
        mock_stop_event.is_set.side_effect = [False, False, True]
        expires_in = 3600
        mock_auth_manager.get_cached_token.side_effect = [
            {}
            , {'expires_at': time.time() + expires_in}
            , {'expires_at': time.time() + expires_in}
        ]
        self.proxy_server._token_refresh_thread()
        
        mock_initialize_spotipy.assert_called_once()
        mock_refresh_token.assert_not_called()
        self.assertAlmostEqual(mock_stop_event.wait.call_args[0][0], expires_in - 600, places=2)
        
    def test_spotipy_method(self):
        mock_spotipy = mock.MagicMock()
        self.proxy_server.sp = mock_spotipy
        app = Flask(__name__)
        self.proxy_server.app = app
        client = app.test_client()
        self.proxy_server._setup_routes()
        
        # Test Successful Call
        payload = {
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"}
        }
        mock_spotipy.sample_method.return_value = "mocked"
        response = client.post('/spotipy/sample_method', json=payload)
        self.assertEqual(response.json, {"result": "mocked"})
        self.assertEqual(response.status_code, 200)
        mock_spotipy.sample_method.assert_called_once_with("arg1", "arg2", key1="value1")
        mock_spotipy.reset_mock()
        
        # Test Nonexistent Method
        mock_spotipy.nonexistent_method.side_effect = AttributeError("example_error")
        response = client.post('/spotipy/nonexistent_method', json={})
        self.assertEqual(response.json, {'error': "Invalid method 'nonexistent_method': example_error"})
        self.assertEqual(response.status_code, 400)
        mock_spotipy.reset_mock()
        
        # Test Argument Error
        response = client.post('/spotipy/arg_method', json={})
        self.assertEqual(response.json, {'error': "Incorrect arguments or non-callable method 'arg_method': " +
                                         "Object of type MagicMock is not JSON serializable"})
        self.assertEqual(response.status_code, 400)
        
        # Test Generic Exception
        mock_spotipy.sample_method.side_effect = Exception("Test Exception")
        response = client.post('/spotipy/sample_method', json={})
        self.assertEqual(response.json, {'error': 'Test Exception'})
        self.assertEqual(response.status_code, 500)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════