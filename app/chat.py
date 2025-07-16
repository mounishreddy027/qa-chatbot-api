from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from databases import Database
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate environment variables
required_env_vars = ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 
                     'POSTGRES_PORT', 'POSTGRES_DB']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

# PostgreSQL connection URL
try:
    DATABASE_URL = (
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )
except Exception as e:
    logger.error(f"Failed to construct database URL: {str(e)}")
    raise

database = Database(DATABASE_URL)
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500))
    answer = Column(String(5000))
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables (run once)
try:
    engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

async def add_to_history(question: str, answer: str):
    """Add a question-answer pair to chat history with error handling."""
    if not question or not answer:
        logger.warning("Attempted to add empty question or answer to history")
        return False
        
    try:
        query = ChatHistory.__table__.insert().values(
            question=question,
            answer=answer,
            timestamp=datetime.utcnow()
        )
        await database.execute(query)
        logger.info("Added new entry to chat history")
        return True
    except Exception as e:
        logger.error(f"Failed to add to chat history: {str(e)}")
        return False

async def get_history(limit: int = 100):
    """Get chat history with error handling."""
    try:
        if limit <= 0:
            logger.warning(f"Invalid limit value: {limit}, using default")
            limit = 100
            
        query = ChatHistory.__table__.select().order_by(ChatHistory.timestamp.desc()).limit(limit)
        result = await database.fetch_all(query)
        logger.info(f"Retrieved {len(result)} chat history entries")
        return result
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        return []

async def connect_db():
    """Connect to the database with error handling."""
    try:
        await database.connect()
        logger.info("Database connection established")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return False

async def disconnect_db():
    """Disconnect from the database with error handling."""
    try:
        await database.disconnect()
        logger.info("Database connection closed")
        return True
    except Exception as e:
        logger.error(f"Error disconnecting from database: {str(e)}")
        return False