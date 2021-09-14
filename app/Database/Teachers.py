from app.Database import db, Column, Integer, String, Boolean
import sys
from enum import Enum


class AccessLevel:
    NO_ACCESS = 0
    CASUAL_ACCESS = 1
    ADMIN = 2
    GOD = 3


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = Column('id', Integer, primary_key=True, unique=True)
    name = Column('name', String(60))
    email = Column('email', String(60), unique=True)
    access_level = Column('access_level', Integer)
    is_updated = Column('is_updated', Boolean)

    def __init__(self, id, name, email, access_level):
        self.name = name
        self.id = id
        self.email = email
        self.is_updated = True
        if isinstance(access_level, int):
            if 0 <= access_level <= 3:
                self.access_level = access_level
            else:
                sys.exit('incorrect access level! should be between 0 and 2')

        else:
            sys.exit('incorrect access level! should be integer value, but '
                     + str(access_level) + ' of type ' + str(type(access_level)) + ' is given')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'access_level': self.access_level
        }


def update_teachers_rights(email, access_level):
    existing_teacher = Teacher.query.filter_by(email=email)
    if existing_teacher.first() is not None:
        existing_teacher.update(dict(access_level=access_level, is_updated=True))
        db.session.commit()


# Функция, добавляющая учителя в список авторитетных лиц
# id - managebac id учителя
# name - имя, email - адрес
# access_level - уровень доступа 0, 1, 2, 3 (см. выше в файле)
def add_teacher(id, name, email, access_level):
    existing_teacher = Teacher.query.filter_by(id=id)

    # Если создаем учителя с нуля
    if existing_teacher.first() is None:
        new_teacher = Teacher(id, name, email, access_level)
        db.session.add(new_teacher)
    else:
        # Иначе обновляем значение записи
        existing_teacher.update(dict(name=name, email=email, is_updated=True))

    db.session.commit()


# Получение уровня доступа учителя по email-у
def get_access_level(email):
    teacher = Teacher.query.filter_by(email=email).first()
    if teacher is None:
        return AccessLevel.NO_ACCESS
    else:
        return teacher.access_level


def get_all_teachers():
    all_teachers = Teacher.query.all()
    return [item.to_json() for item in all_teachers]


def get_teacher(email):
    teacher = Teacher.query.filter_by(email=email).first()
    if teacher is None:
        return ""
    else:
        return teacher.name
