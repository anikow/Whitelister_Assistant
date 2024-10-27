import time
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import config
from database.mongodb import perform_database_operations
from database.sql import connect_to_sql
from role_manager import RoleManager
from pymongo import errors as mongo_errors
import mysql.connector
from mysql.connector import Error as mysql_errors
from utils import initialize_database, run_rsync

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a rotating file handler to manage log file size
handler = RotatingFileHandler(config.LOG_FILE, maxBytes=config.LOG_MAX_BYTES, backupCount=config.LOG_BACKUP_COUNT)
logger.addHandler(handler)

# Initialize the database and create the timers table if it doesn't exist
initialize_database()

# Initialize RoleManager
role_manager = RoleManager(config.GUILD_ID)

def handle_seeding_points(members_data, reward_points):
    try:

        timers = role_manager.load_timers()

        users_to_assign = []
        users_removed = []
        users_with_timers = []
        users_unchanged = []

        for doc in members_data:
            discord_user_id = doc['discord_user_id']
            user_roles = doc.get('discord_roles_ids', [])
            seeding_points = doc.get('seeding_points', 0)

            # Check if a timer already exists for this user
            existing_timer = next((t for t in timers if t[0] == discord_user_id), None)
            expiration_time = datetime.fromisoformat(existing_timer[2]) if existing_timer else None

            if seeding_points > reward_points and config.SEED_ROLE_ID not in user_roles:
                users_to_assign.append(discord_user_id)
                role_manager.add_role(discord_user_id, config.SEED_ROLE_ID)
                if existing_timer:
                    role_manager.cancel_timer(discord_user_id)
            elif seeding_points <= reward_points and config.SEED_ROLE_ID in user_roles:
                if expiration_time and datetime.now() > expiration_time:
                    role_manager.remove_role(discord_user_id, config.SEED_ROLE_ID)
                    logger.debug(f"Timer for user {discord_user_id} has expired, role removed.")
                    users_removed.append(discord_user_id)
                elif not existing_timer:
                    users_with_timers.append(discord_user_id)
                    role_manager.start_timer(discord_user_id, config.SEED_ROLE_ID)
                else:
                    users_with_timers.append(discord_user_id)
                    expiration_time_str = existing_timer[2] if existing_timer else 'N/A'
                    logger.debug(f"Timer already exists for user {discord_user_id}, expiring at {expiration_time_str}, skipping.")
            else:
                users_unchanged.append(discord_user_id)

        logger.info(f"Processed {len(members_data)} users for seeding points.")
        logger.info(f"{len(users_to_assign)} users had roles assigned: {users_to_assign}")
        logger.info(f"{len(users_removed)} users were removed: {users_removed}")
        logger.info(f"{len(users_with_timers)} users have timers: {users_with_timers}")
        logger.info(f"{len(users_unchanged)} users were unchanged: {users_unchanged}")

    except Exception as err:
        logger.error(f'An error occurred in handle_seeding_points: {err}')

def handle_hours_played(members_data):
    try:
        # Connect to SQL database
        sql_cnx = connect_to_sql()
        cursor = sql_cnx.cursor(dictionary=True)

        # Calculate the time window for the past 'n' weeks
        weeks_ago = datetime.now() - timedelta(weeks=config.HOURS_PLAYED_WEEKS)

        # Query to get total hours played in the past week per user
        query = """
        SELECT
            steamID,
            SUM(TIMESTAMPDIFF(SECOND, joinTime, leaveTime)) / 3600 AS hours_played
        FROM
            ActivityTracker_PlayerSession
        WHERE
            joinTime >= %s
        GROUP BY
            steamID
        """

        cursor.execute(query, (weeks_ago,))
        hours_data = cursor.fetchall()

        if not hours_data:
            logger.info('No player activity data found for the past week.')
            return

        # Map Steam IDs to hours played
        steam_hours_map = {row['steamID']: row['hours_played'] for row in hours_data}

        users_to_assign = []
        users_removed = []
        users_unchanged = []

        for user in members_data:
            steam_id = user['steamid64']
            discord_user_id = user['discord_user_id']
            user_roles = user.get('discord_roles_ids', [])
            hours_played = steam_hours_map.get(steam_id, 0) # Defaults to 0 if not found on

            if hours_played >= config.HOURS_THRESHOLD and config.ACTIVITY_ROLE_ID not in user_roles:
                users_to_assign.append(discord_user_id)
                role_manager.add_role(discord_user_id, config.ACTIVITY_ROLE_ID)
            elif hours_played < config.HOURS_THRESHOLD and config.ACTIVITY_ROLE_ID in user_roles:
                users_removed.append(discord_user_id)
                role_manager.remove_role(discord_user_id, config.ACTIVITY_ROLE_ID)
            else:
                users_unchanged.append(discord_user_id)

        logger.info(f"Processed {len(members_data)} users for hours played.")
        logger.info(f"{len(users_to_assign)} users had roles assigned: {users_to_assign}")
        logger.info(f"{len(users_removed)} users were removed: {users_removed}")
        logger.info(f"{len(users_unchanged)} users were unchanged: {users_unchanged}")

    except mysql_errors as err:
        logger.error(f'SQL error in handle_hours_played: {err}')
    except mongo_errors.PyMongoError as err:
        logger.error(f'MongoDB error in handle_hours_played: {err}')
    except Exception as err:
        logger.error(f'An error occurred in handle_hours_played: {err}')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'sql_cnx' in locals():
            sql_cnx.close()
            logger.info('Connection to SQL database closed')

def main():

    # Fetch data from mongodb
    db_results = perform_database_operations()
    
    # Extract variables from the returned dictionary
    members_data = db_results.get('members', [])
    reward_points = db_results.get('reward_points', 115)

    logger.info(f'Number of Members: {len(members_data)}')
    logger.info(f'Points Needed for Reward: {reward_points}')

    # Handle seeding points and roles
    handle_seeding_points(members_data, reward_points)

    # Handle hours played and roles
    handle_hours_played(members_data)

if __name__ == '__main__':
    try:
        while True:
            main()
            time.sleep(60)  # Run every 1 minute
    except KeyboardInterrupt:
        logger.info('Program interrupted by user.')
