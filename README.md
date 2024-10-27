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

   # Number of weeks to consider for hours played
   HOURS_PLAYED_WEEKS=2
   HOURS_THRESHOLD=25  # Number of hours required in the past week

   # Lenghts of whitelist after dropping bellow seed point threshold
   TIMER_DURATION=500  # In seconds

   # Logging 
   LOG_FILE=app.log
   LOG_MAX_BYTES=1000000
   LOG_BACKUP_COUNT=5
    ```


