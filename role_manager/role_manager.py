import logging
from ratelimiter import RateLimiter
from threading import Lock
import requests
import config
from utils import execute_db_query
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)

class RoleManager:
    def __init__(self, guild_id):
        # Lock to synchronize API calls
        self.api_lock = Lock()

        # Set up rate limiter (4 requests per 1 second)
        self.limiter = RateLimiter(max_calls=4, period=1)  # 4 requests per second

        # API server URL from config
        self.api_url = config.API_URL

        # Store guild_id for API calls
        self.guild_id = guild_id

    def add_role(self, user_id, role_id):
        with self.api_lock:
            with self.limiter:
                logger.debug(f"Assigning role {role_id} to user {user_id}")
                self._add_role_api_call(user_id, role_id)

    def _add_role_api_call(self, user_id, role_id):
        try:
            data = {
                "guildId": self.guild_id,
                "userId": user_id,
                "roleId": role_id
            }
            response = requests.post(f"{self.api_url}/add-role", json=data)
            if response.status_code == 200:
                logger.debug(f"Role {role_id} added to user {user_id} via API call.")
            else:
                logger.error(f"Failed to add role to user {user_id}: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error adding role to user {user_id}: {e}")

        # Remove any existing timer for the user, as they are getting the role back
        self.cancel_timer(user_id)

    def remove_role(self, user_id, role_id):
        with self.api_lock:
            with self.limiter:
                logger.debug(f"Removing role {role_id} from user {user_id}")
                self._remove_role_api_call(user_id, role_id)

    def _remove_role_api_call(self, user_id, role_id):
        # Retrieve the start time of the timer before removing the role.
        timer_info = self.get_timer_info(user_id)
        start_time = timer_info['start_time'] if timer_info else 'No timer found'

        try:
            data = {
                "guildId": self.guild_id,
                "userId": user_id,
                "roleId": role_id,
                "timestamp": start_time
            }
            response = requests.post(f"{self.api_url}/remove-role", json=data)
            if response.status_code == 200:
                logger.debug(f"Role {role_id} removed from user {user_id} via API call. {start_time}")
            else:
                logger.error(f"Failed to remove role from user {user_id}: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error removing role from user {user_id}: {e}")

        # Delete the timer from the database
        execute_db_query('DELETE FROM timers WHERE discord_user_id = ?', (user_id,))

    def start_timer(self, user_id, role_id, duration=None):
        if duration is None:
            duration = config.TIMER_DURATION
        start_time = datetime.now()
        expiration_time = start_time + timedelta(seconds=duration)

        # Save timer to the database
        execute_db_query('REPLACE INTO timers (discord_user_id, role_id, expiration_time, start_time) VALUES (?, ?, ?, ?)',
                         (user_id, role_id, expiration_time.isoformat(), start_time.isoformat()))

        logger.debug(f"Started a timer for user {user_id}, role {role_id}, to expire at {expiration_time.isoformat()}")

    def cancel_timer(self, user_id):
        execute_db_query('DELETE FROM timers WHERE discord_user_id = ?', (user_id,))
        logger.debug(f"Cancelled timer for user {user_id}")

    def load_timers(self):
        conn = sqlite3.connect('timers.db')
        c = conn.cursor()
        c.execute('SELECT discord_user_id, role_id, expiration_time FROM timers')
        rows = c.fetchall()
        conn.close()
        return rows

    def get_timer_info(self, user_id):
        conn = sqlite3.connect('timers.db')
        c = conn.cursor()
        c.execute('SELECT start_time FROM timers WHERE discord_user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()

        if row:
            return {
                "start_time": row[0]  # Return the start time directly
            }
        return None
