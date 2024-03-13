from loguru import logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db_layer.models import Logs


class Logger:
    _instance = None
    _logs = ""
    error_level_trace = 'TRACE'
    error_level_debug = 'DEBUG'
    error_level_info = 'INFO'
    error_level_warning = 'WARNING'
    error_level_error = 'ERROR'
    error_level_critical = 'CRITICAL'
    severity_level_trace = '5'
    severity_level_debug = '10'
    severity_level_info = '20'
    severity_level_warning = '30'
    severity_level_error = '40'
    severity_level_critical = '50'

    def __init__(self):
        # self.db_class = DataBaseClass()
        self._instance = logger
        # self.global_state = GlobalState()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def debug(self, message: str):
        logger.debug(f"Debug message : {message}")

    def info(self, message):
        logger.info(f"Logger Info : {message}")

    def warning(self, message):
        logger.warning(f"Warning message  : {message}")

    def error(self, function_name, message):
        logger.error(f"Error in {function_name} : {message}")

    def get_logs(self, message):
        logger.log(f"Log message : {message}")

    def log_exceptions(self, function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                logger.exception(f"An error occurred in {function.__name__}: {e}")
                """
                # Example usage Decorator  :
                    @log_exceptions
                    def divide(a, b):
                        return a / b
                """

        return wrapper

    def custom_catch(self, *args, **kwargs):
        try:
            return super().catch(*args, **kwargs)
            """
                # Replace the default logger with the custom logger
                self.logger.remove()
                self.logger.add(self.logger.custom_catch(), format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
                # Test the custom logger
                logger.info("This is an information message")
                self.logger.error("This is an error message")
            """
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.exception(f"An error occurred: {e}")

    def create_log_file(self, file_name, rotation="100 MB", level="INFO"):
        """  
        Args:
            filename (str): Name of the log file to create.
            rotation (str, optional): Rotation size (e.g., "10 MB", "500 KB"). Defaults to "100 MB".
            level (str, optional): Log level. Defaults to "INFO".
        """
        logger.add(file_name, level=level, rotation=rotation)

    def save_log_table_entry(self, server_name, database_name, model_info):
        try:
            dns = f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(model_info)
            session.commit()
            session.close()
        except Exception as e:
            session.close()
            logger.error(f"An error occurred in save_log_table_entry: {e}")
        finally:
            session.close()

    def log_entry_into_sql_table(self, server_name, database_name, client_id, is_removed=False):
        try:
            def log_to_sql(record):
                try:
                    dns = f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server'
                    engine = create_engine(dns)
                    Session = sessionmaker(bind=engine)
                    session = Session()
                    logger_record = record.record
                    log_entry = Logs(
                        ClientId=client_id,
                        ErrorLevel=logger_record["level"].name,
                        Severity=str(logger_record["level"].no),
                        LogType=logger_record["level"].name,
                        LogDetails=logger_record["message"],
                        LogSummary=logger_record["message"],
                        LoggerName=logger_record["name"],
                        LineNumber=logger_record["line"],
                        FunctionName=logger_record["function"],
                        FileName=logger_record["file"].name,
                        StackTrace=logger_record["message"],
                        ModulName=logger_record["module"],
                        LogDate=logger_record["time"]
                    )
                    session.add(log_entry)
                    session.commit()
                except Exception as e:
                    logger.error("An error occurred while connecting to the SQL database:", e)
                finally:
                    session.close()


            # Add the custom Loguru handler (Sink)
            if is_removed:
                logger.remove(log_to_sql)
            else:
                logger.add(log_to_sql, level='DEBUG', serialize=True)
        except Exception as e:
            logger.error("An error occurred while connecting to the SQL database:", e)
