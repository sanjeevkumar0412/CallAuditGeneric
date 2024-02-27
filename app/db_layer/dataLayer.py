from app.configs.config import dbconfig
import pyodbc

class SqlServerDB:
    server = 'your_server_name'
    database = 'your_database_name'
    username = 'your_username'
    password = 'your_password'

    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    def __init__(self):
        raise RuntimeError('Error on BaseClass Call get_instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def get_all_configurations(clent_id): 
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'GetAllConfigurations'
            parameters = {'ClientId': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(parameters.keys())}"       
            """
                CREATE PROCEDURE [dbo].[GetAllConfigurations]
                @ClientId nvarchar(30)
                AS
                SELECT * FROM Configuration WHERE ClientId = @ClientId
                GO;
            EXEC GetAllConfigurations @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def add_recording_details(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'AddRecordingDetails'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """        
                CREATE PROCEDURE [dbo].[AddRecordingDetails]
                @FileId  nvarchar(30)
                @ClientId  nvarchar(30)
                @UserName  nvarchar(30)
                @FileTypeId  nvarchar(30)
                @FileName  nvarchar(30)
                @FilePath  nvarchar(30)
                @UploadDate datetime
                @Status_Id  nvarchar(30)
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO RecordingDetails (FileId,ClientId,UserName,FileTypeId,FileName,FilePath,UploadDate,Status_Id)  VALUES  ( @FileId  nvarchar(30)
                @ClientId,
                @UserName,
                @FileTypeId,
                @FileName,
                @FilePath,
                @UploadDate,
                @Status_Id)
                GO;
            EXEC AddUpdateRecordingDetails @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_recording_details(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'UpdateRecordingDetails'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """        
                CREATE PROCEDURE [dbo].[UpdateRecordingDetails]
                @FileId  nvarchar(30)
                @ClientId  nvarchar(30)
                @UserName  nvarchar(30)
                @FileTypeId  nvarchar(30)
                @FileName  nvarchar(30)
                @FilePath  nvarchar(30)
                @UploadDate datetime
                @Status_Id  nvarchar(30)
                @IsActive  bit
                @IsDeleted  bit              
                AS
                UPDATE RecordingDetails 
                SET 
                FilePath =@FilePath,UploadDate =@UploadDate,Status_Id = @Status_Id
                WHERE FileId =@FileId
                GO;
            EXEC AddUpdateRecordingDetails @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def add_call_summary(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'AddUpdateCallSummary'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[AddUpdateCallSummary]
                @SummaryId  nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @SummaryDescription  nvarchar(30)
                @SummaryDateTime  datetime             
                @Status_Id  nvarchar(30)
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO CallSummary (SummaryId,ClientId,ClientName,SummaryDescription,SummaryDateTime,Status_Id)  VALUES  (@SummaryId,
                @ClientId,
                @ClientName,
                @SummaryDescription,
                @SummaryDateTime,              
                @Status_Id)
                GO;
            EXEC AddUpdateCallSummary @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_call_summary(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'AddUpdateCallSummary'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[AddUpdateCallSummary]
                @SummaryId  nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @SummaryDescription  nvarchar(30)
                @SummaryDateTime  datetime             
                @Status_Id  nvarchar(30)
                @IsActive  bit
                @IsDeleted  bit              
                AS
                UPDATE CallSummary  
                SET  
                SummaryDescription = @SummaryDescription,
                SummaryDateTime = @SummaryDateTime,              
                Status_Id = @Status_Id
                WHERE SummaryId = @SummaryId
                GO;
            EXEC AddUpdateCallSummary @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def add_errors_logs(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[ErrorLogs]
                @ErrorId  nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @ErrorType  nvarchar(30)
                @ErrorDetails  nvarchar(30)             
                @JobId  nvarchar(30)
                @ErrorDate  datetime
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO CallSummary (ErrorId,ClientId,ClientName,ErrorType,ErrorDetails,JobId,ErrorDate)  VALUES  (@ErrorId,
                @ClientId,
                @ClientName,
                @ErrorType,
                @ErrorDetails,
                @ErrorDate,              
                @JobId)
                GO;
            EXEC ErrorLogs @ClientId = 'QuickApps';
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def add_sentiment_analysis(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[SentimentAnalysis_Insert]
                @AnalysisId  nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @TranscriptId  nvarchar(30)
                @SentimentScore  nvarchar(30)             
                @SentimentStatus  nvarchar(30)
                @AnalysisDateTime  datetime
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO SentimentAnalysis (AnalysisId,ClientId,ClientName,TranscriptId,SentimentScore,SentimentStatus,AnalysisDateTime)  VALUES  (@AnalysisId,
                @ClientId,
                @ClientName,
                @TranscriptId,
                @SentimentScore,
                @SentimentStatus,              
                @AnalysisDateTime)
                GO;       
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_sentiment_analysis(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[SentimentAnalysis_Update]
                @AnalysisId  nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @TranscriptId  nvarchar(30)
                @SentimentScore  nvarchar(30)             
                @SentimentStatus  nvarchar(30)
                @AnalysisDateTime  datetime
                @IsActive  bit
                @IsDeleted  bit              
                AS
                UPDATE SentimentAnalysis SET 
                SentimentScore = @SentimentScore,
                SentimentStatus= @SentimentStatus,              
                AnalysisDateTime= @AnalysisDateTime)
                WHERE AnalysisId=@AnalysisId
                GO;       
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def add_audio_transcripts(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[AudioTranscripts_Insert]
                @TranscriptId   nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @FileId  nvarchar(30)
                @FileName  nvarchar(30)             
                @FileStatus  nvarchar(30)
                @TranscriptText  nvarchar(30)
                @TranscriptionFilePath  nvarchar(30)
                @TranscriptionDate  datetime 
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO AudioTranscripts (TranscriptId,ClientId,ClientName,FileId,FileName,FileStatus,TranscriptText,TranscriptionFilePath,TranscriptionDate)  VALUES  (@TranscriptId,
                @ClientId,
                @ClientName,
                @FileId,
                @FileName,
                @FileStatus,              
                @TranscriptText,
                @TranscriptionFilePath,
                @TranscriptionDate)
                GO;       
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_audio_transcripts(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[AudioTranscripts_Update]
                @TranscriptId   nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @FileId  nvarchar(30)
                @FileName  nvarchar(30)             
                @FileStatus  nvarchar(30)
                @TranscriptText  nvarchar(30)
                @TranscriptionFilePath  nvarchar(30)
                @TranscriptionDate  datetime 
                @IsActive  bit
                @IsDeleted  bit              
                AS
                UPDATE AudioTranscripts SET
                FileStatus= @FileStatus,              
                TranscriptText = @TranscriptText,
                TranscriptionFilePath= @TranscriptionFilePath,
                TranscriptionDate= @TranscriptionDate)
                WHERE TranscriptId  = @TranscriptId
                GO;       
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def add_update_transcripts_job(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
        try:   
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            stored_procedure_name = 'ErrorLogs'
            parameters = {'ClientId': clent_id,'Client': clent_id}
            query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
            """
                CREATE PROCEDURE [dbo].[AudioTranscripts]
                @JobId   nvarchar(30)
                @ClientId  nvarchar(30)
                @ClientName  nvarchar(30)
                @JobTypeId  nvarchar(30)
                @JobStarttime  datetime             
                @JobStatus  nvarchar(30)
                @JobEndTime  datetime
                @IsError  nvarchar(30)
                @TranscriptionDate  datetime 
                @IsActive  bit
                @IsDeleted  bit              
                AS
                INSERT INTO TranscriptsJob (JobId,ClientId,ClientName,JobTypeId,JobStarttime,JobStatus,JobEndTime,IsError)  VALUES  (@JobId,
                @ClientId,
                @ClientName,
                @JobTypeId,
                @JobStarttime,
                @JobStatus,              
                @JobEndTime,
                @IsError)
                GO;       
            """
            cursor.execute(query, parameters)
            connection.commit()        
        except Exception as e:
            print(f"Error in get_all_configurations: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()