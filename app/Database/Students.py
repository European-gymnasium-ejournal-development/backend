from app.Database import db, Column, Integer, String


class Student(db.Model):
    __tablename__ = 'students'
    id = Column('id', Integer, primary_key=True, unique=True)
    name = Column('name', String(60))
    grade_name = Column('grade_name', String(60))

    def __init__(self, id, name, grade_name):
        self.id = id
        self.name = name
        self.grade_name = grade_name

    def to_json(self):
        return {
            'name': self.name,
            'id': self.id,
            'grade_name': self.grade_name
        }


# Добавляет ученика с данным id, name (имя), grade (название класса)
# Если такой ученик уже был (ученик с таким id), то обнавляет значения name и grade
# Контракт: все данные хорошие, проверять их не надо
def add_student(id, name, grade):
    existing_user = Student.query.filter_by(id=id)

    # если создаем ученика с нуля
    if existing_user.first() is None:
        new_user = Student(id, name, grade)
        db.session.add(new_user)
    else:
        # иначе обновляем информацию
        existing_user.update(dict(name=name, grade_name=grade))

    db.session.commit()
