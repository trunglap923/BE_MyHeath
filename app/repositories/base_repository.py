import logging
from contextlib import contextmanager
from app.core.database import get_connection

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self):
        pass

    @contextmanager
    def get_cursor(self):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            yield cur
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise e
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @contextmanager
    def get_connection(self):
        """Use this if you need full control over the connection (e.g. manual commit/rollback)"""
        conn = None
        try:
            conn = get_connection()
            yield conn
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise e
        finally:
            if conn:
                conn.close()
