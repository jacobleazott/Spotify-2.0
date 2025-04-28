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
import uuid
import unittest
from unittest import mock

import src.General_Spotify_Helpers  as gsh
import tests.helpers.tester_helpers as thelp

from tests.helpers.mocked_spotipy     import MockedSpotipyProxy
from src.features.Backup_Spotify_Data import BackupSpotifyData

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Backup Spotify Data functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestBackupSpotifyData(unittest.TestCase):
    @mock.patch('src.General_Spotify_Helpers.SpotipyProxy', new=MockedSpotipyProxy)
    def setUp(self):
        self.spotify = gsh.GeneralSpotifyHelpers()
        self.unique_db_name = f"file:shared_memory_{uuid.uuid4()}?mode=memory&cache=shared"
        self.conn = sqlite3.connect(self.unique_db_name, uri=True)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.backup = BackupSpotifyData(self.spotify, db_path=self.unique_db_name)
        self.backup._create_backup_data_db()
    
    def tearDown(self):
        self.conn.close()

    @mock.patch("sqlite3.connect")
    def test_connect_db_success(self, mock_connect):
        """Test that the context manager sets up the database connection properly."""
        mock_conn = mock.MagicMock()
        mock_conn = mock.MagicMock()
        mock_connect.return_value = mock_conn
        
        with self.backup.connect_db() as conn:
            conn.execute("SELECT 1")
        
        # Assertions
        mock_connect.assert_called_once_with(self.unique_db_name)  # Ensures db connection was attempted
        mock_conn.execute.assert_any_call("PRAGMA foreign_keys = ON;")  # Ensures PRAGMA was set
        mock_conn.commit.assert_called_once()  # Ensures commit was called
        mock_conn.close.assert_called_once()  # Ensures connection was closed
    
    def test_insert_many(self):
        # Test that inserting an empty list does nothing.
        self.backup._insert_many("artists", [])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM artists").fetchone()[0], 0)
        
        # Test inserting with inconsistent row lengths.
        with self.assertRaises(sqlite3.ProgrammingError):
            self.backup._insert_many("artists", [("artist_1", "Artist One"), ("artist_2")])

        # Test inserting wrong data types into the columns.
        with self.assertRaises(ValueError):
            self.backup._insert_many("tracks", [("track_1", "Track One", "not_an_int", 0, 1)])

        # Test inserting into a table that doesn't exist.
        with self.assertRaises(sqlite3.OperationalError):
            self.backup._insert_many("nonexistent_table", [("value1", "value2")])
            
        # Test inserting data with fields that don't exist in the table.
        with self.assertRaises(sqlite3.OperationalError):
            self.backup._insert_many("artists", [("artist_1", "Artist One", "ExtraField")])
        
        # Test inserting data with foreign key that does not exist in the referenced table.
        with self.assertRaises(sqlite3.IntegrityError):
            self.backup._insert_many("albums_artists", [("album_1", "nonexistant_artist")])
        
        # Test inserting duplicate data.
        self.backup._insert_many("artists", [("artist_1", "Artist One")])
        res = self.conn.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Attempt to insert duplicate data.
        self.backup._insert_many("artists", [("artist_1", "Artist Duplicate")])
        res = self.conn.execute("SELECT COUNT(*) FROM artists WHERE id = ?", ("artist_1",)).fetchone()[0]
        self.assertEqual(res, 1)
        
        # Test batch_size with equal sets
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(10)]
        self.conn.execute("DELETE FROM playlists")
        self.conn.commit()
        self.backup._insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 10)
        # Test unequal batches
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
        self.conn.execute("DELETE FROM playlists")
        self.conn.commit()
        self.backup._insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)
        # Test inserting less than batch_size
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(1)]
        self.conn.execute("DELETE FROM playlists")
        self.conn.commit()
        self.backup._insert_many("playlists", test_data, batch_size=5)        
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 1)
        # Test batch_size of 1
        test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(4)]
        self.conn.execute("DELETE FROM playlists")
        self.conn.commit()
        self.backup._insert_many("playlists", test_data, batch_size=1)        
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 4)
        # Test batch_size of 0
        with self.assertRaises(ValueError):
            test_data = [(f"playlist_{i}", f"Playlist {i}", f"Desc {i}") for i in range(17)]
            self.conn.execute("DELETE FROM playlists")
            self.conn.commit()
            self.backup._insert_many("playlists", test_data, batch_size=0)        
            self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM playlists").fetchone()[0], 17)
    
    def test_create_backup_data_db(self):
        # This method is just creating sqlite tables, nothing to unit test since we will fail the other unit tests if
        #   it is incorrect.
        assert True
    
    def test_add_followed_artists_to_db(self):
        thelp.create_env(self.spotify)
        # Test basic insert/ duplicate
        for _ in range(2):
            self.backup._add_followed_artists_to_db()
            self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM followed_artists").fetchone()[0]
                             , len(self.spotify.sp.user_artists))
            self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
                             , len(self.spotify.sp.user_artists))
    
    def test_insert_tracks_into_db_from_playlist(self):
        thelp.create_env(self.spotify)
        
        tables = ["playlists", "artists", "albums", "tracks", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]
        
        # Test adding empty playlist doesn't add anything
        self.backup._insert_tracks_into_db_from_playlist("Pl001")
        table_lens = [self.conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(any(table_lens), False)
        
        # Test we fail because playlist doesn't exist in 'playlists' table yet
        with self.assertRaises(sqlite3.IntegrityError):
            self.backup._insert_tracks_into_db_from_playlist("Pl002")
        
        # Test size of tables after we insert
        self.backup._insert_many("playlists", [("Pl002", "Fake name", "Fake desc")])   
        self.backup._insert_tracks_into_db_from_playlist("Pl002")
        
        # Test expected values from that playlist insertion
        expected_table_values = {
            'playlists': [('Pl002', 'Fake name', 'Fake desc')]
            , 'artists': [('Ar002', 'Fake Artist 2')]
            , 'albums': [('Al002', 'Fake Album 2', '0000-01-01')
                       , ('Al003', 'Fake Album 3', '0000-01-01')
                       , ('Al004', 'Fake Album 4', '0000-01-01')]
            , 'tracks': [('Tr002', 'Fake Track 2', 1, 0, 0)
                       , ('Tr003', 'Fake Track 3', 1, 0, 0)
                       , ('Tr004', 'Fake Track 4', 1, 0, 1)]
            , 'playlists_tracks': [('Pl002', 'Tr002'), ('Pl002', 'Tr003'), ('Pl002', 'Tr004')]
            , 'tracks_artists': [('Tr002', 'Ar002'), ('Tr003', 'Ar002'), ('Tr004', 'Ar002')]
            , 'tracks_albums': [('Tr002', 'Al002'), ('Tr003', 'Al003'), ('Tr004', 'Al004')]
            , 'albums_artists': [('Al002', 'Ar002'), ('Al003', 'Ar002'), ('Al004', 'Ar002')]
        }
        
        for key, value in expected_table_values.items():
            self.assertEqual(self.conn.execute(f"SELECT * FROM '{key}'").fetchall(), value)
            
    def test_insert_tracks_into_db_from_playlist_duplicates(self):
        # Test local tracks and duplicates
        thelp.create_env(self.spotify)
        self.backup._insert_many("playlists", [("Pl004", "Fake name", "Fake desc")])   
        self.backup._insert_tracks_into_db_from_playlist("Pl004")
        self.assertEqual(self.conn.execute("SELECT * FROM tracks").fetchall()
            , [  ('Tr001', 'Fake Track 1', 1, 0, 0)
               , ('local_track_Fake Local Track 1', 'Fake Local Track 1', 1, 1, 0)])

    def test_add_user_playlists_to_db(self):
        self.backup._add_user_playlists_to_db()
        
        tables = ["playlists", "artists", "albums", "tracks", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]

        # Test adding empty playlist doesn't add anything
        table_lens = [self.conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(any(table_lens), False)
        
        thelp.create_env(self.spotify)
        self.backup._add_user_playlists_to_db()
        
        # Test adding empty playlist doesn't add anything
        table_lens = [self.conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(table_lens, [4, 4, 7, 9, 11, 11, 9, 7])

    def test_backup_data(self):
        # We have unit tested all the individual methods called in this method so we don't need to test much here.
        thelp.create_env(self.spotify)
        self.backup.backup_data()
        tables = ["playlists", "artists", "albums", "tracks", "followed_artists", "playlists_tracks"
                  , "tracks_artists", "tracks_albums", "albums_artists"]

        table_lens = [self.conn.execute(f"SELECT COUNT(*) FROM '{table}'").fetchone()[0] for table in tables]
        self.assertEqual(table_lens, [4, 5, 7, 9, 3, 11, 11, 9, 7])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════