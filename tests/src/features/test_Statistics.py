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
import uuid

from datetime import datetime
from unittest import mock

from tests.helpers.mocked_Settings import Test_Settings
from src.features.Statistics       import SpotifyStatistics

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Statistics functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Statistics.Settings', Test_Settings)
class TestStatistics(unittest.TestCase):

    @mock.patch('src.features.Statistics.Settings', Test_Settings)
    def setUp(self):
        Test_Settings.LISTENING_VAULT_DB = f"file:shared_memory_{uuid.uuid4()}?mode=memory&cache=shared"
        self.db_conn_owner = sqlite3.connect(Test_Settings.LISTENING_VAULT_DB, uri=True)
        self.addCleanup(self.db_conn_owner.close)
        
        self.statistics = SpotifyStatistics()
    
    def test_init(self):
        Test_Settings.LISTENING_VAULT_DB = ":memory:"
        statistics_default = SpotifyStatistics()
        self.assertEqual(statistics_default.logger, logging.getLogger())
        self.assertEqual(statistics_default.vault_db.db_path, ':memory:')
        
        statistics_logger = SpotifyStatistics(logger=logging.getLogger('custom_logger'))
        self.assertEqual(statistics_logger.logger, logging.getLogger('custom_logger'))
        self.assertEqual(statistics_logger.vault_db.db_path, ':memory:')
    
    def test_generate_featured_artists_list(self):
        Test_Settings.PLAYLIST_IDS_NOT_IN_ARTISTS = ['playlist_id_1', 'playlist_id_2']
        
        with self.statistics.vault_db.connect_db() as vault_db_conn:
            vault_db_conn.execute("INSERT INTO artists VALUES (?, ?)", ("artist_1", "Artist One"))
            vault_db_conn.execute("INSERT INTO artists VALUES (?, ?)", ("artist_2", "Artist Two"))
            vault_db_conn.execute("INSERT INTO artists VALUES (?, ?)", ("artist_3", "Artist Three"))
            vault_db_conn.execute("INSERT INTO artists VALUES (?, ?)", ("artist_4", "Artist Four"))
            vault_db_conn.execute("INSERT INTO artists VALUES (?, ?)", ("artist_5", "Artist Five"))
            vault_db_conn.execute("INSERT INTO followed_artists VALUES (?)", ("artist_1",))
            vault_db_conn.execute("INSERT INTO followed_artists VALUES (?)", ("artist_2",))
            vault_db_conn.execute("INSERT INTO playlists VALUES (?, ?, ?)", (Test_Settings.MASTER_MIX_ID, "Playlist One", "desc"))
            vault_db_conn.execute("INSERT INTO playlists VALUES (?, ?, ?)", ("playlist_id_1", "Playlist Two", "desc"))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_1", "Track One",   0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_2", "Track Two",   0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_3", "Track Three", 0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_4", "Track Four",  0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_5", "Track Five",  0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_6", "Track Six",   0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_7", "Track Local", 0, 1, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO tracks VALUES (?, ?, ?, ?, ?, ?, ?)", ("track_8", "Track Eight", 0, 0, 1, 1, 1))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_1"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_2"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_3"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_4"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_5"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_6"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_7"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", (Test_Settings.MASTER_MIX_ID, "track_8"))
            vault_db_conn.execute("INSERT INTO playlists_tracks VALUES (?, ?)", ("playlist_id_1", "track_3"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_1", "artist_1"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_1", "artist_2"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_2", "artist_1"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_3", "artist_3"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_4", "artist_1"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_4", "artist_3"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_5", "artist_1"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_5", "artist_4"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_6", "artist_2"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_6", "artist_3"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_7", "artist_1"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_7", "artist_3"))
            vault_db_conn.execute("INSERT INTO tracks_artists VALUES (?, ?)", ("track_8", "artist_5"))

        self.assertEqual(self.statistics.generate_featured_artists_list(20)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 3
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six', 'Track Local']}
                          , {'Artist Name': 'Artist Four', 'Number of Tracks': 1
                             , 'Unique Artists': ['Artist One']
                             , 'Track Names': ['Track Five']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(1)
                         , [{'Artist Name': 'Artist Three', 'Number of Tracks': 3
                             , 'Unique Artists': ['Artist One', 'Artist Two']
                             , 'Track Names': ['Track Four', 'Track Six', 'Track Local']}])
        
        self.assertEqual(self.statistics.generate_featured_artists_list(0), [])
        
    def test_generate_latest_artists(self):            
        # Test Empty Database
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)), [])
        
        # Test Single Artist
        with self.statistics.vault_db.connect_db() as vault_db_conn:
            vault_db_conn.execute("INSERT INTO tracks (id, name) VALUES (?, ?)", ("track1", "Song One"))
            vault_db_conn.execute("INSERT INTO artists (id, name) VALUES (?, ?)", ("artist1", "Artist One"))
            vault_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track1", "artist1"))
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2022-01-01 00:00:00", "track1"))
        
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2022, 12, 31))
                         , [{'Artist': 'Artist One', 'Listening Time (min)': 0.25}])
        
        # Test Multiple Artists Single Track Multiple Entries
        with self.statistics.vault_db.connect_db() as vault_db_conn:
            vault_db_conn.execute("INSERT INTO tracks (id, name) VALUES (?, ?)", ("track2", "Song Two"))
            vault_db_conn.execute("INSERT INTO artists (id, name) VALUES (?, ?)", ("artist2", "Artist Two"))
            vault_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track1", "artist2"))
            vault_db_conn.execute("INSERT INTO tracks_artists (id_track, id_artist) VALUES (?, ?)", ("track2", "artist2"))
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2022-01-02 00:00:00", "track1"))
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2022-01-10 00:00:00", "track2"))
        
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
        with self.statistics.vault_db.connect_db() as vault_db_conn:
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2023-01-02 00:00:00", "track1"))
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2023-01-02 00:00:01", "track1"))
            vault_db_conn.execute("INSERT INTO listening_sessions (time, id_track) VALUES (?, ?)", ("2023-01-10 00:00:00", "track1"))
        
        self.assertEqual(self.statistics.generate_latest_artists(datetime(2022, 1, 1)
                                                                 , end_date = datetime(2023, 2, 1))
                         , [{'Artist': 'Artist Two', 'Listening Time (min)': 1.5}
                          , {'Artist': 'Artist One', 'Listening Time (min)': 1.25}])


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
