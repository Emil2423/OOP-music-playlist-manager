"""Main entry point for Music Playlist Manager application.

This is the single entry point for the application that initializes
all components and starts the CLI controller.
"""

import sys
import logging
from logging_config import setup_logging, get_logger
from database.connection import DatabaseConnection
from controllers.cli_controller import CLIController

# Initialize logging
setup_logging()
logger = get_logger(__name__)


def initialize_app():
    """Initialize application - setup database connection.
    
    Returns:
        DatabaseConnection: Connected database instance
        
    Raises:
        RuntimeError: If initialization fails
    """
    try:
        logger.info("=" * 60)
        logger.info("Initializing Music Playlist Manager Application")
        logger.info("=" * 60)
        
        db = DatabaseConnection()
        db.connect()
        logger.info("Database connection established")
        logger.info("Application initialization completed successfully")
        return db
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise RuntimeError(f"Failed to initialize application: {e}")


def shutdown_app():
    """Shutdown application - close database connection."""
    try:
        db = DatabaseConnection()
        db.disconnect()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def main():
    """Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        initialize_app()
        
        controller = CLIController()
        controller.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ Fatal error: {e}")
        return 1
        
    finally:
        shutdown_app()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
