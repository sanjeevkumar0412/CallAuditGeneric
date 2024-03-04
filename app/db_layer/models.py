from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String,DateTime,Boolean,ForeignKey
from sqlalchemy.orm import relationship
# db = SQLAlchemy()

Base = declarative_base()

class Client(Base):

    __tablename__ = 'Client'

    Id = Column(Integer, primary_key=True)
    ClientName = Column(String)
    Email = Column(String,unique=True,nullable=False)
    BillingInformation = Column(String)
    SubscriptionId = Column(Integer, ForeignKey("subscriptions.Id"))
    # client = relationship("subscriptions", back_populates="client")
    # subscriptions = relationship('Subscriptions', backref='clients')
    ModelType = Column(String)
    Created=Column(DateTime, default=datetime.utcnow())
    Modified=Column(DateTime, default=datetime.utcnow())
    PaymentStatus = Column(String)
    IsActive = Column(Boolean)
    IsDeleted = Column(Boolean)

    # def __repr__(self):
    #     return f"<User(ClientId={self.Id}, clientname='{self.clientname}', clientemail='{self.clientemail}',billinginformation='{self.billinginformation}',subscriptionid='{self.subscriptionid}',modeltype='{self.modeltype}',paymentstatus='{self.paymentstatus}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

class BillingInformation(Base):

    __tablename__ = 'BillingInformation'

    Id = Column(Integer, primary_key=True)
    ClientId=Column(Integer, ForeignKey("client.Id"))
    subscriptionId = Column(Integer, ForeignKey("subscriptions.Id"))
    # Subscriptions = relationship('Subscriptions', backref='clients')
    ClientName = Column(String,nullable=False)
    BillingCycle = Column(String(100), unique=False, nullable=False)
    paymentstatus = Column(String(100), unique=False, nullable=False)
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
    username = Column(String(50), unique=False, nullable=False)
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
    key = Column(String(50), unique=False, nullable=False)
    value = Column(String(50), unique=False, nullable=False)
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
    statusname = Column(String(100), unique=False, default=True)
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
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    fileformat = Column(String(50), unique=False, nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)

    # def __repr__(self):
    #     return f"<FileTypesInfo(typeid={self.typeid}, ClientId='{self.ClientId}', fileformat='{self.fileformat}',IsActive='{self.IsActive},IsDeleted='{self.IsDeleted}" \

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

    # def __repr__(self):
    #     return f"<AudioRecord(userid={self.userid}, ClientId='{self.ClientId}',username='{self.username}',filetype='{self.filetype}',filename='{self.filename},startdate='{self.startdate}" \
    #            f",enddate='{self.enddate}',status='{self.status}',filesize='{self.filesize}',iscompleted='{self.iscompleted}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"


class ClientCallSummary(Base):
    __tablename__ = 'ClientCallSummary'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    ClientName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    SummaryDescription = Column(String(50), unique=False, nullable=False)
    SummaryDateTime = Column(DateTime, default=datetime.utcnow())
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())
    IsActive = Column(Boolean, unique=False, default=True)
    IsDeleted = Column(Boolean, unique=False, default=True)


class ErrorLogs(Base):
    __tablename__ = 'ErrorLogs'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    ClientName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    ErrorType = Column(String(50), unique=False, nullable=False)
    ErrorDetails = Column(DateTime, default=datetime.utcnow())
    ErrorDate = Column(DateTime, default=datetime.utcnow())



class SentimentAnalysis(Base):
    __tablename__ = 'SentimentAnalysis'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('client.ClientId'), nullable=False)
    ClientName = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    TranscriptId = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    SentimentScore = Column(String(50), unique=False, nullable=False)
    # SentimentLabelId = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    # SentimentStatus  = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    # SentimentClientId  = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    # SentimentClientName  = Column(Integer, ForeignKey('client.ClientName'), nullable=False)
    AnalysisDateTime = Column(DateTime, default=datetime.utcnow())



class AudioTranscribe(Base):

    __tablename__ = 'AudioTranscribe'

    Id = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('Client.Id'), nullable=False)
    # UserName = Column(Integer, ForeignKey('Client.Id'), nullable=False)
    FileId = Column(Integer, ForeignKey('FileInfo.Id'), nullable=False)
    FileName = Column(String(50), unique=False, nullable=False)
    FileStatus = Column(Integer, ForeignKey('FileInfo.userid'), nullable=False)
    SentimentScore = Column(String(50), unique=False, nullable=False)
    SentimentLabelId = Column(Integer, ForeignKey('FileInfo.userid'), nullable=False)
    TranscriptText = Column(String(50), unique=False, nullable=False)
    TranscriptionFilePath = Column(String(50), unique=False, nullable=False)
    TranscriptionDate = Column(DateTime(timezone=True), unique=False, default=True)
    StatusId = Column(Integer, ForeignKey('FileInfo.userid'), nullable=False)
    Created = Column(DateTime, default=datetime.utcnow())
    Modified = Column(DateTime, default=datetime.utcnow())

    # def __repr__(self):
    #     return f"<TranscribeTracker(fileid={self.fileid}, audioid='{self.audioid}',username='{self.username}',filetype='{self.filetype}',filename='{self.filename},startdate='{self.startdate}" \
    #            f",enddate='{self.enddate}',status='{self.status}',sequencenumber='{self.sequencenumber}',filesize='{self.filesize}',iscompleted='{self.iscompleted}',IsActive='{self.IsActive}',IsDeleted='{self.IsDeleted}')>"

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
