import config
config.upload_keys()

from app import app
from ManageBackApi import update_all


if __name__ == '__main__':
    update_all.restart()
    app.run(port=5000, host='0.0.0.0')
