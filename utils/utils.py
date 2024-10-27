import sqlite3
import subprocess
import logging
import os
import config

logger = logging.getLogger(__name__)

def execute_db_query(query, args=()):
    conn = sqlite3.connect('timers.db')
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    conn.close()

def initialize_database():
    """
    Initializes the timers.db database and creates the timers table if it doesn't exist.
    """
    if not os.path.exists('timers.db'):
        logger.info('Database timers.db does not exist. Creating a new one.')
    else:
        logger.info('Database timers.db already exists.')

    # Create the timers table if it doesn't exist
    execute_db_query('''
    CREATE TABLE IF NOT EXISTS timers (
        discord_user_id TEXT PRIMARY KEY,
        role_id TEXT,
        expiration_time TEXT,
        start_time TEXT
    )
    ''')
    logger.info('Timers table ensured to exist in timers.db.')

def run_command(command):
    """
    Helper function to run a shell command.
    """
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
        raise
def run_rsync():
    """
    Stops the MongoDB clone container, runs the rsync command to synchronize the MongoDB data from the original to the clone, and then restarts the container.
    """
    container_name = config.MONGODB_CLONE_CONTAINER_NAME

    # Stop MongoDB Docker container
    logger.info("Stopping MongoDB clone container...")
    run_command(['docker', 'stop', container_name])

    # Run rsync
    try:
        logger.info("Running rsync to synchronize MongoDB data...")
        result = run_command(
            [
                'rsync', '-avz', '--delete',
                f"{config.MONGODB_MAIN_DATA_PATH}/",
                f"{config.MONGODB_CLONE_DATA_PATH}/"
            ]
        )
        logger.debug(f"rsync output:\n{result}")
    finally:
        # Start MongoDB Docker container
        logger.info("Starting MongoDB clone container...")
        run_command(['docker', 'start', container_name])