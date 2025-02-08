# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - BACKUP SPOTIFY DATA         CREATED: 2024-10-10          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Backup_Spotify_Data.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import sqlite3
import unittest
from unittest import mock

import src.General_Spotify_Helpers as gsh
import tests.helpers.tester_helpers as thelp

from tests.helpers.mocked_spotipy import MockedSpotipyProxy
from src.features.Backup_Spotify_Data import BackupSpotifyData, replace_none, get_column_types

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Backup Spotify Data functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestBackupSpotifyData(unittest.TestCase):
    @mock.patch('src.General_Spotify_Helpers.SpotipyProxy', new=MockedSpotipyProxy)
    def setUp(self):
        self.spotify = gsh.GeneralSpotifyHelpers()
        self.backup = BackupSpotifyData(self.spotify, db_path=":memory:")
        self.backup.create_backup_data_db()

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
        self.backup.db_conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                data BLOB,
                value NUMERIC
            )""")
        self.assertEqual(get_column_types(self.backup.db_conn, "test_table"), [int, str, float, bytes, float])
    
        # Test for a column with an unsupported SQLite type.
        self.backup.db_conn.execute("""
            CREATE TABLE test_unsupported (
                id INTEGER PRIMARY KEY,
                custom_column CUSTOM_TYPE
            )""")
        self.assertEqual(get_column_types(self.backup.db_conn, "test_unsupported"), [int, str])

    def test_insert_many(self):
        # Test that inserting an empty list does nothing.
        self.backup.insert_many("artists", [])
        self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM artists").fetchone()[0], 0)
        
        # Test inserting with inconsistent row lengths.
        with self.assertRaises(sqlite3.ProgrammingError):
            self.backup.insert_many("artists", [("artist_1", "Artist One"), ("artist_2")])

        # Test inserting wrong data types into the columns.
        with self.assertRaises(ValueError):
            self.backup.insert_many("tracks", [("track_1", "Track One", "not_an_int", 0, 1)])

        # Test inserting into a table that doesn't exist.
        with self.assertRaises(sqlite3.OperationalError):
            self.backup.insert_many("nonexistent_table", [("value1", "value2")])
            
        # Test inserting data with fields that don't exist in the table.
        with self.assertRaises(sqlite3.OperationalError):
            self.backup.insert_many("artists", [("artist_1", "Artist One", "ExtraField")])
            
        # Test inserting data with foreign key that does not exist in the referenced table.
        with self.assertRaises(sqlite3.IntegrityError):
            self.backup.insert_many("albums_artists", [("album_1", "nonexistant_artist")])
        
        # Test inserting duplicate data.
        self.backup.insert_many("artists", [("artist_1", "Artist One")])
        res = self.backup.db_conn.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Attempt to insert duplicate data.
        self.backup.insert_many("artists", [("artist_1", "Artist Duplicate")])
        res = self.backup.db_conn.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Test batch_size with equal sets
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(10)]
        self.backup.db_conn.execute("DELETE FROM playlists")
        self.backup.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 10)
        # Test unequal batches
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
        self.backup.db_conn.execute("DELETE FROM playlists")
        self.backup.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)
        # Test inserting less than batch_size
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(1)]
        self.backup.db_conn.execute("DELETE FROM playlists")
        self.backup.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 1)
        # Test batch_size of 1
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(4)]
        self.backup.db_conn.execute("DELETE FROM playlists")
        self.backup.insert_many("playlists", test_data, batch_size=1)        
        self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 4)
        # Test batch_size of 0
        with self.assertRaises(ValueError):
            test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
            self.backup.db_conn.execute("DELETE FROM playlists")
            self.backup.insert_many("playlists", test_data, batch_size=0)        
            self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)

    def test_create_backup_data_db(self):
        # This method is just creating sqlite tables, nothing to unit test since we will fail the other unit tests if
        #   it is incorrect.
        assert True

    def test_add_followed_artists_to_db(self):
        thelp.create_env(self.spotify)
        # Test basic insert/ duplicate
        for _ in range(2):
            self.backup.add_followed_artists_to_db()
            self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM followed_artists").fetchone()[0]
                             , len(self.spotify.sp.user_artists))
            self.assertEqual(self.backup.db_conn.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
                             , len(self.spotify.sp.user_artists))

    def test_insert_tracks_into_db_from_playlist(self):
        thelp.create_env(self.spotify)
        
        tables = ["playlists", "artists", "albums", "tracks", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]

        # Test adding empty playlist doesn't add anything
        self.backup.insert_tracks_into_db_from_playlist("Pl001")
        table_lens = [self.backup.db_conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(any(table_lens), False)
        
        # Test we fail because playlist doesn't exist in 'playlists' table yet
        with self.assertRaises(sqlite3.IntegrityError):
            self.backup.insert_tracks_into_db_from_playlist("Pl002")
        
        # Test size of tables after we insert
        self.backup.insert_many("playlists", [("Pl002", "Fake name", "Fake desc")])   
        self.backup.insert_tracks_into_db_from_playlist("Pl002")
        
        # Test expected values from that playlist insertion
        expected_table_values = {
            'playlists': [('Pl002', 'Fake name', 'Fake desc')]
            , 'artists': [('Ar002', 'Fake Artist 2')]
            , 'albums': [('Al002', 'Fake Album 2', '0000-01-01')
                       , ('Al003', 'Fake Album 3', '0000-01-01')
                       , ('Al004', 'Fake Album 4', '0000-01-01')]
            , 'tracks': [('Tr002', 'Fake Track 2', 1, 0, 1)
                       , ('Tr003', 'Fake Track 3', 1, 0, 1)
                       , ('Tr004', 'Fake Track 4', 1, 0, 1)]
            , 'playlists_tracks': [('Pl002', 'Tr002'), ('Pl002', 'Tr003'), ('Pl002', 'Tr004')]
            , 'tracks_artists': [('Tr002', 'Ar002'), ('Tr003', 'Ar002'), ('Tr004', 'Ar002')]
            , 'tracks_albums': [('Tr002', 'Al002'), ('Tr003', 'Al003'), ('Tr004', 'Al004')]
            , 'albums_artists': [('Al002', 'Ar002'), ('Al003', 'Ar002'), ('Al004', 'Ar002')]
        }
        
        for key, value in expected_table_values.items():
            self.assertEqual(self.backup.db_conn.execute(f"SELECT * FROM '{key}'").fetchall(), value)

    def test_add_user_playlists_to_db(self):
        self.backup.add_user_playlists_to_db()
        
        tables = ["playlists", "artists", "albums", "tracks", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]

        # Test adding empty playlist doesn't add anything
        table_lens = [self.backup.db_conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(any(table_lens), False)
        
        thelp.create_env(self.spotify)
        self.backup.add_user_playlists_to_db()
        
        # Test adding empty playlist doesn't add anything
        table_lens = [self.backup.db_conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(table_lens, [4, 4, 7, 9, 11, 11, 9, 7])

    def test_backup_data(self):
        # We have unit tested all the individual methods called in this method so we don't need to test much here.
        thelp.create_env(self.spotify)
        self.backup.backup_data()
        tables = ["playlists", "artists", "albums", "tracks", "followed_artists", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]

        table_lens = [self.backup.db_conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(table_lens, [4, 5, 7, 9, 3, 11, 11, 9, 7])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════