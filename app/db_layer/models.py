from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../Cogent-AI.db'
db = SQLAlchemy(app)

# db.session.entry(param)
# db.session.commit()
# Define your models

class Client(db.Model):
    clientid = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(50), unique=False, nullable=False)
    clientemail = db.Column(db.String(100), unique=True, nullable=False)
    billinginformation = db.Column(db.String(100), unique=False, nullable=False)
    subscriptionid = db.Column(db.Integer, db.ForeignKey('subscriptions.subscriptionid'))
    # subscriptions = db.relationship('Subscriptions', backref='clients')
    modeltype = db.Column(db.String(100), unique=False, nullable=False)
    paymentstatus = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<User(clientid={self.clientid}, clientname='{self.clientname}', clientemail='{self.clientemail}',billinginformation='{self.billinginformation}',subscriptionid='{self.subscriptionid}',modeltype='{self.modeltype}',paymentstatus='{self.paymentstatus}',isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"

class BillingInformation(db.Model):
    billingid = db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    subscriptionid = db.Column(db.Integer, db.ForeignKey('subscriptions.subscriptionid'))
    subscriptions = db.relationship('Subscriptions', backref='clients')
    clientname = db.Column(db.String(50), unique=False, nullable=False)
    billingcycle = db.Column(db.String(100), unique=False, nullable=False)
    paymentstatus = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<BillingInformation(billingid={self.billingid}, clientid='{self.clientid}', subscriptionid='{self.subscriptionid}',clientname='{self.clientname}',billingcycle='{self.billingcycle}',paymentstatus='{self.paymentstatus}',isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"


class Subscriptions(db.Model):
    subscriptionid = db.Column(db.Integer, primary_key=True)
    subscriptionplan = db.Column(db.String(50), unique=False, nullable=False)
    usercountsubscription = db.Column(db.String(100), unique=False, nullable=False)
    usercountsubscriptionactivated = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<Subscriptions(subscriptionid={self.subscriptionid}, subscriptionplan='{self.subscriptionplan}', usercountsubscription='{self.usercountsubscription}',usercountsubscriptionactivated='{self.usercountsubscriptionactivated}',description='{self.description}'" \
               f",isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"


class UsersManagement(db.Model):
    __tablename__ = 'UsersManagement'
    userid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    useremail = db.Column(db.String(100), unique=True, nullable=False)
    userrole = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<UsersManagement(userid={self.userid}, clientid='{self.clientid}', username='{self.username}',password='{self.password}',useremail='{self.useremail},userrole='{self.userrole}" \
               f",isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"


class Configuration(db.Model):
    configid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    key = db.Column(db.String(50), unique=False, nullable=False)
    value = db.Column(db.String(50), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<Configuration(configid={self.configid}, clientid='{self.clientid}', key='{self.key}',value='{self.value}',isactive='{self.isactive},isdeleted='{self.isdeleted}" \

class JobStatus(db.Model):
    statusid= db.Column(db.Integer, primary_key=True)
    statusname = db.Column(db.String(100), unique=False, default=True)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<JobStatus(statusid={self.statusid}, statusname='{self.statusname}',isactive='{self.isactive},isdeleted='{self.isdeleted}" \

class FileTypesInfo(db.Model):
    typeid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    fileformat = db.Column(db.String(50), unique=False, nullable=False)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<FileTypesInfo(typeid={self.typeid}, clientid='{self.clientid}', fileformat='{self.fileformat}',isactive='{self.isactive},isdeleted='{self.isdeleted}" \

class AudioRecord(db.Model):
    __tablename__ = 'AudioRecord'
    audioid = db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('UsersManagement.userid'), nullable=False)
    filetype = db.Column(db.String(50), unique=False, nullable=False)
    filename = db.Column(db.String(50), unique=False, nullable=False)
    startdate = db.Column(db.DateTime(timezone=True), unique=False, default=True)
    enddate = db.Column(db.DateTime(timezone=True), unique=False, default=True)
    status = db.Column(db.String(50), unique=False, nullable=False)
    filesize = db.Column(db.Float, unique=False, nullable=False)
    iscompleted = db.Column(db.Boolean(100), unique=False, default=True)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<AudioRecord(userid={self.userid}, clientid='{self.clientid}',username='{self.username}',filetype='{self.filetype}',filename='{self.filename},startdate='{self.startdate}" \
               f",enddate='{self.enddate}',status='{self.status}',filesize='{self.filesize}',iscompleted='{self.iscompleted}',isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"

class TranscribeTracker(db.Model):

    __tablename__ = 'TranscribeTracker'

    fileid = db.Column(db.Integer, primary_key=True)
    audioid = db.Column(db.Integer, db.ForeignKey('AudioRecord.audioid'), nullable=False)
    username = db.Column(db.Integer, db.ForeignKey('UsersManagement.userid'), nullable=False)
    filetype = db.Column(db.String(50), unique=False, nullable=False)
    filename = db.Column(db.String(50), unique=False, nullable=False)
    startdate = db.Column(db.DateTime(timezone=True), unique=False, default=True)
    enddate = db.Column(db.DateTime(timezone=True), unique=False, default=True)
    status = db.Column(db.String(50), unique=False, nullable=False)
    sequencenumber = db.Column(db.String(50), unique=False, nullable=False)
    filesize = db.Column(db.Float, unique=False, nullable=False)
    iscompleted = db.Column(db.Boolean(100), unique=False, default=True)
    isactive = db.Column(db.Boolean(100), unique=False, default=True)
    isdeleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<TranscribeTracker(fileid={self.fileid}, audioid='{self.audioid}',username='{self.username}',filetype='{self.filetype}',filename='{self.filename},startdate='{self.startdate}" \
               f",enddate='{self.enddate}',status='{self.status}',sequencenumber='{self.sequencenumber}',filesize='{self.filesize}',iscompleted='{self.iscompleted}',isactive='{self.isactive}',isdeleted='{self.isdeleted}')>"


with app.app_context():
    # Create database tables
    db.create_all()
