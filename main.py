from app import app
from ManageBackApi import update_all
import config


if __name__ == '__main__':
    config.upload_keys()
    update_all.restart()
    app.run(port=5000, host='0.0.0.0')
