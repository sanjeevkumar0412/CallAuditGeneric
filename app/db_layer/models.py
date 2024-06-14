from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,inspect,Float


Base = declarative_base()

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'Users'

    Id = Column(Integer, primary_key=True, autoincrement=False)
    Name = Column(String)
    Email = Column(String)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class Subscriptions(Base):
    __tablename__ = 'Subscriptions'

    SubscriptionId = Column(String, primary_key=True)
    ClientId = Column(String, ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionPlan = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class SubscriptionPlan(Base):
    __tablename__ = 'SubscriptionPlan'

    SubscriptionId = Column(String, primary_key=True)
    ClientId = Column(String, ForeignKey('Client.ClientId'), nullable=False)
    SubscriptionName = Column(String, unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class JobStatus(Base):
    __tablename__ = 'JobStatus'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    # ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    StatusName = Column(String, unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

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

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class SentimentAnalysis(Base):
    __tablename__ = 'SentimentAnalysis'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    SentimentScore = Column(Float, nullable=False)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow(), nullable=True)
    SentimentStatus = Column(String, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)
    Sentiment = Column(String, nullable=True)
    AudioFileName = Column(String, nullable=True)
    Summary = Column(String, nullable=False)
    Topics = Column(String, nullable=False)
    FoulLanguage = Column(String, nullable=False)
    ActionItems = Column(String, nullable=False)
    Owners = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    Reminder = Column(String, nullable=False)

    def __repr__(self):
        return f"<SentimentAnalysis(ClientId={self.ClientId},SentimentScore='{self.SentimentScore},AnalysisDateTime='{self.AnalysisDateTime}" \
               f",SentimentStatus='{self.SentimentStatus}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}'),Sentiment='{self.Sentiment}',AudioFileName='{self.AudioFileName}',Summary='{self.Summary}',Topics='{self.Topics}',FoulLanguage='{self.FoulLanguage},ActionItems='{self.ActionItems}',Owners='{self.Owners}',prompt='{self.prompt}',Reminder='{self.Reminder}')>"

class AudioTranscribe(Base):
    __tablename__ = 'AudioTranscribe'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey(Client.ClientId), nullable=False)
    JobStatus = Column(String, ForeignKey(JobStatus.Id), nullable=False)
    FileType = Column(String, ForeignKey(FileTypesInfo.Id), nullable=False)
    AudioFileName = Column(String, nullable=False)
    TranscribeFilePath = Column(String, nullable=False)
    TranscribeStartTime = Column(DateTime, nullable=True)
    TranscribeEndTime = Column(DateTime, nullable=True)
    TranscribeDate = Column(DateTime, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, default=True, nullable=True)
    IsDeleted = Column(Boolean, default=False, nullable=True)
    CaseID = Column(String, nullable=False)
    DateofDiscussion = Column(String, nullable=False)
    FileSize = Column(String, nullable=False)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class AudioTranscribeTracker(Base):
    __tablename__ = 'AudioTranscribeTracker'

    Id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    AudioId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    ChunkStatus = Column(String, ForeignKey(JobStatus.Id), nullable=False)
    ChunkFileType = Column(String, ForeignKey(FileTypesInfo.Id), nullable=False)
    ChunkFileName = Column(String, unique=False, nullable=True)
    ChunkSequence = Column(String, unique=False, nullable=True)
    ChunkText = Column(String, unique=False, nullable=True)
    ChunkFilePath = Column(String, unique=False, nullable=True)
    ChunkTranscribeStart = Column(DateTime, unique=False, nullable=True)
    ChunkTranscribeEnd = Column(DateTime, unique=False, nullable=True)
    ChunkCreatedDate = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class ClientMaster(Base):
    __tablename__ = 'ClientMaster'

    Id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    ClientName = Column(String, unique=True, nullable=False)
    ClientUser = Column(String, unique=True, nullable=False)
    ServerName = Column(String, unique=True, nullable=False)
    DatabaseName = Column(String, unique=True, nullable=False)
    ConnectionString = Column(String, unique=True, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=False)
    IsActive = Column(Boolean, unique=False, default=True, nullable=False)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=False)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class DatabaseMaster(Base):
    __tablename__ = 'DatabaseMaster'

    Id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    DatabaseName = Column(String, unique=True, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class MasterConnectionString(Base):
    __tablename__ = 'MasterConnectionString'

    Id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    DatabaseType = Column(Integer, ForeignKey('DatabaseMaster.Id'), nullable=False)
    ConnectionName = Column(String, unique=True, nullable=True)
    ConnectionString = Column(String, unique=True, nullable=True)
    ConnectionType  = Column(String, unique=True, nullable=True)
    Host = Column(String, unique=True, nullable=True)
    Port = Column(String, unique=True, nullable=True)
    Username = Column(String, unique=True, nullable=True)
    Password = Column(String, unique=True, nullable=True)
    DatabaseName = Column(String, unique=True, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class MasterTable(Base):
    __tablename__ = 'MasterTable'

    Id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, nullable=False)
    DatabaseType = Column(Integer, nullable=False)
    ConnectionName = Column(String, unique=True, nullable=True)
    ConnectionString = Column(String, unique=True, nullable=True)
    ConnectionType = Column(String, unique=True, nullable=True)
    Host = Column(String, unique=True, nullable=True)
    Port = Column(String, unique=True, nullable=True)
    Username = Column(String, unique=True, nullable=True)
    Password = Column(String, unique=True, nullable=True)
    DatabaseName = Column(String, unique=True, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
class AudioFileNamePattern(Base):
    __tablename__ = 'AudioFileNamePattern'

    Id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    PatternName = Column(String, ForeignKey('MasterAudioFileName.PatternName'), nullable=False)
    Sequence = Column(Integer, unique=True, nullable=True)
    Separator = Column(String, unique=True, nullable=True)
    IsRequired = Column(Boolean, default=False, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True, nullable=True)
    IsDeleted = Column(Boolean, unique=False, default=False, nullable=True)

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

class ProhibitedKeyword(Base):
    __tablename__ = 'ProhibitedKeyword'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientID = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    Keywords = Column(String, nullable=False)

    def __repr__(self):
        return f"<ProhibitedKeyword(ClientID={self.ClientID},Keywords='{self.Keywords}')>"



class ScoreCardAnalysis(Base):
    __tablename__ = 'ScoreCardAnalysis'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    ScoreCardStatus = Column(Integer, nullable=False)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow(), nullable=True)
    ScoreCard = Column(String, nullable=True)
    Created = Column(DateTime, default=datetime.utcnow(), nullable=True)
    Modified = Column(DateTime, default=datetime.utcnow(), nullable=True)
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=False)
    AudioFileName = Column(String, nullable=True)
    OverallScore = Column(String, nullable=False)
    prompt = Column(String, nullable=False)


    def __repr__(self):
        return f"<ScoreCardAnalysis(ClientId={self.ClientId},ScoreCardStatus='{self.ScoreCardStatus}',AnalysisDateTime='{self.AnalysisDateTime}" \
               f",ScoreCard='{self.ScoreCard},Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}'),AudioFileName='{self.AudioFileName}',prompt='{self.prompt}')>"


class ComplianceScore(Base):
    __tablename__ = 'ComplianceScore'

    Id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    ClientID = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    Compliance = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<ComplianceScore(ClientID={self.ClientID},Compliance='{self.Compliance}')>"

