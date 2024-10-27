# Discord Role Manager

## Overview

This application automates the assignment and removal of Discord roles based on user activity and criteria such as seeding points and hours played. 

## Features

- Assign/remove roles based on seeding points from Whitelister MongoDB.
- Assign/remove roles based on hours played from SquadJS SQL database.

## Directory Structure

- `database/`: Handles database connections.
- `role_manager/`: Manages role assignments and removals.
- `utils/`: Contains utility functions.
- `main.py`: Entry point of the application.
- `config.py`: Configuration variables (not committed to version control).
- `.env`: Environment variables (not committed to version control).

## Setup Instructions

### Prerequisites

- Python 3.x
- Whitelister MongoDB instance
- ActivityTracker plugin for SquadJS
- Discord Bot API access that allows role management. Might have to rewrite part of `role_manager.py` depending on the bot's api call handling.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/michalniko/Whitelister_Assistant.git
   cd discord_role_manager
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use 'venv\Scripts\activate'
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory.

    **Example .env**
    ```bash
   # MongoDB
   MONGODB_USERNAME=username
   MONGODB_PASSWORD=password
   MONGODB_HOST=localhost
   MONGODB_PORT=12345

   # True if you want to work on cloned MongoDB instance
   # False to skip this part and use main MongoDb instance
   USE_DB_CLONE=False
   MONGODB_MAIN_DATA_PATH=/path/to/main/mongodb/data
   MONGODB_CLONE_DATA_PATH=/path/to/clone/mongodb/data
   MONGODB_CLONE_CONTAINER_NAME=mongodb_clone

   # Double check the paths to main and clone

   # SQL Database 
   SQL_HOST=localhost
   SQL_PORT=1234
   SQL_USERNAME=username
   SQL_PASSWORD=password
   SQL_DATABASE=database

   # API 
   API_URL=http://127.0.0.1:1234

   # Discord 
   GUILD_ID=123456789123456789
   ROLE_ID=123456789123456789
   SEED_ROLE_ID=123456789123456789
   ACTIVITY_ROLE_ID=123456789123456789

   # Thresholds
   CHECK_POINTS=10 # Ammount of points needed to gain 100%
   HOURS_THRESHOLD=10  # Number of hours required in the past week

   # How often to start main.py
   TIMER_DURATION=60  # In seconds

   # Logging 
   LOG_FILE=app.log
   LOG_MAX_BYTES=1000000
    ```

5. **Create Configuration File**

    Create a `config.py` file in the root directory for additional settings.

    **Example config.py**
    ```python
   import os
   from dotenv import load_dotenv

   # Load environment variables from .env file
   load_dotenv()

   # MongoDB 
   MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
   MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
   MONGODB_HOST = os.getenv('MONGODB_HOST')
   MONGODB_PORT = os.getenv('MONGODB_PORT')
   MONGODB_URI = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}'
   DATABASE_NAME = 'admin'
   COLLECTION_NAME = 'players'

   # Flag to determine if cloning is needed
   USE_DB_CLONE = os.getenv('USE_DB_CLONE', 'False').lower() == 'true'
   # Paths for rsync
   MONGODB_MAIN_DATA_PATH = os.getenv('MONGODB_MAIN_DATA_PATH')
   MONGODB_CLONE_DATA_PATH = os.getenv('MONGODB_CLONE_DATA_PATH')
   MONGODB_CLONE_CONTAINER_NAME = os.getenv('MONGODB_CLONE_CONTAINER_NAME')

   # SQL Database 
   SQL_HOST = os.getenv('SQL_HOST')
   SQL_PORT = int(os.getenv('SQL_PORT', '3306'))
   SQL_USERNAME = os.getenv('SQL_USERNAME')
   SQL_PASSWORD = os.getenv('SQL_PASSWORD')
   SQL_DATABASE = os.getenv('SQL_DATABASE')

   # API 
   API_URL = os.getenv('API_URL')

   # Discord 
   GUILD_ID = os.getenv('GUILD_ID')
   ROLE_ID = os.getenv('ROLE_ID')  # CI member role
   SEED_ROLE_ID = os.getenv('SEED_ROLE_ID')  # Test role
   ACTIVITY_ROLE_ID = os.getenv('ACTIVITY_ROLE_ID')  # Replace with actual role ID

   # SEEDING Thresholds
   CHECK_POINTS = float(os.getenv('CHECK_POINTS', '78.5'))
   HOURS_THRESHOLD = float(os.getenv('HOURS_THRESHOLD', '10'))

   # Timer 
   TIMER_DURATION = int(os.getenv('TIMER_DURATION', '58'))  # In seconds

   # Logging 
   LOG_FILE = os.getenv('LOG_FILE', 'app.log')
   LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '1000000'))
   LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    ```


