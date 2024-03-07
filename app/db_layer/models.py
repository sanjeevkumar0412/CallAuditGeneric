from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String,DateTime,Boolean,ForeignKey
from sqlalchemy.orm import relationship
# db = SQLAlchemy()

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
    __tablename__ = 'Client'

    Id = Column(Integer, primary_key=True)
    ClientName = Column(String)
    ClientEmail = Column(String,unique=True,nullable=False)
    BillingInformation = Column(String)
    SubscriptionId = Column(String)
    # SubscriptionId = Column(Integer, ForeignKey("subscriptions.Id"))
    ModelType = Column(String)
    Created=Column(DateTime, default=datetime.utcnow())
    Modified=Column(DateTime, default=datetime.utcnow())
    PaymentStatus = Column(String)
    IsActive = Column(Boolean)
    IsDeleted = Column(Boolean)

    def __repr__(self):
        return f"<Client(Id={self.Id}, ClientName='{self.ClientName}', ClientEmail='{self.ClientEmail}',SubscriptionId='{self.SubscriptionId}',ModelType='{self.ModelType}',PaymentStatus='{self.PaymentStatus}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class BillingInformation(Base):

    __tablename__ = 'BillingInformation'

    Id = Column(Integer, primary_key=True)
    ClientId=Column(Integer, ForeignKey("client.Id"))
    SubscriptionId = Column(Integer, ForeignKey("subscriptions.Id"))
    # Subscriptions = relationship('Subscriptions', backref='clients')
    ClientName = Column(String,nullable=False)
    BillingCycle = Column(String(100), unique=False, nullable=False)
    PaymentStatus = Column(String(100), unique=False, nullable=False)
    SubscriptionStartDate=Column(DateTime,default=datetime.utcnow())
    SubscriptionEndDate=Column(DateTime,default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    # def __repr__(self):
    #     return f"<BillingInformation(billingid={self.billingid}, ClientId='{self.ClientId}', subscriptionid='{self.subscriptionid}',clientname='{self.clientname}',billingcycle='{self.billingcycle}',paymentstatus='{self.paymentstatus}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class UsersManagement(Base):

    __tablename__ = 'UsersManagement'

    Id= Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    UserName = Column(String(50), unique=False, nullable=False)
    Token = Column(String(50), unique=False, nullable=False)
    SecretKey = Column(String(50), unique=False, nullable=False)
    # password = Column(String(50), unique=False, nullable=False)
    UserEmail = Column(String(100), unique=True, nullable=False)
    UserRole = Column(String(100), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    # def __repr__(self):
    #     return f"<UsersManagement(userid={self.userid}, ClientId='{self.ClientId}', username='{self.username}',password='{self.password}',useremail='{self.useremail},userrole='{self.userrole}" \
    #            f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class Subscriptions(Base):

    __tablename__ = 'Subscriptions'

    Id = Column(Integer, primary_key=True)
    SubscriptionPlan = Column(String(50), unique=False, nullable=False)
    SubscriptionDescription = Column(String(150), unique=False, nullable=False)
    # UsercountSubscription = Column(String(100), unique=False, nullable=False)
    # UsercountSubscriptionActivated = Column(String(100), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    # def __repr__(self):
    #     return f"<Subscriptions(subscriptionid={self.subscriptionid}, subscriptionplan='{self.subscriptionplan}', usercountsubscription='{self.usercountsubscription}',usercountsubscriptionactivated='{self.usercountsubscriptionactivated}',description='{self.description}'" \
    #            f",IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class Configuration(Base):

    __tablename__ = 'Configuration'

    Id= Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    ClientName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    Key = Column(String(50), unique=False, nullable=False)
    Value = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean(100), unique=False, default=True)
    IsDeleted = Column(Boolean(100), unique=False, default=True)

    # def __repr__(self):
    #     return f"<Configuration(configid={self.configid}, ClientId='{self.ClientId}', key='{self.key}',value='{self.value}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class JobStatus(Base):
    __tablename__ = 'JobStatus'

    Id= Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    StatusName = Column(String(100), unique=False, default=True)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    # def __repr__(self):
    #     return f"<JobStatus(statusid={self.statusid}, statusname='{self.statusname}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

class SubscriptionPlan(Base):
    __tablename__ = 'SubscriptionPlan'

    Id= Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    Name = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)


class FileInfo(Base):

    __tablename__ = 'FileInfo'

    Id= Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    FileFormat = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)
    def __repr__(self):
        return f"<FileInfo(ClientId={self.ClientId}, FileFormat='{self.FileFormat}',Created='{self.Created}',Modified='{self.Modified}')>"

