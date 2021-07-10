from app import app
from ManageBackApi.update_all import update_all
from ManageBackApi.DB_subjects_STS import update_subjects_tasks_marks


if __name__ == '__main__':
    app.run(port=5000)
