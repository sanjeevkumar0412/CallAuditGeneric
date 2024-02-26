from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Index, Date, DateTime, Numeric, BigInteger, String, ForeignKey, Boolean)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../Cogent-AI.db'
db = SQLAlchemy(app)

with app.app_context():
    Base = automap_base()
    Base.prepare(db.engine, reflect=True)


class TableBase(Base):
    """sqlalchemy ORM for my table."""
    __abstract__ = True # when its true not to create model in sqlalchemy
    # __tablename__ = "table1"
    # id = Column("id", BigInteger, primary_key=True, autoincrement=True)
    # date = Column("date", Date, nullable=False)
    # value = Column("value", Numeric(20, 8))