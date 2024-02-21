from app.configs.config import dbconfig
import pyodbc

server = 'your_server_name'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'

connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

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

def add_update_recording_details(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
    try:   
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        stored_procedure_name = 'AddUpdateRecordingDetails'
        parameters = {'ClientId': clent_id,'Client': clent_id}
        query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
        """
            CREATE PROCEDURE [dbo].[AddUpdateRecordingDetails]
              @FileId  nvarchar(30)
              @ClientId  nvarchar(30)
              @UserName  nvarchar(30)
              @FileTypeId  nvarchar(30)
              @FileName  nvarchar(30)
              @FilePath  nvarchar(30)
              @UploadDate nvarchar(30)
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

def add_update_call_summary(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
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
              @SummaryDateTime  nvarchar(30)             
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
              @ErrorDate  nvarchar(30)
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

def add_update_sentiment_analysis(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
    try:   
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        stored_procedure_name = 'ErrorLogs'
        parameters = {'ClientId': clent_id,'Client': clent_id}
        query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
        """
            CREATE PROCEDURE [dbo].[SentimentAnalysis]
              @AnalysisId  nvarchar(30)
              @ClientId  nvarchar(30)
              @ClientName  nvarchar(30)
              @TranscriptId  nvarchar(30)
              @SentimentScore  nvarchar(30)             
              @SentimentStatus  nvarchar(30)
              @AnalysisDateTime  nvarchar(30)
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

def add_update_audio_transcripts(clent_id,data): #data is in object form like {'ClientId': clent_id,'ClientId': clent_id}
    try:   
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        stored_procedure_name = 'ErrorLogs'
        parameters = {'ClientId': clent_id,'Client': clent_id}
        query = f"EXEC {stored_procedure_name} @{', '.join(data.keys())}"       
        """
            CREATE PROCEDURE [dbo].[AudioTranscripts]
              @TranscriptId   nvarchar(30)
              @ClientId  nvarchar(30)
              @ClientName  nvarchar(30)
              @FileId  nvarchar(30)
              @FileName  nvarchar(30)             
              @FileStatus  nvarchar(30)
              @TranscriptText  nvarchar(30)
              @TranscriptionFilePath  nvarchar(30)
              @TranscriptionDate  nvarchar(30) 
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
              @JobStarttime  nvarchar(30)             
              @JobStatus  nvarchar(30)
              @JobEndTime  nvarchar(30)
              @IsError  nvarchar(30)
              @TranscriptionDate  nvarchar(30) 
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