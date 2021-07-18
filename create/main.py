from create.config import upload_keys


def create_app():
    upload_keys()

    from app import app
    from ManageBackApi import update_all

    update_all.restart()
    return app
