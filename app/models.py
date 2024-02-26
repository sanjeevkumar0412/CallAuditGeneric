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
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<User(clientid={self.clientid}, clientname='{self.clientname}', clientemail='{self.clientemail}',billinginformation='{self.billinginformation}',subscription_id='{self.subscription_id}',modeltype='{self.modeltype}',paymentstatus='{self.paymentstatus}',is_active='{self.is_active}',is_deleted='{self.is_deleted}')>"

class BillingInformation(db.Model):
    billingid = db.Column(db.Integer, primary_key=True)
    # clientid = db.Column(db.Integer, db.ForeignKey('clients.clientid'), nullable=False)
    subscriptionid = db.Column(db.Integer, db.ForeignKey('subscriptions.subscriptionid'))
    subscriptions = db.relationship('Subscriptions', backref='clients')
    clientname = db.Column(db.String(50), unique=False, nullable=False)
    billingcycle = db.Column(db.String(100), unique=False, nullable=False)
    paymentstatus = db.Column(db.String(100), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<BillingInformation(billingid={self.billingid}, clientid='{self.clientid}', subscriptionid='{self.subscriptionid}',clientname='{self.clientname}',billingcycle='{self.billingcycle}',paymentstatus='{self.paymentstatus}',is_active='{self.is_active}',is_deleted='{self.is_deleted}')>"


class Subscriptions(db.Model):
    subscriptionid = db.Column(db.Integer, primary_key=True)
    subscriptionplan = db.Column(db.String(50), unique=False, nullable=False)
    usercountsubscription = db.Column(db.String(100), unique=False, nullable=False)
    usercountsubscriptionactivated = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<Subscriptions(subscriptionid={self.subscriptionid}, subscriptionplan='{self.subscriptionplan}', usercountsubscription='{self.usercountsubscription}',usercountsubscriptionactivated='{self.usercountsubscriptionactivated}',description='{self.description}'" \
               f",is_active='{self.is_active}',is_deleted='{self.is_deleted}')>"


class UsersManagement(db.Model):
    userid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    username = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(50), unique=False, nullable=False)
    useremail = db.Column(db.String(100), unique=True, nullable=False)
    userrole = db.Column(db.String(100), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<UsersManagement(userid={self.userid}, clientid='{self.clientid}', username='{self.username}',password='{self.password}',useremail='{self.useremail},userrole='{self.userrole}" \
               f",is_active='{self.is_active}',is_deleted='{self.is_deleted}')>"


class Configuration(db.Model):
    configid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    key = db.Column(db.String(50), unique=False, nullable=False)
    value = db.Column(db.String(50), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<Configuration(configid={self.configid}, clientid='{self.clientid}', key='{self.key}',value='{self.value}',is_active='{self.is_active},is_deleted='{self.is_deleted}" \

class JobStatus(db.Model):
    statusid= db.Column(db.Integer, primary_key=True)
    statusname = db.Column(db.String(100), unique=False, default=True)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<JobStatus(statusid={self.statusid}, statusname='{self.statusname}',is_active='{self.is_active},is_deleted='{self.is_deleted}" \

class FileTypesInfo(db.Model):
    typeid= db.Column(db.Integer, primary_key=True)
    clientid = db.Column(db.Integer, db.ForeignKey('client.clientid'), nullable=False)
    fileformat = db.Column(db.String(50), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(100), unique=False, default=True)
    is_deleted = db.Column(db.Boolean(100), unique=False, default=True)

    def __repr__(self):
        return f"<FileTypesInfo(typeid={self.typeid}, clientid='{self.clientid}', fileformat='{self.fileformat}',is_active='{self.is_active},is_deleted='{self.is_deleted}" \


# with app.app_context():
#     # Create database tables
#     db.create_all()
