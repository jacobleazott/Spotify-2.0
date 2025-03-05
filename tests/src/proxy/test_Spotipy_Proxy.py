# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - SPOTIPY PROXY            CREATED: 2025-03-02          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Spotipy_Proxy.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import unittest
from unittest import mock

from src.proxy.Spotipy_Proxy        import SpotipyProxy
from tests.helpers.mocked_Settings  import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Spotipy Proxy functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.proxy.Spotipy_Proxy.Settings', Test_Settings)
class TestSpotipyProxy(unittest.TestCase):
    
    def test_init(self):
        test_defaults_spotipy_proxy = SpotipyProxy()
        # Test Defaults
        self.assertEqual(test_defaults_spotipy_proxy.logger, logging.getLogger())
        self.assertEqual(test_defaults_spotipy_proxy.base_url, f"http://127.0.0.1:{Test_Settings.PROXY_SERVER_PORT}")
        self.assertEqual(test_defaults_spotipy_proxy.max_retries, 3)
        self.assertEqual(test_defaults_spotipy_proxy.backoff_factor, 1.0)
        self.assertEqual(test_defaults_spotipy_proxy.overall_timeout, 20)
        
        # Test Custom
        Test_Settings.PROXY_SERVER_PORT = "1212"
        logger = mock.MagicMock()
        test_spotipy_proxy = SpotipyProxy(logger=logger, max_retries=20, backoff_factor=99.9, overall_timeout=1000)
        
        self.assertEqual(test_spotipy_proxy.logger, logger)
        self.assertEqual(test_spotipy_proxy.base_url, "http://127.0.0.1:1212")
        self.assertEqual(test_spotipy_proxy.max_retries, 20)
        self.assertEqual(test_spotipy_proxy.backoff_factor, 99.9)
        self.assertEqual(test_spotipy_proxy.overall_timeout, 1000)
    
    @mock.patch('src.proxy.Spotipy_Proxy.requests')
    def test_get_attr(self, mocked_requests):
        spotipy_proxy = SpotipyProxy(backoff_factor=0.0)
        mock_requests_post = mocked_requests.post
        
        # Test 200 Response
        mock_requests_post.return_value.status_code = 200
        mock_requests_post.return_value.json.return_value = {"result": "test"}
        self.assertEqual(spotipy_proxy.test1(), "test")
        mock_requests_post.assert_called_once()
        mock_requests_post.reset_mock()
        
        # Test 500 Response Max Retries
        mock_requests_post.return_value.status_code = 500
        mock_requests_post.return_value.json.return_value = {"result": "test"}
        with self.assertRaises(Exception):
            spotipy_proxy.test1()
        self.assertEqual(mock_requests_post.call_count, 3)
        mock_requests_post.reset_mock()

        # Test 500 Response Then 200
        mock_response_1 = mock.Mock(status_code=500)
        mock_response_1.json.return_value = {"result": "test2"}
        mock_response_2 = mock.Mock(status_code=200)
        mock_response_2.json.return_value = {"result": "test2"}
        mock_requests_post.side_effect = [mock_response_1, mock_response_2]
        
        self.assertEqual(spotipy_proxy.any_Fake_Method_Name(), "test2")
        self.assertEqual(mock_requests_post.call_count, 2)
        mock_requests_post.reset_mock()
        
        # Test Error In Response
        mock_response_1 = mock.Mock(status_code=200)
        mock_response_1.json.return_value = {"error": "test3"}
        mock_response_2 = mock.Mock(status_code=200)
        mock_response_2.json.return_value = {"result": "test3"}
        mock_requests_post.side_effect = [mock_response_1, mock_response_2]
        
        self.assertEqual(spotipy_proxy.any_Fake_Method_Name(), "test3")
        self.assertEqual(mock_requests_post.call_count, 2)
        mock_requests_post.reset_mock()

        # Test Timeout
        spotipy_proxy.overall_timeout = 0
        with self.assertRaises(Exception):
            spotipy_proxy.method1274()
        self.assertEqual(mock_requests_post.call_count, 0)


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════