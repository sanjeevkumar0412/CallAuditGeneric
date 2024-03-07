
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String,DateTime,Boolean,ForeignKey

Base = declarative_base()

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'Users'

    Id = Column(Integer, primary_key=True,autoincrement=False)
    Name = Column(String)
    Email = Column(String)

    def __repr__(self):
        return f"<Client(Id={self.Id}, Name='{self.Name}', Email='{self.Email}')>"

class Client(Base):
    __tablename__ = 'client'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, unique=True, nullable=False)
    ClientId = Column(String, primary_key=True,unique=True,nullable=False)
    ClientName = Column(String,unique=True,nullable=False)
    ClientEmail = Column(String,unique=True,nullable=False)
    ClientUserName = Column(String,unique=True,nullable=False)
    ClientPassword = Column(String)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean)
    IsDeleted = Column(Boolean)

    def __repr__(self):
        return f"<Client(ClientId={self.ClientId}, ClientName='{self.ClientName}', ClientEmail='{self.ClientEmail}',ClientUserName='{self.ClientUserName}',ClientPassword='{self.ClientPassword}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class AuthTokenManagement(Base):
    __tablename__ = 'AuthTokenManagement'

    Id = Column(Integer, primary_key=True,unique=True,nullable=False)
    UserName = Column(String(50),nullable=False)
    ClientId = Column(String(50),ForeignKey("Client.ClientId"),nullable=False)
    Token = Column(String(50),nullable=False)
    SecretKey = Column(String(50),nullable=False)
    Created=Column(DateTime, default=datetime.utcnow())
    Modified=Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean)
    IsDeleted = Column(Boolean)

    def __repr__(self):
        return f"<AuthTokenManagement(UserName={self.UserName}, ClientId='{self.ClientId}', Token='{self.Token}',SecretKey='{self.SecretKey}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class BillingInformation(Base):

    __tablename__ = 'BillingInformation'

    BillingId = Column(Integer, primary_key=True)
    ClientId=Column(String(50), ForeignKey("Client.ClientId"))
    SubscriptionId = Column(String(50), ForeignKey("SubscriptionPlan.SubscriptionId"))
    ClientName = Column(String(50),nullable=False)
    SubscriptionStartDate=Column(DateTime,default=datetime.utcnow())
    SubscriptionEndDate=Column(DateTime,default=datetime.utcnow())
    PaymentStatus = Column(String(50), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<BillingInformation(BillingId={self.BillingId}, ClientId='{self.ClientId}', SubscriptionId='{self.SubscriptionId}',ClientName='{self.ClientName}',SubscriptionStartDate='{self.SubscriptionStartDate}',SubscriptionEndDate='{self.SubscriptionEndDate}',PaymentStatus='{self.PaymentStatus}',Modified='{self.Modified}',Created='{self.Created}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class UsersManagement(Base):

    __tablename__ = 'UsersManagement'

    UserName = Column(String(50), primary_key=True, unique=False, nullable=False)
    ClientId = Column(String(50), ForeignKey('Client.ClientId'), nullable=False)
    UserEmail = Column(String(50), unique=False, nullable=False)
    UserPassword = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<UsersManagement(UserName={self.UserName}, ClientId='{self.ClientId}', UserEmail='{self.UserEmail}',UserPassword='{self.UserPassword}'" \
               f",IsActive='{self.IsActive}',Modified='{self.Modified}',Created='{self.Created}',IsDeleted='{self.IsDeleted}')>"

class Subscriptions(Base):

    __tablename__ = 'Subscriptions'

    SubscriptionId = Column(String(50), primary_key=True)
    ClientId = Column(String(50), ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionPlan = Column(String(150), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<Subscriptions(SubscriptionId={self.SubscriptionId}, ClientId='{self.ClientId}', SubscriptionPlan='{self.SubscriptionPlan}',Modified='{self.Modified}',Created='{self.Created}'" \
               f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class SubscriptionPlan(Base):
    __tablename__ = 'SubscriptionPlan'

    SubscriptionId = Column(String(50), primary_key=True)
    ClientId = Column(String(50), ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionName = Column(String(150), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<SubscriptionPlan(SubscriptionId={self.SubscriptionId}, ClientId='{self.ClientId}', SubscriptionName='{self.SubscriptionName}',Modified='{self.Modified}',Created='{self.Created}'" \
               f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class Configurations(Base):

    __tablename__ = 'Configurations'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    ConfigKey = Column(String(50), unique=False, nullable=False)
    ConfigValue = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean(100), unique=False, default=True)
    IsDeleted = Column(Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<Configurations(ClientId={self.ClientId}, ConfigKey='{self.ConfigKey}', ConfigValue='{self.ConfigValue}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class JobStatus(Base):
    __tablename__ = 'JobStatus'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    StatusName = Column(String(100), unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)
    def __repr__(self):
        return f"<JobStatus(ClientId={self.ClientId}, StatusName='{self.StatusName}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class FileTypesInfo(Base):

    __tablename__ = 'FileTypesInfo'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    FileType = Column(String(50), unique=False, nullable=False)
    FilePath = Column(String(50), unique=False, nullable=False)
    FileType = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)
    def __repr__(self):
        return f"<FileTypesInfo(ClientId={self.ClientId}, FileType='{self.FileType}', FilePath='{self.FilePath}', FileDescription='{self.FileDescription}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted})>"

class ClientCallRecording(Base):

    __tablename__ = 'ClientCallRecording'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('client.Id'), nullable=False)
    CallFileName = Column(String(50), unique=False, nullable=False)
    CallFilePath = Column(String(50), unique=False, nullable=False)
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

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
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

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    LogType = Column(String(50), unique=False, nullable=False)
    LogSummary = Column(String(50), unique=False, nullable=False)
    ModulName = Column(String(50), unique=False, nullable=False)
    LogDetails = Column(String(50), unique=False, nullable=False)
    Severity = Column(String(50), unique=False, nullable=False)
    LogDate = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<Logs(ClientId={self.ClientId}, LogType='{self.LogType}',LogSummary='{self.LogSummary}',LogDetails='{self.LogDetails}',ModulName='{self.ModulName}',Severity='{self.Severity}',LogDate='{self.LogDate},Created='{self.Created}" \
               f",Modified='{self.Modified}')>"


class SentimentAnalysis(Base):
    __tablename__ = 'SentimentAnalysis'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    TranscriptId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    SentimentScore = Column(String(50), nullable=False)
    SentimentLabel  = Column(String(50), nullable=False)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow())
    SentimentStatus = Column(String(50), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<SentimentAnalysis(ClientId={self.ClientId}, TranscriptId='{self.TranscriptId}',SentimentScore='{self.SentimentScore}',SentimentLabel='{self.SentimentLabel},AnalysisDateTime='{self.AnalysisDateTime}" \
               f",SentimentStatus='{self.SentimentStatus}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class AudioTranscribe(Base):

    __tablename__ = 'AudioTranscribe'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    AudioFileName = Column(String(50), unique=False, nullable=False)
    JobStatus = Column(String(50), unique=False, nullable=False)
    FileType = Column(String(50), unique=False, nullable=False)
    TranscribeText = Column(String(50), unique=False, nullable=False)
    TranscribeFilePath = Column(String(50), unique=False, nullable=False)
    TranscribeStartTime = Column(DateTime(timezone=True), unique=False, default=True)
    TranscribeEndTime = Column(DateTime(timezone=True), unique=False, default=True)
    TranscribeDate = Column(DateTime(timezone=True), unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<AudioTranscribe(ClientId={self.ClientId}, AudioFileName='{self.AudioFileName}',JobStatus='{self.JobStatus}',FileType='{self.FileType}',TranscribeText='{self.TranscribeText},TranscribeFilePath='{self.TranscribeFilePath}" \
               f",TranscribeStartTime='{self.TranscribeStartTime}',TranscribeEndTime='{self.TranscribeEndTime}',TranscribeDate='{self.TranscribeDate}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class AudioTranscribeTracker(Base):
    __tablename__ = 'AudioTranscribeTracker'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    AudioId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    AudioFileName = Column(String(50), unique=False, nullable=False)
    ChunkSequence = Column(String(50), unique=False, nullable=False)
    ChunkText = Column(String(50), unique=False, nullable=False)
    ChunkFilePath = Column(String(50), unique=False, nullable=False)
    ChunkStatus = Column(String(50), unique=False, nullable=False)
    ChunkTranscribeStart = Column(DateTime(timezone=True), unique=False, default=True)
    ChunkTranscribeEnd = Column(DateTime(timezone=True), unique=False, default=True)
    ChunkCreatedDate = Column(DateTime(timezone=True), unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<AudioTranscribeTracker(ClientId={self.ClientId}, AudioId='{self.AudioId}',AudioFileName='{self.AudioFileName}',ChunkSequence='{self.ChunkSequence}',ChunkText='{self.ChunkText},ChunkFilePath='{self.ChunkFilePath}" \
               f",ChunkStatus='{self.ChunkStatus}',ChunkTranscribeStart='{self.ChunkTranscribeStart}',ChunkTranscribeEnd='{self.ChunkTranscribeEnd}',ChunkCreatedDate='{self.ChunkCreatedDate}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"



