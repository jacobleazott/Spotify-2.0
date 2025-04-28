# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - STATISTICS                  CREATED: 2025-03-14          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Statistics.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import sqlite3
import unittest

from datetime import datetime
from unittest import mock

from tests.helpers.mocked_Settings import Test_Settings
from src.features.Statistics       import SpotifyStatistics

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Statistics functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Statistics.Settings', Test_Settings)
class TestStatistics(unittest.TestCase):
    
    #     @mock.patch('src.Spotify_Features.DriveUploader')
    # @mock.patch('src.Spotify_Features.glob')
    # @mock.patch('os.path.getmtime')
    # def test_latest_backup(self, mock_getmtime, mock_glob, MockDriveUploader):
    #     # Define your mocked file paths
    #     mock_glob.return_value = ['/path/to/file1.txt'
    #                               , '/path/to/file2.txt'
    #                               , '/path/to/file3.txt']
    
    @mock.patch('src.features.Statistics.glob')
    @mock.patch('os.path.getmtime')
    @mock.patch('src.features.Statistics.DatabaseHelpers')
    def setUp(self, mock_dbh, mock_getmtime, mock_glob):
        mock_glob.return_value = ['/path/to/file1.txt']
        self.statistics = SpotifyStatistics()
        self.mock_dbh = mock.MagicMock()
        self.statistics.dbh = self.mock_dbh
    
    @mock.patch('src.features.Statistics.glob')
    @mock.patch('os.path.getmtime')
    @mock.patch('src.features.Statistics.DatabaseHelpers')
    def test_init(self, mock_dbh, mock_getmtime, mock_glob):
        mock_glob.return_value = ['/path/to/file1.txt'
                                , '/path/to/file2.txt'
                                , '/path/to/file3.txt']
        
        mock_getmtime.side_effect = lambda path: {'/path/to/file1.txt': 100
                                                  , '/path/to/file2.txt': 200
                                                  , '/path/to/file3.txt': 300}[path]
        
        statistics_default = SpotifyStatistics()
        self.assertEqual(statistics_default.logger, logging.getLogger())
        self.assertEqual(statistics_default.dbh, mock_dbh.return_value)
        self.assertEqual(statistics_default.latest_backup, '/path/to/file3.txt')
        
        statistics_logger = SpotifyStatistics(logger=logging.getLogger('custom_logger'))
        self.assertEqual(statistics_logger.logger, logging.getLogger('custom_logger'))
    
    def test_generate_featured_artists_list(self):
        Test_Settings.PLAYLIST_IDS_NOT_IN_ARTISTS = ['playlist_id_1', 'playlist_id_2']
        self.mock_dbh.db_get_user_followed_artists.return_value = [{'id': 'artist_1'}, {'id': 'artist_2'}]
        
        self.mock_dbh.db_get_tracks_from_playlist.side_effect = lambda playlist_id: {
            Test_Settings.MASTER_MIX_ID: [{'id': 'track_1', 'name': 'Track One', 'is_local': False}
                                          , {'id': 'track_2', 'name': 'Track Two', 'is_local': False}
                                          , {'id': 'track_3', 'name': 'Track Three', 'is_local': False}
                                          , {'id': 'track_4', 'name': 'Track Four', 'is_local': False}
                                          , {'id': 'track_5', 'name': 'Track Five', 'is_local': False}
                                          , {'id': 'track_6', 'name': 'Track Six', 'is_local': False}
                                          , {'id': 'track_7', 'name': 'Track Seven', 'is_local': True}]
            , 'playlist_id_1': [{'id': 'track_3'}]
        }.get(playlist_id, [])
        
        self.mock_dbh.db_get_track_artists.side_effect = lambda track_id: {
            'track_1': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_2', 'name': 'Artist Two'}]
            , 'track_2': [{'id': 'artist_1', 'name': 'Artist One'}]
            , 'track_3': [{'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_4': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_5': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_4', 'name': 'Artist Four'}]
            , 'track_6': [{'id': 'artist_2', 'name': 'Artist Two'}, {'id': 'artist_3', 'name': 'Artist Three'}]
            , 'track_7': [{'id': 'artist_1', 'name': 'Artist One'}, {'id': 'artist_3', 'name': 'Artist Three'}]
        }.get(track_id, [])

        print(self.statistics.generate_featured_artists_list(2))

        self.assertEqual(self.statistics.generate_featured_artists_list(2)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 2
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six']}
                          , {'Artist Name': 'Artist Four', 'Number of Tracks': 1
                             , 'Unique Artists': ['Artist One']
                             , 'Track Names': ['Track Five']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(1)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 2
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(0), [])
        
    def test_generate_latest_artists(self):
        # Setup Databases and Tables
        Test_Settings.LISTENING_VAULT_DB = "file:shared_memory?mode=memory&cache=shared"
        listening_conn = sqlite3.connect(Test_Settings.LISTENING_VAULT_DB)
        
        listening_conn.execute(f"""
            CREATE TABLE IF NOT EXISTS 'listening_sessions' (
                track_id TEXT,
                time TEXT
            );
        """)
        listening_conn.commit()
        
        backup_db_conn = sqlite3.connect(":memory:")
        self.mock_dbh.backup_db_conn = backup_db_conn
        
        backup_db_conn.executescript("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                name TEXT
            ) WITHOUT ROWID;
            
            CREATE TABLE IF NOT EXISTS artists (
                id TEXT PRIMARY KEY,
                name TEXT
            ) WITHOUT ROWID;
            
            CREATE TABLE IF NOT EXISTS tracks_artists (
                id_track text REFERENCES tracks(id),
                id_artist text REFERENCES artists(id),
                UNIQUE(id_track, id_artist)
            );
        """)
        backup_db_conn.commit()
        
        # Test Empty Database
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)), [])
        
        # Test Single Artist
        backup_db_conn.execute("INSERT INTO tracks (id, name) VALUES (?, ?)", ("track1", "Song One"))
        backup_db_conn.execute("INSERT INTO artists (id, name) VALUES (?, ?)", ("artist1", "Artist One"))
        backup_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track1", "artist1"))
        backup_db_conn.commit()
        
        listening_conn.execute("INSERT INTO '2022' (track_id, time) VALUES (?, ?)", ("track1", "2022-01-01 00:00:00"))
        listening_conn.commit()
        
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2022, 12, 31))
                         , [{'Artist': 'Artist One', 'Listening Time (min)': 0.25}])
        
        # Test Multiple Artists Single Track Multiple Entries
        backup_db_conn.execute("INSERT INTO tracks (id, name) VALUES (?, ?)", ("track2", "Song Two"))
        backup_db_conn.execute("INSERT INTO artists (id, name) VALUES (?, ?)", ("artist2", "Artist Two"))
        backup_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track1", "artist2"))
        backup_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track2", "artist2"))
        backup_db_conn.commit()
        
        listening_conn.execute("INSERT INTO '2022' (track_id, time) VALUES (?, ?)", ("track1", "2022-01-02 00:00:00"))
        listening_conn.execute("INSERT INTO '2022' (track_id, time) VALUES (?, ?)", ("track2", "2022-01-10 00:00:00"))
        listening_conn.commit()
        
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2022, 12, 31))
                         , [{'Artist': 'Artist Two', 'Listening Time (min)': 0.75}
                          , {'Artist': 'Artist One', 'Listening Time (min)': 0.5}])
        
        # Test 'num_artists' Change
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2022, 12, 31)
                                                                 , num_artists=1)
                         , [{'Artist': 'Artist Two', 'Listening Time (min)': 0.75}])
        
        # Test 'num_artists' Change
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2022, 12, 31)
                                                                 , num_artists=0)
                         , [])
        
        # Test Out of Range Date
        self.assertCountEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                      , end_date = datetime(2022, 1, 5))
                         , [{'Artist': 'Artist Two', 'Listening Time (min)': 0.5}
                          , {'Artist': 'Artist One', 'Listening Time (min)': 0.5}])
        
        # Test Multiple Years
        listening_conn.execute("INSERT INTO '2023' (track_id, time) VALUES (?, ?)", ("track1", "2023-01-02 00:00:00"))
        listening_conn.execute("INSERT INTO '2023' (track_id, time) VALUES (?, ?)", ("track1", "2023-01-02 00:00:01"))
        listening_conn.execute("INSERT INTO '2023' (track_id, time) VALUES (?, ?)", ("track1", "2023-01-10 00:00:00"))
        listening_conn.commit()
        
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2023, 2, 1))
                         , [{'Artist': 'Artist Two', 'Listening Time (min)': 1.5}
                          , {'Artist': 'Artist One', 'Listening Time (min)': 1.25}])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
