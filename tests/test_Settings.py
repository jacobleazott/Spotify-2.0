# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    SANITY TEST - MOCKED SETTINGS            CREATED: 2025-03-03          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit test to verify 'mocked_Settings.py' has all attributes 'Settings.py' does.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import unittest
from dataclasses import fields

from src.helpers.Settings           import SettingsClass
from tests.helpers.mocked_Settings  import MockedSettingsClass

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test to verify mocked_Settings.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestSpotifyProxyServer(unittest.TestCase):

    def test_settings_class_attributes(self):
        settings_class_attributes = {field.name for field in fields(SettingsClass)}
        built_in_attributes = {'__dict__', '__module__', '__weakref__', '__annotations__', '__doc__'}
        mocked_settings_class_attributes = set(vars(MockedSettingsClass)) - built_in_attributes

        missing_attributes_in_mock = settings_class_attributes - mocked_settings_class_attributes
        missing_attributtes_in_settings = mocked_settings_class_attributes - settings_class_attributes

        self.assertEqual(len(missing_attributes_in_mock), 0
                         , f"Missing Attributes In Mock: {missing_attributes_in_mock}")
        self.assertEqual(len(missing_attributtes_in_settings), 0
                         , f"Missing attributes In Settings: {missing_attributtes_in_settings}")


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════