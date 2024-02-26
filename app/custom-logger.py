from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../Cogent-AI.db'
db = SQLAlchemy(app)

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
