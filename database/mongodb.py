from pymongo import MongoClient, errors as mongo_errors
import logging
import config
from utils import run_rsync
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

def connect_to_mongodb():
    uri = config.MONGODB_URI
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info('Connected successfully to MongoDB')
        return client
    except mongo_errors.ServerSelectionTimeoutError:
        logger.error('Failed to connect to MongoDB: Server selection timeout.')
        raise
    except mongo_errors.ConnectionError:
        logger.error('Failed to connect to MongoDB: Connection error.')
        raise
    except Exception as err:
        logger.error(f'An unexpected error occurred: {err}')
        raise

def fetch_members_with_role():
    """
    Connects to MongoDB, retrieves all members with the specified ROLE_ID, and returns the data.
    """
    try:
        # Synchronize the MongoDB clone if cloning is enabled
        if config.USE_DB_CLONE:
            run_rsync()

        client = connect_to_mongodb()
        database = client[config.DATABASE_NAME]
        collection = database[config.COLLECTION_NAME]

        query = {'discord_roles_ids': config.ROLE_ID}
        data = list(collection.find(query))

        if not data:
            logger.info(f'No data found for role: {config.ROLE_ID}')
            return []

        return data

    except mongo_errors.PyMongoError as err:
        logger.error(f'MongoDB error during member fetch: {err}')
        return []
    except Exception as err:
        logger.error(f'An error occurred during member fetch: {err}')
        return []
    finally:
        if 'client' in locals():
            client.close()
            logger.info('Connection to MongoDB closed after fetching members.')
