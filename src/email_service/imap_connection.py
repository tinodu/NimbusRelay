"""
IMAP Connection Manager

Encapsulates IMAP connection management logic for establishing, maintaining,
and terminating connections to an IMAP server.
"""

import imaplib
from typing import Optional
from src.models.email_models import ConnectionConfig

class IMAPConnectionManager:
    """
    Manages the lifecycle of an IMAP connection, including connect, disconnect,
    connection status, and automatic reconnection.
    """

    def __init__(self) -> None:
        """
        Initialize the IMAPConnectionManager.
        """
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.config: Optional[ConnectionConfig] = None
        self._last_selected_folder: Optional[str] = None

    def connect(self, config: ConnectionConfig, ssl_context=None) -> bool:
        """
        Connect to the IMAP server using the provided configuration and optional SSL context.

        Args:
            config (ConnectionConfig): IMAP connection configuration.
            ssl_context: Optional SSL context.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            import ssl
            self.config = config
            if ssl_context is None:
                ssl_context = ssl.create_default_context()
            self.connection = imaplib.IMAP4_SSL(
                config.imap_server,
                config.imap_port,
                ssl_context=ssl_context
            )
            self.connection.login(config.imap_username, config.imap_password)
            self._last_selected_folder = None
            return True
        except Exception as e:
            print(f"IMAP connection failed: {e}")
            self.connection = None
            return False

    def disconnect(self) -> None:
        """
        Safely disconnect from the IMAP server.
        """
        if self.connection:
            try:
                try:
                    self.connection.close()
                except Exception:
                    pass
                self.connection.logout()
            except Exception:
                pass
            self.connection = None
            self._last_selected_folder = None

    def is_connected(self) -> bool:
        """
        Check if the IMAP connection is currently established.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.connection is not None

    def _ensure_connection(self) -> bool:
        """
        Ensure the IMAP connection is alive; reconnect if needed.

        Returns:
            bool: True if the connection is alive or successfully reconnected, False otherwise.
        """
        if self.connection is None or self.config is None:
            return False
        try:
            self.connection.noop()
            return True
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError):
            print("IMAP connection lost, attempting to reconnect...")
            self.disconnect()
            return self.connect(self.config)

    def get_connection(self):
        """
        Return the current IMAP connection (for compatibility with IMAPFolderService).
        """
        return self.connection