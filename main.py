from app import Database
from app.Database import Inspection
from app import app
from tests import test_database

if __name__ == "__main__":
    Database.Teachers.add_teacher(8, 'nikita', 'andrusov.n@gmail.com', 3)
    app.run(port=5000)



