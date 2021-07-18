from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, event
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relation
from sqlalchemy.ext.declarative import declarative_base
from create.config import Metadata
from app import app
from flask_sqlalchemy import SQLAlchemy


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@localhost/ManageBac'.format(Metadata.DATABASE_USER,
                                                                                   Metadata.DATABASE_PASSWORD)

db = SQLAlchemy(app)

from app.Database.Students import Student
from app.Database.Marks import Mark
from app.Database.Tasks import Task
from app.Database.Subjects import Subject, SubjectToStudentMapping
from app.Database.Teachers import Teacher
from app.Database.JWRefreshTokens import JWRefreshToken

db.create_all()
db.session.commit()
print(db.metadata.tables.keys())

print('database initialized')

