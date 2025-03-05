# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - MANUAL                      CREATED: 2025-03-04          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Manual.py'.
# This isn't necessarily "source" code as it's just a helper to manually run any method from any class or member class.
#   Which helps extensively with testing and development.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import unittest
from unittest import mock

from src.helpers.Manual import MethodInvoker, main

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Test Classes For Unit Testing.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SubFeature:
    def method_with_args(self, arg1: int, arg2: str = "default"):
        return f"arg1={arg1}, arg2={arg2}"

class FakeFeature:
    
    def __init__(self):
        self.sub_feat = SubFeature()
    
    def simple_method(self):
        return "simple_called"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all 'Manual.py' functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestManual(unittest.TestCase):
    
    def setUp(self):
        self.invoker = MethodInvoker(FakeFeature())

    @mock.patch("src.helpers.Manual.Prompt.ask")
    def test_get_valid_choice(self, mock_ask):
        mock_ask.return_value = "1"
        self.assertEqual(self.invoker.get_valid_choice("Select", 3), 1)
        
        mock_ask.return_value = ""
        self.assertEqual(self.invoker.get_valid_choice("Select", 3), 0)
        
        mock_ask.side_effect = ["invalid", "4", "1"]
        self.assertEqual(self.invoker.get_valid_choice("Select", 3), 1)

    @mock.patch("src.helpers.Manual.Prompt.ask")
    def test_get_user_input(self, mock_ask):
        mock_ask.return_value = "42"
        self.assertEqual(self.invoker.get_user_input("test", int), 42)

        mock_ask.return_value = ""
        self.assertEqual(self.invoker.get_user_input("test", int), None)
        self.assertEqual(self.invoker.get_user_input("test", int, 99), 99)
        
        mock_ask.side_effect = ["invalid", "15"]
        self.assertEqual(self.invoker.get_user_input("test", int), 15)

    def test_get_available_classes(self):
        classes = self.invoker.get_available_classes()
        self.assertIn("sub_feat", classes)
        self.assertIsInstance(classes["sub_feat"], SubFeature)
    
    @mock.patch("src.helpers.Manual.Prompt.ask")
    def test_select_class(self, mock_ask):
        mock_ask.side_effect = ["0", "1"]
        self.invoker.select_class()
        self.assertIsInstance(self.invoker.obj, FakeFeature)
        
        mock_ask.side_effect = ["1", "0"]
        self.invoker.select_class()
        self.assertIsInstance(self.invoker.obj, SubFeature)

    def test_display_available_methods(self):
        methods = self.invoker.display_available_methods()
        self.assertIn("simple_method", methods)
        self.assertTrue(callable(methods["simple_method"]))
    
    def test_invoke_simple_method(self):
        with mock.patch.object(self.invoker, "get_valid_choice") as mock_get_valid_choice:
            with mock.patch.object(self.invoker, "get_user_input") as mock_get_user_input:
                mock_get_valid_choice.return_value = 0
                mock_get_user_input.return_value = None
                self.invoker.invoke_method()
                self.assertEqual(self.invoker.obj.simple_method(), "simple_called")
                
                mock_get_valid_choice.side_effect = [1, 0, 0]
                mock_get_user_input.side_effect = [10, "custom"]
                self.invoker.invoke_method()
                self.assertEqual(self.invoker.obj.method_with_args(10, "custom"), "arg1=10, arg2=custom")
    
    @mock.patch("src.helpers.Manual.MethodInvoker")
    @mock.patch("src.helpers.Manual.SpotifyFeatures")
    @mock.patch("src.helpers.Manual.os.system")
    def test_main(self, mock_clear, mock_spotify, mock_invoker):
        main()

        mock_clear.assert_called_once_with("clear")
        mock_spotify.assert_called_once_with(log_file_name="Manual.log")
        mock_invoker.assert_called_once_with(mock_spotify())
        mock_invoker.return_value.invoke_method.assert_called_once()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════