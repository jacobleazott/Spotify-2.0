# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - DECORATORS                  CREATED: 2025-03-02          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'decorators.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

import logging
import requests
import unittest
from unittest import mock

from src.helpers.decorators import *
from src.helpers.Settings   import Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Decorators functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestDecorators(unittest.TestCase):
    
    def test_get_file_logger(self):
        logger = get_file_logger('test1.log')
        self.assertTrue(logger.isEnabledFor(logging.INFO))
        self.assertEqual(logger.handlers[0].mode, 'w')
        self.assertEqual(len(logger.handlers), 1)
        
        logger = get_file_logger('test2.log', log_level=logging.ERROR, mode='a', console=True)
        self.assertTrue(logger.isEnabledFor(logging.ERROR))
        self.assertEqual(logger.handlers[0].mode, 'a')
        self.assertEqual(len(logger.handlers), 2)
        self.assertIsInstance(logger.handlers[0], logging.FileHandler)
        self.assertIsInstance(logger.handlers[1], logging.StreamHandler)
    
    def test_log_func_defaults_and_exceptions(self):
        with mock.patch('src.helpers.decorators.logging') as mock_logging:
            mock_log = mock.MagicMock()
            mock_logging.getLogger.return_value = mock_log
            
            # Test No Logger, ConnectionError Exception
            with self.assertRaises(requests.exceptions.ConnectionError):
                @log_func
                def test_func_ConnectionError():
                    raise requests.exceptions.ConnectionError()
                test_func_ConnectionError()
            
            mock_logging.getLogger.assert_called_once()
            mock_log.log.assert_not_called()
            mock_log.error.assert_called_once_with("Failed to establish connection to proxy server: ")
            mock_logging.reset_mock()
            mock_log.reset_mock()
            
            # Test No Logger, RequestException Exception
            with self.assertRaises(requests.exceptions.RequestException):
                @log_func
                def test_func_RequestException():
                    raise requests.exceptions.RequestException()
                test_func_RequestException()
            
            mock_logging.getLogger.assert_called_once()
            mock_log.log.assert_not_called()
            mock_log.error.assert_called_once_with("Request to Spotify API failed: ")
            mock_logging.reset_mock()
            mock_log.reset_mock()

            # Test No Logger, Generic Exception
            with self.assertRaises(Exception):
                @log_func
                def test_func_Exception():
                    raise Exception()
                test_func_Exception()
            
            mock_logging.getLogger.assert_called_once()
            mock_log.log.assert_not_called()
            mock_log.error.assert_called_once_with(f"Exception raised in test_func_Exception. exception: "
                                                   , exc_info=True)
            mock_logging.reset_mock()
            mock_log.reset_mock()
    
    def test_log_func_with_logger(self):
        mock_logger = mock.MagicMock()
        mock_logger.__class__ = logging.Logger
        mock_logger.isEnabledFor.return_value = True
        
        # Test Passing In Logger Through Args
        @log_func
        def test_args_func(logger):
            pass
        test_args_func(mock_logger)
        mock_logger.log.assert_called_once_with(Settings.FUNCTION_ARG_LOGGING_LEVEL
                                                , f"_function test_args_func called with {repr(mock_logger)}")
        mock_logger.reset_mock()

        # Test Passing In Logger Through Kwargs
        @log_func
        def test_kwargs_func(logger=None):
            pass
        test_kwargs_func(logger=mock_logger)
        mock_logger.log.assert_called_once_with(Settings.FUNCTION_ARG_LOGGING_LEVEL
                                                , f"_function test_kwargs_func called with logger={repr(mock_logger)}")
        mock_logger.reset_mock()
        
        # Test Passing In Logger Through Class Member
        class TestClass():
            def __init__(self):
                self.logger = mock_logger
            
            @log_func
            def test_func(self):
                pass
        
        TestClass().test_func()
        # Because we log the self argument it's a little hard to test exactly.
        mock_logger.log.assert_called_once()
        mock_logger.reset_mock()
    
    @mock.patch('src.helpers.decorators.log_func')
    def test_log_func_called(self, mock_log_func):
        
        class TestClassMethod(LogAllMethods):
            def test_method(self):
                pass
        
        TestClassMethod().test_method()
        mock_log_func.assert_called_once()
        mock_log_func.reset_mock()
        
        class TestClassNoMethod(LogAllMethods):
            test_attribute = 'test'

        TestClassNoMethod().test_attribute
        mock_log_func.log.assert_not_called()
        
    def test_log_func_none(self):
        mock_func = mock.Mock(return_value="success")

        # Apply the decorator without arguments
        decorator = log_func()  # This should return the inner 'decorator_log'
        self.assertTrue(callable(decorator))

        decorated_func = decorator(mock_func)
        
        result = decorated_func()
        self.assertEqual(result, "success")


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════