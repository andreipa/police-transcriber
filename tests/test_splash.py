#  Copyright (c) 2025. TechDev Andrade Ltda.
#  All rights reserved.
#  This source code is the intellectual property of TechDev Andrade Ltda and is intended for private use, research, or internal projects only. Redistribution and use in source or binary forms are not permitted without prior written permission.

import os
import unittest
from unittest.mock import patch, MagicMock

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from config import APP_NAME, SLOGAN_EN, VERSION
from gui.splash import SplashScreen


class TestSplashScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the QApplication instance required for PyQt tests."""
        cls.app = QApplication([])

    def setUp(self):
        """Set up the test environment."""
        self.splash_path = os.path.join("assets", "images", "splash.png")

    @patch("os.path.exists")
    @patch("PyQt5.QtGui.QPixmap")
    @patch("PyQt5.QtWidgets.QLabel")
    @patch("PyQt5.QtWidgets.QProgressBar")
    @patch("PyQt5.QtGui.QFont")
    @patch("PyQt5.QtWidgets.QVBoxLayout")
    def test_splash_screen_init_with_logo(self, mock_layout, mock_font, mock_progress_bar, mock_label, mock_pixmap, mock_exists):
        """Test SplashScreen initialization with logo present."""
        mock_exists.return_value = True
        mock_pixmap_instance = MagicMock()
        mock_scaled_pixmap = MagicMock()
        mock_pixmap.return_value = mock_pixmap_instance
        mock_pixmap_instance.scaledToWidth.return_value = mock_scaled_pixmap

        splash = SplashScreen()

        self.assertEqual(splash.windowTitle(), APP_NAME)
        self.assertEqual(splash.minimumSize().width(), 550)
        self.assertEqual(splash.minimumSize().height(), 500)
        self.assertTrue(splash.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(splash.windowFlags() & Qt.WindowStaysOnTopHint)

        mock_exists.assert_called_once_with(self.splash_path)
        mock_pixmap.assert_called_once_with(self.splash_path)
        mock_pixmap_instance.scaledToWidth.assert_called_once_with(300, Qt.SmoothTransformation)
        mock_label.return_value.setPixmap.assert_called_once_with(mock_scaled_pixmap)
        mock_label.return_value.setAlignment.assert_any_call(Qt.AlignCenter)

        mock_label.assert_any_call(APP_NAME)
        mock_label.assert_any_call(SLOGAN_EN)
        mock_label.assert_any_call(VERSION)
        mock_label.assert_any_call("Inicializando...")

        mock_progress_bar.assert_called_once()
        mock_progress_bar.return_value.setRange.assert_called_once_with(0, 100)
        mock_progress_bar.return_value.setValue.assert_called_once_with(0)
        mock_progress_bar.return_value.setTextVisible.assert_called_once_with(True)
        mock_progress_bar.return_value.setFormat.assert_called_once_with("%p%")
        mock_progress_bar.return_value.setFixedWidth.assert_called_once_with(300)

        mock_layout.assert_called_once()
        mock_layout.return_value.setAlignment.assert_called_once_with(Qt.AlignCenter)
        mock_layout.return_value.setSpacing.assert_called_once_with(10)
        mock_layout.return_value.setContentsMargins.assert_called_once_with(20, 20, 20, 20)
        mock_layout.return_value.addWidget.assert_called()
        mock_layout.return_value.addSpacerItem.assert_called()

    @patch("os.path.exists")
    @patch("PyQt5.QtWidgets.QLabel")
    @patch("PyQt5.QtWidgets.QProgressBar")
    @patch("PyQt5.QtGui.QFont")
    @patch("PyQt5.QtWidgets.QVBoxLayout")
    def test_splash_screen_init_no_logo(self, mock_layout, mock_font, mock_progress_bar, mock_label, mock_exists):
        """Test SplashScreen initialization when logo is missing."""
        mock_exists.return_value = False

        splash = SplashScreen()

        mock_exists.assert_called_once_with(self.splash_path)
        mock_label.return_value.setText.assert_any_call("Logo não encontrado")
        mock_label.return_value.setAlignment.assert_any_call(Qt.AlignCenter)

    @patch("PyQt5.QtCore.QCoreApplication.processEvents")
    def test_splash_screen_set_message(self, mock_process_events):
        """Test SplashScreen.setMessage updates the message label."""
        splash = SplashScreen()
        message = "Loading model..."
        splash.setMessage(message)
        splash.message_label.setText.assert_called_once_with(message)
        mock_process_events.assert_called_once_with(splash.QEventLoop.AllEvents, 100)

    @patch("PyQt5.QtCore.QCoreApplication.processEvents")
    def test_splash_screen_set_progress(self, mock_process_events):
        """Test SplashScreen.setProgress updates the progress bar."""
        splash = SplashScreen()
        value = 50
        splash.setProgress(value)
        splash.progress_bar.setValue.assert_called_once_with(value)
        mock_process_events.assert_called_once_with(splash.QEventLoop.AllEvents, 100)


if __name__ == "__main__":
    unittest.main()
