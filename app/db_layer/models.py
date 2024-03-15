from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,inspect


Base = declarative_base()

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'Users'

    Id = Column(Integer, primary_key=True, autoincrement=False)
    Name = Column(String)
    Email = Column(String)

    def __repr__(self):
        return f"<Client(Id={self.Id}, Name='{self.Name}', Email='{self.Email}')>"


class Client(Base):
    __tablename__ = 'Client'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, unique=True, nullable=False)
    ClientId = Column(String, primary_key=True, unique=True, nullable=False)
    ClientName = Column(String, unique=True, nullable=False)
    ClientEmail = Column(String, unique=True, nullable=False)
    ClientUserName = Column(String, unique=True, nullable=False)
    ClientPassword = Column(String, unique=True, nullable=False)
    ServerName = Column(String, unique=True, nullable=False)
    DatabaseName = Column(String, unique=True, nullable=False)
    AuthenticationType= Column(String, unique=True, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<Client(ClientId={self.ClientId}, ClientName='{self.ClientName}', ClientEmail='{self.ClientEmail}',ClientUserName='{self.ClientUserName}',ClientPassword='{self.ClientPassword}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class AuthTokenManagement(Base):
    __tablename__ = 'AuthTokenManagement'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(String, ForeignKey("Client.ClientId"), nullable=False)
    UserName = Column(String, unique=False,nullable=False)
    Token = Column(String, unique=False,nullable=False)
    SecretKey = Column(String, unique=False,nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<AuthTokenManagement(UserName={self.UserName}, ClientId='{self.ClientId}', Token='{self.Token}',SecretKey='{self.SecretKey}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class BillingInformation(Base):
    __tablename__ = 'BillingInformation'

    BillingId = Column(Integer, primary_key=True)
    ClientId = Column(String, ForeignKey("Client.ClientId"))
    SubscriptionId = Column(String, ForeignKey("SubscriptionPlan.SubscriptionId"))
    ClientName = Column(String, nullable=False)
    SubscriptionStartDate = Column(DateTime, default=datetime.utcnow())
    SubscriptionEndDate = Column(DateTime, default=datetime.utcnow())
    PaymentStatus = Column(String, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<BillingInformation(BillingId={self.BillingId}, ClientId='{self.ClientId}', SubscriptionId='{self.SubscriptionId}',ClientName='{self.ClientName}',SubscriptionStartDate='{self.SubscriptionStartDate}',SubscriptionEndDate='{self.SubscriptionEndDate}',PaymentStatus='{self.PaymentStatus}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class UsersManagement(Base):
    __tablename__ = 'UsersManagement'

    UserName = Column(String, primary_key=True, unique=False, nullable=False)
    ClientId = Column(String, ForeignKey('Client.ClientId'), nullable=False)
    UserEmail = Column(String, unique=False, nullable=False)
    UserPassword = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<UsersManagement(UserName={self.UserName}, ClientId='{self.ClientId}', UserEmail='{self.UserEmail}',UserPassword='{self.UserPassword}'" \
               f",IsActive='{self.IsActive}',Modified='{self.Modified}',Created='{self.Created}',IsDeleted='{self.IsDeleted}')>"


class Subscriptions(Base):
    __tablename__ = 'Subscriptions'

    SubscriptionId = Column(String, primary_key=True)
    ClientId = Column(String, ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionPlan = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<Subscriptions(SubscriptionId={self.SubscriptionId}, ClientId='{self.ClientId}', SubscriptionPlan='{self.SubscriptionPlan}',Modified='{self.Modified}',Created='{self.Created}'" \
               f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class SubscriptionPlan(Base):
    __tablename__ = 'SubscriptionPlan'

    SubscriptionId = Column(String, primary_key=True)
    ClientId = Column(String, ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionName = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<SubscriptionPlan(SubscriptionId={self.SubscriptionId}, ClientId='{self.ClientId}', SubscriptionName='{self.SubscriptionName}',Modified='{self.Modified}',Created='{self.Created}'" \
               f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class Configurations(Base):
    __tablename__ = 'Configurations'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    ConfigKey = Column(String, unique=False, nullable=False)
    ConfigValue = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<Configurations(ClientId={self.ClientId}, ConfigKey='{self.ConfigKey}', ConfigValue='{self.ConfigValue}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class JobStatus(Base):
    __tablename__ = 'JobStatus'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    StatusName = Column(String, unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<JobStatus(ClientId={self.ClientId}, StatusName='{self.StatusName}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class FileTypesInfo(Base):
    __tablename__ = 'FileTypesInfo'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    FileType = Column(String, unique=False, nullable=False)
    FilePath = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<FileTypesInfo(ClientId={self.ClientId}, FileType='{self.FileType}', FilePath='{self.FilePath}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted})>"


class ClientCallRecording(Base):
    __tablename__ = 'ClientCallRecording'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    CallFileName = Column(String, unique=False, nullable=False)
    CallFilePath = Column(String, unique=False, nullable=False)
    UploadDate = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<ClientCallRecording(ClientId={self.ClientId}, CallFileName='{self.CallFileName}',CallFilePath='{self.CallFilePath}',UploadDate='{self.UploadDate}',Created='{self.Created}" \
               f",Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class ClientCallSummary(Base):
    __tablename__ = 'ClientCallSummary'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    SummaryDescription = Column(String(150), unique=False, nullable=False)
    SummaryDateTime = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<ClientCallSummary(ClientId={self.ClientId},SummaryDescription='{self.SummaryDescription}',SummaryDateTime='{self.SummaryDateTime}', Created='{self.Created}" \
               f",Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class Logs(Base):
    __tablename__ = 'Logs'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    LogType = Column(String, unique=False, nullable=True)
    LogSummary = Column(String, unique=False, nullable=True)
    ModulName = Column(String, unique=False, nullable=True)
    LogDetails = Column(String, unique=False, nullable=True)
    Severity = Column(String, unique=False, nullable=True)
    ErrorLevel = Column(String, unique=False, nullable=True)
    LoggerName = Column(String, unique=False, nullable=True)
    LineNumber = Column(Integer, unique=False, nullable=True)
    FunctionName = Column(String, unique=False, nullable=True)
    FileName = Column(String, unique=False, nullable=True)
    StackTrace = Column(String, unique=False, nullable=True)
    LogDate = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)

    def __repr__(self):
        return f"<Logs(ClientId={self.ClientId}, LogType='{self.LogType}',LogSummary='{self.LogSummary}',LogDetails='{self.LogDetails}',ModulName='{self.ModulName}',Severity='{self.Severity}',LogDate='{self.LogDate},Created='{self.Created}" \
               f",Modified='{self.Modified}')>"


class SentimentAnalysis(Base):
    __tablename__ = 'SentimentAnalysis'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    TranscriptId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    SentimentScore = Column(String, nullable=True)
    SentimentText = Column(String, nullable=True)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow(), nullable=True)
    SentimentStatus = Column(String, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<SentimentAnalysis(ClientId={self.ClientId}, TranscriptId='{self.TranscriptId}',SentimentText='{self.SentimentText}',SentimentScore='{self.SentimentScore},AnalysisDateTime='{self.AnalysisDateTime}" \
               f",SentimentStatus='{self.SentimentStatus}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class AudioTranscribe(Base):
    __tablename__ = 'AudioTranscribe'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey(Client.ClientId), nullable=False)
    AudioFileName = Column(String, nullable=False)
    JobStatus = Column(String, nullable=False)
    FileType = Column(String, nullable=False)
    TranscribeText = Column(String, nullable=True)
    TranscribeFilePath = Column(String, nullable=False)
    SentimentStatus= Column(String, nullable=False)
    TranscribeStartTime = Column(DateTime, nullable=True)
    TranscribeEndTime = Column(DateTime, nullable=True)
    TranscribeDate = Column(DateTime, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, default=True, nullable=True)
    IsDeleted = Column(Boolean, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    # def toDict(self):
    #     column_attrs = inspect(self).mapper.column_attrs
    #     return {
    #         c.key: (
    #             getattr(self, c.key).isoformat() if isinstance(column_attrs[c.key].type, DateTime) else getattr(self,
    #                                                                                                             c.key))
    #         for c in column_attrs
    #     }


    # def toDict(self):
    #     return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    # def __init__(self, Id, ClientId, AudioFileName,JobStatus,FileType,TranscribeText,TranscribeFilePath,SentimentStatus,TranscribeStartTime,TranscribeEndTime,TranscribeDate,Created,Modified,IsActive,IsDeleted):
    #      self.Id:Id
    #      self.ClientId = ClientId
    #      self.AudioFileName=AudioFileName
    #      self.JobStatus=JobStatus
    #      self.FileType = FileType
    #      self.TranscribeText =TranscribeText
    #      self.TranscribeFilePath= TranscribeFilePath
    #      self.SentimentStatus = SentimentStatus
    #      self.TranscribeStartTime= TranscribeStartTime
    #      self.TranscribeEndTime =TranscribeEndTime
    #      self.TranscribeDate =TranscribeDate
    #      self.Created =Created
    #      self.Modified= Modified
    #      self.IsActive= IsActive
    #      self.IsDeleted =self.IsDeleted
    # def to_dict(self):
    #     """Returns a dictionary representation of the model instance."""
    #     return {
    #         "Id": self.Id,
    #         "ClientId": self.ClientId,
    #         "AudioFileName": self.AudioFileName,
    #         "JobStatus": self.JobStatus,
    #         "FileType": self.FileType,
    #         "TranscribeText": self.TranscribeText,
    #         "TranscribeFilePath": self.TranscribeFilePath,
    #         "SentimentStatus": self.SentimentStatus,
    #         "TranscribeStartTime": self.TranscribeStartTime,
    #         "TranscribeEndTime": self.TranscribeEndTime,
    #         "TranscribeDate": self.TranscribeDate,
    #         "Created": self.Created,
    #         "Modified": self.Modified,
    #         "IsActive": self.IsActive,
    #         "IsDeleted": self.IsDeleted,
    #     }
    # def __repr__(self):
    #     return f"<AudioTranscribe(ClientId={self.ClientId}, AudioFileName='{self.AudioFileName}',JobStatus='{self.JobStatus}',FileType='{self.FileType}',TranscribeText='{self.TranscribeText},TranscribeFilePath='{self.TranscribeFilePath}" \
    #            f",TranscribeStartTime='{self.TranscribeStartTime}',TranscribeEndTime='{self.TranscribeEndTime}',TranscribeDate='{self.TranscribeDate}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class AudioTranscribeTracker(Base):
    __tablename__ = 'AudioTranscribeTracker'

    Id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    AudioId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    AudioFileName = Column(String, unique=False, nullable=True)
    ChunkSequence = Column(String, unique=False, nullable=True)
    ChunkText = Column(String, unique=False, nullable=True)
    ChunkFilePath = Column(String, unique=False, nullable=True)
    ChunkStatus = Column(String, unique=False, nullable=True)
    ChunkTranscribeStart = Column(DateTime, unique=False, nullable=True)
    ChunkTranscribeEnd = Column(DateTime, unique=False, nullable=True)
    ChunkCreatedDate = Column(DateTime, unique=False, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def __repr__(self):
        return f"<AudioTranscribeTracker(ClientId={self.ClientId}, AudioId='{self.AudioId}',AudioFileName='{self.AudioFileName}',ChunkSequence='{self.ChunkSequence}',ChunkText='{self.ChunkText},ChunkFilePath='{self.ChunkFilePath}" \
               f",ChunkStatus='{self.ChunkStatus}',ChunkTranscribeStart='{self.ChunkTranscribeStart}',ChunkTranscribeEnd='{self.ChunkTranscribeEnd}',ChunkCreatedDate='{self.ChunkCreatedDate}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class ClientMaster(Base):
    __tablename__ = 'ClientMaster'

    Id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, unique=True, nullable=False)
    ClientName = Column(String, unique=True, nullable=False)
    ClientUser = Column(String, unique=True, nullable=False)
    ServerName = Column(String, unique=True, nullable=False)
    DatabaseName = Column(String, unique=True, nullable=False)
    ConnectionString = Column(String, unique=True, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=False)
    IsActive = Column(Boolean, unique=False, default=True, nullable=False)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=False)

    def __repr__(self):
        return (
            f"<ClientMaster(ClientId={self.ClientId}, ClientName='{self.ClientName}', ClientUser='{self.ClientUser}', ServerName='{self.ServerName}', DatabaseName='{self.DatabaseName}', ConnectionString='{self.ConnectionString}', Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>")
