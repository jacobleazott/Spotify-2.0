# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - DATABASE HELPERS            CREATED: 2025-04-27          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Database_Helpers.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import sqlite3
import uuid
import unittest
from unittest import mock

import src.General_Spotify_Helpers  as gsh
import tests.helpers.tester_helpers as thelp

from tests.helpers.mocked_spotipy     import MockedSpotipyProxy
from src.helpers.Database_Helpers     import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Backup Spotify Data functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestDatabaseHelpers(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_replace_none(self):
        # Test replacing None values in a simple dictionary.
        input_data = {"key1": "value1", "key2": None, "key3": 123}
        expected_output = {"key1": "value1", "key2": "unknown", "key3": 123}
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in a simple list.
        input_data = [1, None, "value", None]
        expected_output = [1, "unknown", "value", "unknown"]
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in a nested dictionary.
        input_data = {"key1": {"subkey1": None, "subkey2": "value"}, "key2": 123}
        expected_output = {"key1": {"subkey1": "unknown", "subkey2": "value"}, "key2": 123}
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in a nested list.
        input_data = [1, [None, "value"], [None, 3]]
        expected_output = [1, ["unknown", "value"], ["unknown", 3]]
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in a combination of nested dictionaries and lists.
        input_data = {"key1": [1, None, {"subkey1": None}], "key2": None}
        expected_output = {"key1": [1, "unknown", {"subkey1": "unknown"}], "key2": "unknown"}
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test when no None values are present.
        input_data = {"key1": "value", "key2": 123, "key3": [1, "two"]}
        expected_output = {"key1": "value", "key2": 123, "key3": [1, "two"]}
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in an empty dictionary.
        input_data = {}
        expected_output = {}
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None values in an empty list.
        input_data = []
        expected_output = []
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test when input is None.
        input_data = None
        expected_output = "unknown"
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
        # Test replacing None in a complex structure with nested dictionaries and lists.
        input_data = {
            "key1": [1, {"subkey1": None, "subkey2": [None, 2]}, None],
            "key2": {"nested": [None, 5]},
            "key3": None
        }
        expected_output = {
            "key1": [1, {"subkey1": "unknown", "subkey2": ["unknown", 2]}, "unknown"],
            "key2": {"nested": ["unknown", 5]},
            "key3": "unknown"
        }
        self.assertEqual(replace_none(input_data, "unknown"), expected_output)
        
    def test_get_column_types(self):
        # Test for correct Python types for a table.
        conn = sqlite3.connect(":memory:")
        conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                data BLOB,
                value NUMERIC
            )""")
        conn.commit()
        self.assertEqual(get_column_types(conn, "test_table"), [int, str, float, bytes, float])
        
        # Test for a column with an unsupported SQLite type.
        conn.execute("""
            CREATE TABLE test_unsupported (
                id INTEGER PRIMARY KEY,
                custom_column CUSTOM_TYPE
            )""")
        conn.commit()
        self.assertEqual(get_column_types(conn, "test_unsupported"), [int, str])