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
import shutil
import sqlite3
import tempfile
import uuid
import unittest
from unittest import mock
from datetime import datetime, timedelta

import src.General_Spotify_Helpers  as gsh
import tests.helpers.tester_helpers as thelp
import tests.helpers.api_response_test_messages as artm

from tests.helpers.mocked_spotipy     import MockedSpotipyProxy
from src.helpers.Database_Helpers     import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Backup Spotify Data functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestDatabaseHelpers(unittest.TestCase):
    def setUp(self):
        self.unique_db_path = f"file:shared_memory_{uuid.uuid4()}?mode=memory&cache=shared"
        self.db_conn_owner = sqlite3.connect(self.unique_db_path, uri=True)
        self.addCleanup(self.db_conn_owner.close)
        
        self.dbh = DatabaseHelpers(self.unique_db_path)
        
    def setup_test_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            tmp_unit_test_db_path = tmp_file.name
        shutil.copy("tests/helpers/unit_test.db", tmp_unit_test_db_path)
        self.dbh.db_path = tmp_unit_test_db_path
        return sqlite3.connect(tmp_unit_test_db_path)
    
    def test_generate_create_statement(self):
        def normalize(statement):
            return ' '.join(statement.split())
        
        fields = {
            "id": "INTEGER PRIMARY KEY"
          , "name": "TEXT"
        }
        self.assertEqual(normalize(generate_create_statement("test_table", fields))
                         , normalize("CREATE TABLE IF NOT EXISTS test_table ( id INTEGER PRIMARY KEY, name TEXT );"))
        
        fields = {
            "key": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
          , "name": "BLOB"
          , "__constraints__": [ "UNIQUE (key)" ]
          , "__without_rowid__": True
        }
        self.assertEqual(normalize(generate_create_statement("test_table", fields))
                         , normalize("CREATE TABLE IF NOT EXISTS test_table ( key TIMESTAMP DEFAULT CURRENT_TIMESTAMP, name BLOB, UNIQUE (key) ) WITHOUT ROWID;"))
    
    def test_get_table_fields(self):
        schema = {
            "test_table": {
                "key": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
              , "name": "BLOB"
              , "__constraints__": [ "UNIQUE (key)" ]
              , "__without_rowid__": True
            },
            "test_table2": {
                "test2": "BLOB"
            }
        }
        with mock.patch("src.helpers.Database_Helpers.SCHEMA_FIELDS", schema):
            self.assertEqual(get_table_fields("test_table"), ["key", "name"])
            self.assertEqual(get_table_fields("test_table2"), ["test2"])
    
    def test_build_entries_from_tracks(self):
        artist_1 = thelp.create_artist("artist_1", "Artist 1")
        artist_2 = thelp.create_artist("artist_2", "Artist 2")
        track_1 = thelp.create_track("track_1", "Track 1"
                                     , thelp.create_album("album_1", "Album 1", [artist_1], "single")
                                     , [artist_1])
        track_2 = thelp.create_track("track_2", "Track 2"
                                     , thelp.create_album("album_2", "Album 2", [artist_1, artist_2], "album")
                                     , [artist_2])
        
        expected_output = {
            "tracks": [('track_1', 'Track 1', 1, False, True, 1, 1), ('track_2', 'Track 2', 1, False, True, 1, 1)],
            "albums": [('album_1', 'Album 1', '0000-01-01', 0), ('album_2', 'Album 2', '0000-01-01', 0)],
            "artists": [('artist_1', 'Artist 1'), ('artist_1', 'Artist 1'), ('artist_2', 'Artist 2'), ('artist_1', 'Artist 1'), ('artist_2', 'Artist 2')],
            "playlists_tracks": [],
            "tracks_artists": [('track_1', 'artist_1'), ('track_2', 'artist_2')],
            "tracks_albums": [('track_1', 'album_1'), ('track_2', 'album_2')],
            "albums_artists": [('album_1', 'artist_1'), ('album_2', 'artist_1'), ('album_2', 'artist_2')]
        }
        self.assertEqual(build_entries_from_tracks([track_1, track_2]), expected_output)
        
        expected_output["playlists_tracks"] = [("playlist_1", "track_1"), ("playlist_1", "track_2")]
        track_1["album"]['total_tracks'] = None
        self.assertEqual(build_entries_from_tracks([track_1, track_2], "playlist_1"), expected_output)
    
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
    
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # DatabaseHelpers ═════════════════════════════════════════════════════════════════════════════════════════════════
    # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    def test_init(self):
        self.assertEqual(self.unique_db_path, self.dbh.db_path)
        self.assertEqual(self.dbh.schema, DatabaseSchema.FULL)
        self.assertEqual(self.dbh.logger, logging.getLogger())
        
        with mock.patch("src.helpers.Database_Helpers.DatabaseHelpers.create_database") as mock_create_database:
            logger = mock.MagicMock()
            dbh_init = DatabaseHelpers("test", DatabaseSchema.SNAPSHOT, logger=logger)
            self.assertEqual(dbh_init.db_path, "test")
            self.assertEqual(dbh_init.schema, DatabaseSchema.SNAPSHOT)
            self.assertEqual(dbh_init.logger, logger)
            mock_create_database.assert_called_once()
    
    @mock.patch("src.helpers.Database_Helpers.sqlite3.connect")
    def test_connect_db(self, mock_connect):
        with self.dbh.connect_db() as db_conn:
            self.assertEqual(db_conn, mock_connect.return_value)
            mock_connect.assert_called_once_with(self.unique_db_path)
            db_conn.execute.assert_any_call("PRAGMA foreign_keys = ON;")
            db_conn.commit.assert_not_called()
        db_conn.commit.assert_called_once()
        db_conn.close.assert_called_once()
    
    @mock.patch("src.helpers.Database_Helpers.sqlite3.connect")
    def test_connect_db_readonly(self, mock_connect):
        self.dbh.db_path = "test_db"
        with self.dbh.connect_db_readonly() as db_conn:
            self.assertEqual(db_conn, mock_connect.return_value)
            mock_connect.assert_called_once_with(f'file:{self.dbh.db_path}?mode=ro', uri=True)
            db_conn.execute.assert_called_once_with("PRAGMA foreign_keys = ON;")
        db_conn.commit.assert_not_called()
        db_conn.close.assert_called_once()
        
        mock_connect.reset_mock()
        
        self.dbh.db_path = "test_db?"
        with self.dbh.connect_db_readonly() as db_conn:
            self.assertEqual(db_conn, mock_connect.return_value)
            mock_connect.assert_called_once_with(self.dbh.db_path, uri=True)
            db_conn.execute.assert_called_once_with("PRAGMA foreign_keys = ON;")
        db_conn.commit.assert_not_called()
        db_conn.close.assert_called_once()

    @mock.patch("src.helpers.Database_Helpers.sqlite3.connect")
    @mock.patch("src.helpers.Database_Helpers.generate_create_statement")
    def test_create_database(self, mock_generate_create_statement, mock_connect):
        schema = {
            "artists": [
                "artist_id INTEGER PRIMARY KEY",
                "name TEXT"
            ],
            "listening_sessions": [
                "track_id INTEGER PRIMARY KEY",
                "name TEXT"
            ]
        }
        mock_generate_create_statement.side_effect = ["create_artist_table", "create_listening_sessions_table"]
        with mock.patch("src.helpers.Database_Helpers.SCHEMA_FIELDS", schema):
            self.dbh.create_database()
            mock_connect.assert_called_once_with(self.unique_db_path)
            mock_generate_create_statement.assert_any_call("artists", schema["artists"])
            mock_generate_create_statement.assert_any_call("listening_sessions", schema["listening_sessions"])
            mock_connect.return_value.executescript.assert_called_once_with(
                "\n".join(["create_artist_table", "create_listening_sessions_table"]))
            
        mock_generate_create_statement.reset_mock()
        mock_connect.reset_mock()
            
        mock_generate_create_statement.side_effect = ["create_artist_table"]
        with mock.patch("src.helpers.Database_Helpers.SCHEMA_FIELDS", schema):
            self.dbh.schema = DatabaseSchema.SNAPSHOT
            self.dbh.create_database()
            mock_connect.assert_called_once_with(self.unique_db_path)
            mock_generate_create_statement.assert_any_call("artists", schema["artists"])
            mock_connect.return_value.executescript.assert_called_once_with(
                "\n".join(["create_artist_table"]))
    
    def test_insert_many(self):
        # Test that inserting an empty list does nothing.
        self.dbh.insert_many("artists", [])
        self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM artists").fetchone()[0], 0)
        
        # Test inserting with inconsistent row lengths.
        with self.assertRaises(sqlite3.ProgrammingError):
            self.dbh.insert_many("artists", [("artist_1", "Artist One"), ("artist_2")])

        # Test inserting wrong data types into the columns.
        with self.assertRaises(ValueError):
            self.dbh.insert_many("tracks", [("track_1", "Track One", "not_an_int", 0, 1)])

        # Test inserting into a table that doesn't exist.
        with self.assertRaises(sqlite3.OperationalError):
            self.dbh.insert_many("nonexistent_table", [("value1", "value2")])
            
        # Test inserting data with fields that don't exist in the table.
        with self.assertRaises(sqlite3.OperationalError):
            self.dbh.insert_many("artists", [("artist_1", "Artist One", "ExtraField")])
        
        # Test inserting data with foreign key that does not exist in the referenced table.
        with self.assertRaises(sqlite3.IntegrityError):
            self.dbh.insert_many("albums_artists", [("album_1", "nonexistant_artist")])
        
        # Test inserting duplicate data.
        self.dbh.insert_many("artists", [("artist_1", "Artist One")])
        res = self.db_conn_owner.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Attempt to insert duplicate data.
        self.dbh.insert_many("artists", [("artist_1", "Artist Duplicate")])
        res = self.db_conn_owner.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Test batch_size with equal sets
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(10)]
        self.db_conn_owner.execute("DELETE FROM playlists")
        self.db_conn_owner.commit()
        self.dbh.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 10)
        # Test unequal batches
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
        self.db_conn_owner.execute("DELETE FROM playlists")
        self.db_conn_owner.commit()
        self.dbh.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)
        # Test inserting less than batch_size
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(1)]
        self.db_conn_owner.execute("DELETE FROM playlists")
        self.db_conn_owner.commit()
        self.dbh.insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 1)
        # Test batch_size of 1
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(4)]
        self.db_conn_owner.execute("DELETE FROM playlists")
        self.db_conn_owner.commit()
        self.dbh.insert_many("playlists", test_data, batch_size=1)        
        self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 4)
        # Test batch_size of 0
        with self.assertRaises(ValueError):
            test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
            self.db_conn_owner.execute("DELETE FROM playlists")
            self.db_conn_owner.commit()
            self.dbh.insert_many("playlists", test_data, batch_size=0)        
            self.assertEqual(self.db_conn_owner.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)
    
    def test_increment_track_count(self):
        self.setup_test_db()
        
        # Test Incrementing Non-Existant Track
        with self.assertRaises(sqlite3.IntegrityError):
            self.dbh.increment_track_count("track_1")
        
        # Test Incrementing Existing Track With No Count
        self.dbh.increment_track_count("4RWzi7WNbW3H1Rr0aE9oPl")
        self.assertEqual(self.dbh.get_track_play_counts(["4RWzi7WNbW3H1Rr0aE9oPl"])[0]['play_count'], 1)
        
        # Test Incrementing Existing Track With Count
        self.dbh.increment_track_count("0B5QmtgAv1p6QnsdXM6u0H")
        self.assertEqual(self.dbh.get_track_play_counts(["0B5QmtgAv1p6QnsdXM6u0H"])[0]['play_count'], 11)
    
    def test_add_listening_session(self):
        self.setup_test_db()
        
        # Test Adding Listening Session With Non-Existant Track
        with self.assertRaises(sqlite3.IntegrityError):
            self.dbh.add_listening_session("track_1")
        
        # Test Adding Listening Session With Existing Track
        self.dbh.add_listening_session("0B5QmtgAv1p6QnsdXM6u0H")
        res = self.dbh.get_tracks_listened_in_date_range(datetime.now() - timedelta(days=1), datetime.now())
        self.assertEqual(res, [{"id": "0B5QmtgAv1p6QnsdXM6u0H", "track_count": 1}])
        
        self.dbh.add_listening_session("0B5QmtgAv1p6QnsdXM6u0H")
        self.dbh.add_listening_session("4RWzi7WNbW3H1Rr0aE9oPl")
        self.dbh.add_listening_session("0B5QmtgAv1p6QnsdXM6u0H")
        res = self.dbh.get_tracks_listened_in_date_range(datetime.now() - timedelta(days=1), datetime.now())
        self.assertEqual(res, [{"id": "0B5QmtgAv1p6QnsdXM6u0H", "track_count": 3}
                             , {"id": "4RWzi7WNbW3H1Rr0aE9oPl", "track_count": 1}])
    
    def test_conn_query_to_dict(self):
        self.setup_test_db()
        
        self.assertEqual(self.dbh._conn_query_to_dict("SELECT * FROM followed_artists")
                         , [{'id': '0MlOPi3zIDMVrfA9R04Fe3'}
                          , {'id': '0WQh63ofwTzWOy1ubiHMdk'}
                          , {'id': '0gadJ2b9A4SKsB1RFkBb66'}
                          , {'id': '5b0j3TTNSKCByBq4rHYKvG'}
                          , {'id': '6bmlMHgSheBauioMgKv2tn'}
                          , {'id': '72j6TTVpXqFzwAQ2BKIDmY'}])

    def test_get_row_by_id(self):
        self.setup_test_db()
        
        # Test Non-Existant Table
        with self.assertRaises(ValueError):
            self.dbh.get_row_by_id("table_1", "0B5QmtgAv1p6QnsdXM6u0H")
            
        # Test Non-Existant ID
        self.assertEqual(self.dbh.get_row_by_id("tracks", "track_1"), None)
        
        # Test Existant ID
        self.assertEqual(self.dbh.get_row_by_id("artists", "0MlOPi3zIDMVrfA9R04Fe3")
                         , {'id': '0MlOPi3zIDMVrfA9R04Fe3', 'name': 'American Authors'})
        
    def test_get_table_size(self):
        self.setup_test_db()
        
        # Test Non-Existant Table
        with self.assertRaises(ValueError):
            self.dbh.get_table_size("table_1")
            
        # Test Existant Table
        self.assertEqual(self.dbh.get_table_size("artists"), 13)
        self.assertEqual(self.dbh.get_table_size("followed_artists"), 6)
    
    def test_get_tracks_from_playlist(self):
        self.setup_test_db()
        
        # Test Empty Playlist
        self.assertEqual(self.dbh.get_tracks_from_playlist("playlist_1"), [])
        
        # Test Non-Empty Playlist
        expected_results = [
            {'id': '4RWzi7WNbW3H1Rr0aE9oPl', 'name': 'First Visit to K&A', 'duration_ms': 109586, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 3},
            {'id': '0U8KmbmtY2cPI0XpPSVPKu', 'name': 'Say Amen', 'duration_ms': 222586, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 2},
            {'id': 'local_track_Kiss Yourself Goodbye', 'name': 'Kiss Yourself Goodbye', 'duration_ms': 202000, 'is_local': 1, 'is_playable': 0, 'disc_number': 0, 'track_number': 0},
            {'id': '0B5QmtgAv1p6QnsdXM6u0H', 'name': 'Tell Me', 'duration_ms': 204937, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1},
            {'id': '1DdEuIq0H7adWm6TqFRLT5', 'name': 'bad at goodbyes', 'duration_ms': 130216, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1},
            {'id': '1iV5yIJimMf9pWfaDdf0UR', 'name': 'Dead Eyes', 'duration_ms': 219428, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1},
            {'id': '25yup6WYnPoITrfzhkBLmt', 'name': "I Can't Sleep", 'duration_ms': 152500, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 4},
            {'id': '0FmfRErQFP13h77PKWCawW', 'name': 'Bird in Flight', 'duration_ms': 175346, 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1}
        ]
        self.assertEqual(self.dbh.get_tracks_from_playlist("4UWdavQLwFVg3teF89KKEt"), expected_results)
    
    def test_get_track_artists(self):
        self.setup_test_db()
        
        # Test Non-Existant Track
        self.assertEqual(self.dbh.get_track_artists("track_1"), [])
        
        # Test Track With 1 Artist
        self.assertEqual(self.dbh.get_track_artists("0FmfRErQFP13h77PKWCawW"), [{"id": "0gadJ2b9A4SKsB1RFkBb66", "name": "Passenger"}])

        # Test Track With Multiple Artists
        self.assertEqual(self.dbh.get_track_artists("0U8KmbmtY2cPI0XpPSVPKu")
                         , [{"id": "0MlOPi3zIDMVrfA9R04Fe3", "name": "American Authors"},
                            {"id": "5gw5ANPCVcxU0maLiGRzzP", "name": "Billy Raffoul"}])
    
    def test_get_user_playlists(self):
        self.setup_test_db()
        self.assertEqual(self.dbh.get_user_playlists()
                         , [{"id": "4UWdavQLwFVg3teF89KKEt", "name": "Test Playlist", "description": "Test Playlist Description"}])
    
    def test_get_user_followed_artists(self):
        self.setup_test_db()
        self.assertEqual(self.dbh.get_user_followed_artists(), [{'id': '0MlOPi3zIDMVrfA9R04Fe3', 'name': 'American Authors'}
                                                              , {'id': '0WQh63ofwTzWOy1ubiHMdk', 'name': 'Peech.'}
                                                              , {'id': '0gadJ2b9A4SKsB1RFkBb66', 'name': 'Passenger'}
                                                              , {'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds'}
                                                              , {'id': '6bmlMHgSheBauioMgKv2tn', 'name': 'Powfu'}
                                                              , {'id': '72j6TTVpXqFzwAQ2BKIDmY', 'name': 'The All-American Rejects'}])
    
    def test_get_tracks_listened_in_date_range(self):
        self.setup_test_db()
        # Test No Tracks In Range
        self.assertEqual(self.dbh.get_tracks_listened_in_date_range(datetime(2023, 1, 15)
                                                         , datetime(2024, 1, 20)), [])
        # Test Tracks In Range
        self.assertEqual(self.dbh.get_tracks_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 45))
                         , [{'id': '0B5QmtgAv1p6QnsdXM6u0H', 'track_count': 2},
                            {'id': '0FmfRErQFP13h77PKWCawW', 'track_count': 1},
                            {'id': '1DdEuIq0H7adWm6TqFRLT5', 'track_count': 1}])
       
        
        # Test Tracks On Edge Of Range
        self.assertEqual(self.dbh.get_tracks_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 30))
                         , [{'id': '0B5QmtgAv1p6QnsdXM6u0H', 'track_count': 2},
                            {'id': '0FmfRErQFP13h77PKWCawW', 'track_count': 1},
                            {'id': '1DdEuIq0H7adWm6TqFRLT5', 'track_count': 1}])
        
        # Test Track Just Outside Of Range
        self.assertEqual(self.dbh.get_tracks_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 29))
                         , [{'id': '0B5QmtgAv1p6QnsdXM6u0H', 'track_count': 2},
                            {'id': '0FmfRErQFP13h77PKWCawW', 'track_count': 1}])
    
    def test_get_artists_listened_in_date_range(self):
        self.setup_test_db()
        
        # Test No Artists In Range
        self.assertEqual(self.dbh.get_artists_listened_in_date_range(datetime(2023, 1, 15)
                                                         , datetime(2024, 1, 20)), [])
        # Test Artists In Range
        self.assertEqual(self.dbh.get_artists_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 45))
                         , [{'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds', 'artist_count': 3}
                          , {'id': '0WQh63ofwTzWOy1ubiHMdk', 'name': 'Peech.', 'artist_count': 2}
                          , {'id': '4DSFmAOMwMqDVKIsPY0kqs', 'name': 'Sweezy', 'artist_count': 1}
                          , {'id': '0gadJ2b9A4SKsB1RFkBb66', 'name': 'Passenger', 'artist_count': 1}
                          , {'id': '4t3LO0Or2OMeBrH9Jy1bLY', 'name': 'Ezra', 'artist_count': 1}])
       
        
        # Test Artists On Edge Of Range
        self.assertEqual(self.dbh.get_artists_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 30))
                         , [{'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds', 'artist_count': 3}
                          , {'id': '0WQh63ofwTzWOy1ubiHMdk', 'name': 'Peech.', 'artist_count': 2}
                          , {'id': '4DSFmAOMwMqDVKIsPY0kqs', 'name': 'Sweezy', 'artist_count': 1}
                          , {'id': '0gadJ2b9A4SKsB1RFkBb66', 'name': 'Passenger', 'artist_count': 1}
                          , {'id': '4t3LO0Or2OMeBrH9Jy1bLY', 'name': 'Ezra', 'artist_count': 1}])
        
        # Test Artists Just Outside Of Range
        self.assertEqual(self.dbh.get_artists_listened_in_date_range(datetime(2025, 1, 15, 0, 0, 0)
                                                         , datetime(2025, 1, 15, 1, 14, 29))
                         , [{'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds', 'artist_count': 2}
                          , {'id': '0WQh63ofwTzWOy1ubiHMdk', 'name': 'Peech.', 'artist_count': 2}
                          , {'id': '0gadJ2b9A4SKsB1RFkBb66', 'name': 'Passenger', 'artist_count': 1}])

    def test_get_artists_appear_in_playlist(self):
        self.setup_test_db()
        
        # Test Non-Existant Playlist
        self.assertEqual(self.dbh.get_artists_appear_in_playlist("playlist_1"), [])
        
        # Test Playlist
        self.assertEqual(self.dbh.get_artists_appear_in_playlist("4UWdavQLwFVg3teF89KKEt")
                         , [{'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds', 'num_appearances': 3}
                            , {'id': '6bmlMHgSheBauioMgKv2tn', 'name': 'Powfu', 'num_appearances': 2}
                            , {'id': '0MlOPi3zIDMVrfA9R04Fe3', 'name': 'American Authors', 'num_appearances': 1}
                            , {'id': '0WQh63ofwTzWOy1ubiHMdk', 'name': 'Peech.', 'num_appearances': 1}
                            , {'id': '0gadJ2b9A4SKsB1RFkBb66', 'name': 'Passenger', 'num_appearances': 1}
                            , {'id': '1EowJ1WwkMzkCkRomFhui7', 'name': 'RADWIMPS', 'num_appearances': 1}
                            , {'id': '1bq8rqNnfrojn0OSAfeNXJ', 'name': 'Sarcastic Sounds', 'num_appearances': 1}
                            , {'id': '4DSFmAOMwMqDVKIsPY0kqs', 'name': 'Sweezy', 'num_appearances': 1}
                            , {'id': '4t3LO0Or2OMeBrH9Jy1bLY', 'name': 'Ezra', 'num_appearances': 1}
                            , {'id': '5gw5ANPCVcxU0maLiGRzzP', 'name': 'Billy Raffoul', 'num_appearances': 1}
                            , {'id': '6R29RU7eyQHSNc5kaHPWJn', 'name': 'Ouse', 'num_appearances': 1}
                            , {'id': 'local_track_Kiss Yourself Goodbye', 'name': 'The All-American Rejects', 'num_appearances': 1}])
    
    def test_get_artist_appears_with(self):
        self.setup_test_db()
        
        # Test Non-Existant Artist
        self.assertEqual(self.dbh.get_artist_appears_with("artist_1"), [])
        
        # Test Artist Who Only Appears With Themselves
        self.assertEqual(self.dbh.get_artist_appears_with("1EowJ1WwkMzkCkRomFhui7"), [])
        
        # Test Artist With One Collab
        self.assertEqual(self.dbh.get_artist_appears_with("5gw5ANPCVcxU0maLiGRzzP")
                         , [{'id': '0MlOPi3zIDMVrfA9R04Fe3', 'name': 'American Authors'}])
        
        # Test Artist With Multiple Collabs
        self.assertEqual(self.dbh.get_artist_appears_with("6bmlMHgSheBauioMgKv2tn")
                         , [{'id': '5b0j3TTNSKCByBq4rHYKvG', 'name': 'Promoting Sounds'}
                          , {'id': '6R29RU7eyQHSNc5kaHPWJn', 'name': 'Ouse'}
                          , {'id': '1bq8rqNnfrojn0OSAfeNXJ', 'name': 'Sarcastic Sounds'}])
    
    def test_get_artist_tracks(self):
        self.setup_test_db()
        
        # Test Non-Existant Track
        self.assertEqual(self.dbh.get_artist_tracks("artist_1"), [])
        
        # Test Artist With 1 Track
        self.assertEqual(self.dbh.get_artist_tracks("0gadJ2b9A4SKsB1RFkBb66")
                         , [{'id': '0FmfRErQFP13h77PKWCawW', 'name': 'Bird in Flight', 'duration_ms': 175346
                             , 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1}])
        
        # Test Artist With Multiple Tracks
        self.assertEqual(self.dbh.get_artist_tracks("6bmlMHgSheBauioMgKv2tn")
                         , [{'id': '1iV5yIJimMf9pWfaDdf0UR', 'name': 'Dead Eyes', 'duration_ms': 219428
                            , 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 1}
                          , {'id': '25yup6WYnPoITrfzhkBLmt', 'name': "I Can't Sleep", 'duration_ms': 152500
                            , 'is_local': 0, 'is_playable': 1, 'disc_number': 1, 'track_number': 4}])
    
    def test_get_track_play_counts(self):
        self.setup_test_db()
        
        # Test Empty List
        self.assertEqual(self.dbh.get_track_play_counts([]), [])
        
        # Test Non-Existant Track
        self.assertEqual(self.dbh.get_track_play_counts(["track_1"]), [])
        
        # Test Track With No Count
        self.assertEqual(self.dbh.get_track_play_counts(["4RWzi7WNbW3H1Rr0aE9oPl"]), [])
        
        # Test Single Track
        self.assertEqual(self.dbh.get_track_play_counts(["0B5QmtgAv1p6QnsdXM6u0H"])
                         , [{"id": "0B5QmtgAv1p6QnsdXM6u0H", "play_count": 10}])
        
        # Test Multiple Tracks
        self.assertEqual(self.dbh.get_track_play_counts(["0B5QmtgAv1p6QnsdXM6u0H", "0FmfRErQFP13h77PKWCawW", "N/A"])
                         , [{"id": "0B5QmtgAv1p6QnsdXM6u0H", "play_count": 10}
                          , {"id": "0FmfRErQFP13h77PKWCawW", "play_count": 2}])
        
        # Test Multiple Batches
        self.assertEqual(self.dbh.get_track_play_counts(["0B5QmtgAv1p6QnsdXM6u0H", "0FmfRErQFP13h77PKWCawW", "N/A"], batch_size=1)
                         , [{"id": "0B5QmtgAv1p6QnsdXM6u0H", "play_count": 10}
                          , {"id": "0FmfRErQFP13h77PKWCawW", "play_count": 2}])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════