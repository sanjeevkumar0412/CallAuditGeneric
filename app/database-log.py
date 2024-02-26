import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a SQLAlchemy engine
engine = create_engine('sqlite:///logs.db', echo=True)

# Create a sessionmaker
Session = sessionmaker(bind=engine)

Base = declarative_base()

# Define a Log model
class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    level = Column(String(10))
    func_name = Column(String(50))
    file_name = Column(String(50))
    message = Column(String)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<Log(id={self.id},level={self.level} ,func_name={self.func_name},file_name={self.file_name}, message={self.message}, created_at={self.created_at})>"

# Create tables in the database
Base.metadata.create_all(engine)

# Create a custom database logger
class DatabaseLogger(logging.Handler):
    def emit(self, record):
        # Create a session
        session = Session()

        # Insert log record into the database
        log = Log(level=record.levelname, message=record.msg)
        session.add(log)
        session.commit()

        # Close the session
        session.close()

# Create a logger

logger = logging.getLogger('db_logger')
logger.setLevel(logging.DEBUG)

# Add the custom database handler to the logger
db_handler = DatabaseLogger()
logger.addHandler(db_handler)

# Log some messages

logger.critical('This is a critical message')

def main(logger,db_handler):
    try:
        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.warning('This is a warning message')
        logger.error('This is an error message')
    except Exception as e:
        logger.critical('Critical Error',e)
