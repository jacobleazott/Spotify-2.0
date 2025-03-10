# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - WEEKLY REPORT               CREATED: 2025-02-28          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Weekly_Report.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import logging
import os
import unittest
import pytest

from unittest import mock
from datetime import datetime

from src.helpers.Settings           import Settings
from src.features.Weekly_Report     import *

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Weekly Report functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class TestWeeklyReport(unittest.TestCase):
    
    def setUp(self):
        self.mocked_sanity_tester = mock.MagicMock()
        self.mocked_logger = mock.MagicMock()
        self.weekly_report = WeeklyReport(self.mocked_sanity_tester, logger=self.mocked_logger)
    
    def test_init(self):
        self.assertIs(self.mocked_sanity_tester, self.weekly_report.sanity_tester)
        self.assertIs(self.mocked_logger, self.weekly_report.logger)
        default_logger_weekly_report = WeeklyReport(self.mocked_sanity_tester)
        self.assertIs(logging.getLogger(), default_logger_weekly_report.logger)

    @mock.patch('smtplib.SMTP_SSL')
    def test_send_email(self, mock_smtp_ssl):
        os.environ['GMAIL_TOKEN'] = 'tokeny token token'
        with mock.patch('builtins.open', mock.mock_open(read_data=b'test image data')) as mock_file:
            mock_smtp_server = mock.MagicMock()
            mock_smtp_ssl.return_value.__enter__.return_value = mock_smtp_server
            mock_file.return_value.__enter__.return_value.read.side_effect = lambda: b'\x89PNG\r\n\x1a\n'
            
            self.weekly_report._send_email('test subject', 'test body')
            
            mock_smtp_ssl.assert_called_once_with('smtp.gmail.com', 465)
            mock_smtp_server.login.assert_called_once_with(Settings.SENDER_EMAIL, os.environ['GMAIL_TOKEN'])
            mock_smtp_server.sendmail.assert_called_once_with(Settings.SENDER_EMAIL, Settings.RECIPIENT_EMAIL, mock.ANY)

    @mock.patch('src.features.Weekly_Report.plt')
    @mock.patch('sqlite3.connect')
    def test_gen_playback_graph(self, mock_connect, mock_plt):
        mock_conn = mock_connect.return_value
        mock_conn.execute.return_value = mock.Mock(fetchall=mock.Mock(return_value=[1, 2, 3]))
        mock_plt.subplots.return_value = (mock.MagicMock(), mock.MagicMock())
        
        self.weekly_report._gen_playback_graph()
        # Test DB Conn Connection
        mock_connect.assert_called_once_with(Settings.LISTENING_DB)
        mock_conn.execute.assert_called()
        mock_conn.close.assert_called_once()
        # Test Plot Creation
        mock_plt.subplots.assert_called_once()
        mock_plt.bar.assert_called_once()
        mock_plt.ylabel.assert_called_once()
        mock_plt.title.assert_called_once()
        mock_plt.title.plot()
        mock_plt.savefig.assert_called_once_with(self.weekly_report.LISTENING_DATA_PLOT_FILEPATH)
    
    @mock.patch('src.features.Weekly_Report.datetime')
    def test_gen_average_for_past_month(self, mock_datetime):
        listening_conn = mock.Mock()
        # Set To A Saturday 
        mock_datetime.today.return_value = datetime(2025, 1, 5)
        
        # Test One Week
        listening_conn.execute.return_value = mock.Mock(fetchall=mock.Mock(return_value=[1] * 200))
        days_back = 7
        expected_output = [200 * 15 / 3600] * 7
        self.assertEqual(self.weekly_report._gen_average_for_past_month(listening_conn, days_back), expected_output)
        
        # Test Incomplete Weeks
        days_back = 25
        expected_output = [200 * 15 / 3600] * 7
        self.assertEqual(self.weekly_report._gen_average_for_past_month(listening_conn, days_back), expected_output)
        
        # Test Averaging
        listening_conn.execute.return_value.fetchall.side_effect = [
            [1] * 100, [1] * 100, [1] * 100, [1] * 100, [1] * 100, [1] * 100, [1] * 100, 
            [1] * 200, [1] * 300, [1] * 400, [1] * 500, [1] * 600, [1] * 700, [1] * 800
        ]
        days_back = 14
        expected_output = [300 * 15 / 3600 / 2, 400 * 15 / 3600 / 2, 500 * 15 / 3600 / 2, 600 * 15 / 3600 / 2
                           , 700 * 15 / 3600 / 2, 800 * 15 / 3600 / 2, 900 * 15 / 3600 / 2]
        self.assertEqual(self.weekly_report._gen_average_for_past_month(listening_conn, days_back), expected_output)

        # Test Incomplete Averaging
        listening_conn.execute.return_value.fetchall.side_effect = [
            [1] * 99, [1] * 50, [1] * 100, [1] * 100, [1] * 100, [1] * 100, [1] * 1
        ]
        days_back = 7
        expected_output = [0, 0, 100 * 15 / 3600, 100 * 15 / 3600, 100 * 15 / 3600, 100 * 15 / 3600, 0]
        self.assertEqual(self.weekly_report._gen_average_for_past_month(listening_conn, days_back), expected_output)
        
        # Test Missing Data
        listening_conn.execute.return_value = mock.Mock(fetchall=mock.Mock(return_value=[]))
        days_back = 1000
        expected_output = [0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(self.weekly_report._gen_average_for_past_month(listening_conn, days_back), expected_output)

    def test_gen_weekly_report(self):
        with mock.patch.object(self.weekly_report, '_gen_playback_graph')\
             , mock.patch.object(self.weekly_report, '_send_email') \
             , mock.patch('src.features.Weekly_Report.generate_dynamic_table'):

            self.weekly_report.gen_weekly_report()
            self.weekly_report._gen_playback_graph.assert_called_once()
            self.weekly_report._send_email.assert_called_once()
    
    def test_flatten_row(self):
        row = {'A': 1, 'B': 2}
        expected = {'A': 1, 'B': 2}
        self.assertEqual(flatten_row(row), expected)
        
        row = {'A': [{'B': 1}, {'C': 2}]}
        expected = {'A': [{'A B': 1}, {'A C': 2}]}
        self.assertEqual(flatten_row(row), expected)
        
        row = {'A': {'B': 1, 'C': {'D': [2, 3]}}}
        expected = {'A B': 1, 'A C D': '2, 3'}
        self.assertEqual(flatten_row(row), expected)
        
        row = {'A': [1, 2]}
        expected = {'A': '1, 2'}
        self.assertEqual(flatten_row(row), expected)
    
    def test_expand_rows(self):
        data = [
            {'A': 1, 'B': [{'C': 2}, {'C': 3}]}
          , {'A': 4, 'B': [{'C': 5}, {'C': 6}]}
        ]
        expected = [
            {'A': 1, 'B C': 2}
          , {'A': 1, 'B C': 3}
          , {'A': 4, 'B C': 5}
          , {'A': 4, 'B C': 6}
        ]
        self.assertEqual(expand_rows(data), expected)
        
        data = [
            {'A': 1, 'B': 2}
          , {'A': 4, 'B': 5}
        ]
        expected = [
            {'A': 1, 'B': 2}
          , {'A': 4, 'B': 5}
        ]
        self.assertEqual(expand_rows(data), expected)

    def test_merge_duplicates(self):
        data = [{'A': 1, 'B': 2}, {'A': 1, 'B': 3}, {'A': 2, 'B': 3}]
        preserve_keys = ['A', 'B']
        expected = [{'A': 1, 'B': 2}, {'A': '', 'B': 3}, {'A': 2, 'B': ''}]
        self.assertEqual(merge_duplicates(data, preserve_keys), expected)
        
        data = [{'A': 1, 'B': 2}, {'A': 2, 'B': 3}, {'A': 3, 'B': 3}]
        preserve_keys = ['A']
        expected = [{'A': 1, 'B': 2}, {'A': 2, 'B': 3}, {'A': 3, 'B': 3}]
        self.assertEqual(merge_duplicates(data, preserve_keys), expected)

        data = []
        preserve_keys = ['A', 'B']
        expected = []
        self.assertEqual(merge_duplicates(data, preserve_keys), expected)
    
    def test_generate_dynamic_table(self):
        pass


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════