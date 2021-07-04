from app.Database import db, Column, Integer, String
import sys
from enum import Enum


class AccessLevel(Enum):
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

    def __init__(self, id, name, email, access_level):
        self.name = name
        self.id = id
        self.email = email
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
        existing_teacher.update(dict(name=name, email=email, access_level=access_level))

    db.session.commit()


# Получение уровня доступа учителя по email-у
def get_access_level(email):
    teacher = Teacher.query.filter_by(email=email).first()
    if teacher is None:
        return AccessLevel.NO_ACCESS
    else:
        return teacher.access_level
