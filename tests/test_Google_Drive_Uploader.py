# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                             ╠══╣
# ║  ║    UNIT TESTS - GOOGLE DRIVE UPLOADER       CREATED: 2024-10-10          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                             ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ════════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Unit tests for all functionality out of 'Google_Drive_Uploader.py'.
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import unittest
from unittest import mock

from src.features.Google_Drive_Uploader import DriveUploader
from tests.helpers.mocked_Settings      import Test_Settings

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Unit test collection for all Google Drive Uploader functionality.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@mock.patch('src.features.Google_Drive_Uploader.Settings', Test_Settings)
class TestDriveUploader(unittest.TestCase):
    @mock.patch('src.features.Google_Drive_Uploader.GoogleAuth')  # Replace with your actual module name
    @mock.patch('src.features.Google_Drive_Uploader.GoogleDrive')
    def test_authorize(self, mock_drive, mock_gauth):
        mock_instance = mock_gauth.return_value
        
        # Test New Credentials
        mock_instance.credentials = None  # Simulate missing credentials.
        uploader = DriveUploader()
        mock_instance.CommandLineAuth.assert_called_once()
        mock_instance.SaveCredentialsFile.assert_called_once_with(Test_Settings.DRIVE_TOKEN_FILE)
        self.assertIsNotNone(uploader.drive)

        # Test Refresh Credentials
        mock_instance.reset_mock()
        mock_instance.credentials = mock.Mock()  # Simulate existing credentials.
        mock_instance.access_token_expired = True  # Simulate expired token.
        uploader = DriveUploader()
        mock_instance.Refresh.assert_called_once()
        mock_instance.SaveCredentialsFile.assert_called_once_with(Test_Settings.DRIVE_TOKEN_FILE)
        self.assertIsNotNone(uploader.drive)

        # Test Existing Credentials
        mock_instance.reset_mock()
        mock_instance.credentials = mock.Mock()  # Simulate existing credentials.
        mock_instance.access_token_expired = False  # Token is valid.
        uploader = DriveUploader()
        mock_instance.Authorize.assert_called_once()
        mock_instance.SaveCredentialsFile.assert_not_called()
        self.assertIsNotNone(uploader.drive)

    @mock.patch('src.features.Google_Drive_Uploader.GoogleDrive')
    def test_upload_file(self, mock_drive):
        mock_instance = mock_drive.return_value
        mock_instance.CreateFile.return_value = mock.Mock()
        DriveUploader.authorize = mock.MagicMock() # We don't want to trigger this here.
        DriveUploader.drive = mock_instance # Need to override drive so we can assert CreateFile is called.

        test_file_path = 'test_file.txt'
        
        DriveUploader().upload_file(test_file_path)

        mock_instance.CreateFile.assert_called_once_with({
            'title': 'test_file.txt', 
            'parents': [{'id': Test_Settings.DRIVE_FOLDER_ID}]
        })

        gfile = mock_instance.CreateFile.return_value
        gfile.SetContentFile.assert_called_once_with(test_file_path)
        gfile.Upload.assert_called_once()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════