class ClientCallRecording(Base):

    __tablename__ = 'ClientCallRecording'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.Id'), nullable=False)
    UserName = Column(Integer, ForeignKey('UsersManagement.Id'), nullable=False)
    FileTypeId = Column(Integer, ForeignKey('FileInfo.Id'), nullable=False)
    FileName = Column(String(50), unique=False, nullable=False)
    FilePath = Column(String(50), unique=False, nullable=False)
    StatusId = Column(Integer, ForeignKey('UsersManagement.Id'), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    # filesize = Column(Float, unique=False, nullable=False)
    # iscompleted = Column(Boolean(100), unique=False, default=True)
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<ClientCallRecording(ClientId={self.ClientId}, UserName='{self.UserName}',FileTypeId='{self.FileTypeId}',FileName='{self.FileName}',FilePath='{self.FilePath}',StatusId='{self.StatusId}',Created='{self.Created}" \
               f",Modified='{self.Modified}')>"


class ClientCallSummary(Base):
    __tablename__ = 'ClientCallSummary'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    UserName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    SummaryDescription = Column(String(50), unique=False, nullable=False)
    SummaryDateTime = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<ClientCallSummary(ClientId={self.ClientId}, UserName='{self.UserName}',SummaryDescription='{self.SummaryDescription}',SummaryDateTime='{self.SummaryDateTime}', Created='{self.Created}" \
               f",Modified='{self.Modified}')>"


class ErrorLogs(Base):
    __tablename__ = 'ErrorLogs'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    UserName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    ErrorType = Column(String(50), unique=False, nullable=False)
    ErrorDetails = Column(DateTime, default=datetime.utcnow())
    ErrorDate = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<ErrorLogs(ClientId={self.ClientId}, UserName='{self.UserName}',ErrorType='{self.ErrorType}',ErrorDetails='{self.ErrorDetails}',ErrorDate='{self.ErrorDate},Created='{self.Created}" \
               f",Modified='{self.Modified}')>"


class SentimentAnalysis(Base):
    __tablename__ = 'SentimentAnalysis'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    UserName = Column(Integer, ForeignKey('client.UserName'), nullable=False)
    TranscriptId = Column(Integer, ForeignKey('AudioTranscribe.Id'), nullable=False)
    SentimentScore = Column(Integer, nullable=False)
    SentimentLabel  = Column(String(50), nullable=False)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow())
    SentimentStatus = Column(String(50), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<SentimentAnalysis(ClientId={self.ClientId}, UserName='{self.UserName}',TranscriptId='{self.TranscriptId}',SentimentScore='{self.SentimentScore}',SentimentLabel='{self.SentimentLabel},AnalysisDateTime='{self.AnalysisDateTime}" \
               f",SentimentStatus='{self.SentimentStatus}',Created='{self.Created}',Modified='{self.Modified}')>"


class AudioTranscribe(Base):

    __tablename__ = 'AudioTranscribe'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('Client.ClientId'), nullable=False)
    # UserName = Column(Integer, ForeignKey('Client.UserName'), nullable=False)
    FileId = Column(Integer, ForeignKey('FileInfo.Id'), nullable=False)
    FileName = Column(String(50), unique=False, nullable=False)
    # FileStatus = Column(Integer, ForeignKey('FileInfo.userid'), nullable=False)
    TranscribeText = Column(String(50), unique=False, nullable=False)
    TranscribeFilePath = Column(String(50), unique=False, nullable=False)
    TranscribeDate = Column(DateTime(timezone=True), unique=False, default=True)
    Status = Column(Integer, ForeignKey('FileInfo.userid'), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    def __repr__(self):
        return f"<AudioTranscribe(ClientId={self.ClientId}, FileId='{self.FileId}',FileName='{self.FileName}',TranscribeText='{self.TranscribeText}',TranscribeFilePath='{self.TranscribeFilePath},TranscribeDate='{self.TranscribeDate}" \
               f",Status='{self.Status}',Created='{self.Created}',Modified='{self.Modified}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class TranscribeJob(Base):

    __tablename__ = 'TranscribeJob'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('Client.Id'), nullable=False)
    UserName = Column(Integer, ForeignKey('Client.Name'), nullable=False)
    JobTypeId = Column(Integer, ForeignKey('Client.Id'), nullable=False)
    StatusId = Column(Integer, ForeignKey('Jobstatus.Id'), nullable=False)
    JobStarttime = Column(DateTime, default=datetime.utcnow())
    JobEndTime = Column(DateTime, default=datetime.utcnow())
    IsError  = Column(Boolean)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive  = Column(Boolean)
    IsDeleted  = Column(Boolean)


# with app.app_context():
#     # Create database tables
#     create_all()
